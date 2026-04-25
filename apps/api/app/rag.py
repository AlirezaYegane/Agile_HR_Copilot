from pathlib import Path
import os
import re

import google.generativeai as genai
from dotenv import load_dotenv
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class PolicyRAG:
    """
    Lightweight local policy retriever.

    Why this exists:
    - Chroma + Google embedding model was crashing on startup because the selected
      embedding model is not available for the installed google-generativeai API version.
    - This version keeps the project moving: it indexes the HR policy PDFs locally with
      TF-IDF, retrieves relevant chunks, and still uses Gemini for grounded answer writing.
    """

    def __init__(self, root: Path):
        self.root = root
        load_dotenv(root / ".env")

        self.policy_dir = Path(os.getenv("POLICY_DOCS_DIR", str(root / "data/policies")))
        if not self.policy_dir.is_absolute():
            self.policy_dir = root / self.policy_dir

        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        self.docs: list[str] = []
        self.metas: list[dict] = []
        self.vectorizer = None
        self.matrix = None
        self.model = None

        if self.api_key and self.api_key != "YOUR_REAL_GEMINI_API_KEY_HERE" and self.api_key != "YOUR_GEMINI_API_KEY_HERE":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)

        self._index()

    def is_ready(self) -> bool:
        return len(self.docs) > 0 and self.matrix is not None

    def count(self) -> int:
        return len(self.docs)

    def _clean(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def _chunk(self, text: str, size: int = 900, overlap: int = 150) -> list[str]:
        text = self._clean(text)
        chunks = []
        start = 0

        while start < len(text):
            chunk = text[start : start + size].strip()
            if chunk:
                chunks.append(chunk)
            start += size - overlap

        return chunks

    def _index(self) -> None:
        pdfs = sorted(self.policy_dir.glob("*.pdf"))

        for pdf in pdfs:
            reader = PdfReader(str(pdf))
            full_text = "\n".join(page.extract_text() or "" for page in reader.pages)

            for i, chunk in enumerate(self._chunk(full_text)):
                self.docs.append(chunk)
                self.metas.append({"source": pdf.name, "chunk": i})

        if self.docs:
            self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            self.matrix = self.vectorizer.fit_transform(self.docs)

    def _retrieve(self, question: str, k: int = 4) -> list[tuple[str, dict, float]]:
        if not self.is_ready():
            return []

        q_vec = self.vectorizer.transform([question])
        sims = cosine_similarity(q_vec, self.matrix).ravel()
        top_idx = sims.argsort()[::-1][:k]

        return [(self.docs[i], self.metas[i], float(sims[i])) for i in top_idx]

    def ask(self, question: str, k: int = 4) -> dict:
        hits = self._retrieve(question, k=k)

        if not hits:
            return {
                "answer": "I can't answer that from the current policy corpus.",
                "sources": [],
            }

        context_block = "\n\n---\n\n".join(
            f"[Source: {meta['source']} — chunk {meta['chunk']}]\n{doc}"
            for doc, meta, _score in hits
        )

        # If Gemini key is missing/invalid, still return a useful grounded retrieval result.
        if self.model is None:
            top_doc, top_meta, _ = hits[0]
            return {
                "answer": (
                    "I found relevant policy context, but Gemini is not configured yet. "
                    f"The strongest match is from [{top_meta['source']}], chunk {top_meta['chunk']}: "
                    f"{top_doc[:500]}..."
                ),
                "sources": [
                    {
                        "source": meta["source"],
                        "chunk": meta["chunk"],
                        "score": score,
                        "preview": doc[:250] + "...",
                    }
                    for doc, meta, score in hits
                ],
            }

        prompt = f"""You are an HR analytics assistant for a consulting team.

Answer the user's question using ONLY the policy context below.
If the answer is not in the context, say:
"I can't answer that from the current policy corpus."

Always cite the specific source filename when making a claim.
Keep the answer to 3-5 sentences in plain English.

CONTEXT:
{context_block}

QUESTION:
{question}

ANSWER:
"""

        try:
            response = self.model.generate_content(prompt)
            answer = response.text
        except Exception as e:
            top_doc, top_meta, _ = hits[0]
            answer = (
                "I found relevant policy context, but the configured Gemini model was unavailable. "
                f"Strongest source: [{top_meta['source']}], chunk {top_meta['chunk']}. "
                f"Relevant excerpt: {top_doc[:500]}..."
            )

        return {
            "answer": answer,
            "sources": [
                {
                    "source": meta["source"],
                    "chunk": meta["chunk"],
                    "score": score,
                    "preview": doc[:250] + "...",
                }
                for doc, meta, score in hits
            ],
        }

