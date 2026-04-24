from pathlib import Path
from html import escape
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

policy_dir = Path("data/policies")
policy_dir.mkdir(parents=True, exist_ok=True)

policies = {
    "retention_career_growth.md": """# Retention & Career Growth Policy

This policy defines how the organisation supports employee retention, internal mobility, career growth, and early intervention for avoidable resignations. The goal is to ensure that employees can see a credible future inside the organisation before they begin looking externally.

Managers are expected to hold career conversations at least twice per year. These conversations should cover role satisfaction, learning goals, internal mobility interests, promotion readiness, workload concerns, and any barriers affecting performance or wellbeing. A career conversation is not a performance review; it is a forward-looking discussion focused on growth, opportunity, and retention.

Employees who have been in the same role for more than eighteen months should be considered for internal mobility conversations. Where business needs allow, managers should support lateral moves, stretch assignments, mentoring, shadowing, and project-based exposure across teams. Internal applicants should receive fair consideration before an external hiring process is finalised.

Promotion readiness is reviewed during the annual performance cycle and again during the mid-year talent review. Promotion decisions must consider performance, scope of responsibility, demonstrated behaviours, and business need. Time in role alone does not guarantee promotion, but long periods without progression should trigger a manager review.

Stay interviews should be used for employees in critical roles, high-performing employees, and employees with elevated attrition risk. A stay interview should explore what keeps the employee engaged, what may cause them to leave, what support they need from their manager, and whether there are immediate actions that could improve their experience.

If an employee is identified as a flight risk, the manager should escalate to the HR Business Partner within five business days. The escalation should include the reason for concern, recent engagement signals, role criticality, and proposed retention actions. Retention actions may include workload adjustment, career planning, mentoring, recognition, flexible work review, or targeted development support.

No employee should be told that an algorithm or analytics model has labelled them as a risk. Analytics may support manager awareness, but all actions must remain human-led, respectful, and focused on support rather than surveillance.

Retention interventions must be documented at an aggregate level for governance. Individual notes should be limited to relevant business information and must not include sensitive personal details unless the employee has voluntarily raised them and there is a legitimate HR reason to record them.
""",

    "compensation_pay_equity.md": """# Compensation & Pay Equity Policy

This policy defines the organisation's approach to compensation, salary bands, variable pay, and pay equity review. The objective is to provide fair, transparent, and market-aware compensation practices while protecting employee privacy.

Each role is assigned to a salary band based on job family, job level, location, market benchmarks, and scope of responsibility. Salary bands are reviewed annually by the People and Finance teams. Managers may not create informal salary bands or make off-cycle pay commitments without HR and Finance approval.

Compensation decisions must consider role level, performance, skills, market movement, internal equity, and budget availability. Managers should avoid using negotiation strength, personal preference, or non-work-related factors as reasons for pay differences. Where exceptions are proposed, the business reason must be documented and reviewed by HR.

The annual compensation review includes base salary, variable pay eligibility, and equity adjustments where applicable. Performance may influence salary movement, but performance ratings must not be the only input. Employees at the lower end of the salary band who are meeting expectations should be reviewed carefully for progression.

Pay equity analysis is conducted at least once per year. The review compares compensation outcomes across gender, age band, department, job level, tenure cohort, and other lawful business dimensions where data is available and appropriate. Any group-level difference should be investigated to determine whether it is explained by role level, experience, performance, location, or another legitimate factor.

If an unexplained pay gap is identified, HR will prepare a remediation recommendation for leadership review. Remediation may include salary adjustment, promotion review, band correction, or process change. Pay equity actions should be handled confidentially and should not disadvantage employees who raise compensation concerns.

Variable pay, bonus, and recognition programs must be applied consistently. Eligibility rules should be documented before awards are approved. Managers must be able to explain the business basis for any exceptional bonus recommendation.

Employees may ask questions about their salary band, compensation review process, and progression expectations. Managers should provide practical guidance without disclosing another employee's compensation.

Compensation analytics must be aggregated where possible. Individual-level compensation data should only be visible to authorised HR, Finance, and leadership users with a legitimate business need.
""",

    "diversity_inclusion_wellbeing.md": """# Diversity, Inclusion & Wellbeing Charter

This charter defines the organisation's commitment to inclusive employment practices, fair representation, wellbeing, and respectful workplace behaviour. The goal is to create a workplace where people can contribute safely and progress based on capability, performance, and potential.

Hiring processes should be structured, consistent, and evidence-based. Interview panels should use role-related criteria and avoid questions that are not relevant to the work. Candidate shortlists should be reviewed for representation where enough applications are available. Hiring managers should document selection reasons before final approval.

Promotion, development, and succession processes should be reviewed for fairness across gender, age band, department, job level, and other lawful business categories. Where a group is under-represented in leadership or critical roles, HR should work with leaders to understand the cause and create practical actions such as mentoring, sponsorship, training access, or clearer progression pathways.

The organisation supports flexible work where it is compatible with role requirements, team delivery, and customer needs. Flexible work decisions should be made consistently and should not penalise employees in performance, promotion, or development discussions.

Employee wellbeing is a shared responsibility between employees, managers, HR, and leadership. Managers should watch for workload pressure, sustained overtime, low engagement, conflict, or sudden behavioural changes. Where wellbeing concerns are raised, managers should listen, offer practical support, and involve HR where further assistance is needed.

The organisation does not tolerate discrimination, harassment, bullying, victimisation, or retaliation. Employees can raise concerns with their manager, HR Business Partner, senior leader, or another approved reporting channel. Concerns should be handled promptly, confidentially, and fairly.

Diversity and wellbeing reporting must be aggregated and privacy-protected. Dashboards should apply minimum group-size thresholds before showing demographic breakdowns. No manager should use demographic information to make negative employment decisions about an individual.

Inclusion is measured through engagement surveys, representation trends, hiring outcomes, promotion patterns, attrition patterns, and qualitative feedback. Metrics are used to identify systemic issues and improve workplace practices, not to label individuals or teams unfairly.

Leaders are accountable for creating respectful team environments. This includes modelling inclusive behaviour, addressing inappropriate conduct early, making development opportunities visible, and ensuring employees have a safe way to raise concerns.
"""
}

for filename, text in policies.items():
    (policy_dir / filename).write_text(text, encoding="utf-8")

styles = getSampleStyleSheet()

for md_file in policy_dir.glob("*.md"):
    raw = md_file.read_text(encoding="utf-8")
    story = []
    for block in raw.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        if block.startswith("#"):
            story.append(Paragraph(escape(block.lstrip("# ").strip()), styles["Heading1"]))
        else:
            story.append(Paragraph(escape(block), styles["BodyText"]))
        story.append(Spacer(1, 8))

    pdf_path = md_file.with_suffix(".pdf")
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
    doc.build(story)
    print(f"wrote {pdf_path}")

print("Policy PDFs ready.")
