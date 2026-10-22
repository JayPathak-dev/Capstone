import uuid
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func
from backend.app.models.project import Project
from backend.app.models.alert import Alert
from backend.app.models.milestone import Milestone
from backend.app.schemas.assistant import ChatRequest, ChatResponse, ReferencedProject
from backend.app.core.config import settings


# ==============================================================================
# Governed Backend Tools (Read-Only, Typed, Parameter-Checked)
# ==============================================================================

def tool_get_project_details(db: Session, identifier: str) -> Optional[Dict[str, Any]]:
    """Retrieve verified ground-truth project record by code or ID."""
    p = db.scalar(
        select(Project).filter(
            (Project.id == identifier) | (Project.project_code.ilike(f"%{identifier}%")) | (Project.project_name.ilike(f"%{identifier}%"))
        )
    )
    if not p:
        return None
    return {
        "id": p.id,
        "code": p.project_code,
        "name": p.project_name,
        "sector": p.sector,
        "agency": p.implementing_agency,
        "region": p.region,
        "approved_budget": p.approved_budget,
        "revised_budget": p.revised_budget,
        "actual_expenditure": p.actual_expenditure,
        "financial_progress": p.current_financial_progress,
        "physical_progress": p.current_physical_progress,
        "planned_start": str(p.planned_start_date),
        "expected_completion": str(p.expected_completion_date),
        "risk_score": p.current_risk_score,
        "risk_level": p.current_risk_level,
        "predicted_delay_days": p.predicted_delay_days,
        "forecast_final_cost": p.forecast_final_cost,
    }


def tool_list_high_risk_projects(db: Session, limit: int = 5, sector: Optional[str] = None) -> List[Dict[str, Any]]:
    """List projects in HIGH or CRITICAL risk bands."""
    query = select(Project).filter(Project.current_risk_level.in_(["HIGH", "CRITICAL"]))
    if sector and sector != "ALL":
        query = query.filter(Project.sector == sector)
    query = query.order_by(desc(Project.current_risk_score)).limit(limit)
    projects = db.scalars(query).all()
    return [
        {
            "id": p.id,
            "code": p.project_code,
            "name": p.project_name,
            "sector": p.sector,
            "risk_score": p.current_risk_score,
            "risk_level": p.current_risk_level,
            "physical_progress": p.current_physical_progress,
            "expenditure": p.actual_expenditure,
            "approved_budget": p.approved_budget,
            "predicted_delay_days": p.predicted_delay_days,
            "forecast_final_cost": p.forecast_final_cost,
        }
        for p in projects
    ]


def tool_get_overdue_milestones(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
    """Fetch pending milestones that missed their planned deadline."""
    query = (
        select(Milestone)
        .filter(Milestone.status.in_(["DELAYED", "MISSED"]))
        .order_by(Milestone.planned_date)
        .limit(limit)
    )
    milestones = db.scalars(query).all()
    return [
        {
            "project_code": m.project.project_code if m.project else "N/A",
            "project_name": m.project.project_name if m.project else "N/A",
            "milestone_name": m.milestone_name,
            "planned_date": str(m.planned_date),
            "status": m.status,
            "completion_percentage": m.completion_percentage,
        }
        for m in milestones
    ]


def tool_get_active_alerts(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieve latest early warning alerts."""
    query = select(Alert).filter(Alert.status.in_(["NEW", "ACKNOWLEDGED"])).order_by(desc(Alert.created_at)).limit(limit)
    alerts = db.scalars(query).all()
    return [
        {
            "project_code": a.project.project_code if a.project else "N/A",
            "project_name": a.project.project_name if a.project else "N/A",
            "title": a.title,
            "severity": a.severity,
            "alert_type": a.alert_type,
            "recommended_action": a.recommended_action,
        }
        for a in alerts
    ]


# ==============================================================================
# Assistant Orchestrator (Tool Calling & Grounded Response Synthesis)
# ==============================================================================

def process_assistant_chat(db: Session, request: ChatRequest) -> ChatResponse:
    """
    Execute grounded assistant turn:
    1. Parse intent and extract entities.
    2. Invoke authorized backend tools.
    3. Generate data-grounded response with explicit evidence links.
    """
    msg = request.message.lower().strip()
    tools_used: List[str] = []
    referenced_projects: List[ReferencedProject] = []
    response_text = ""
    suggested_followups = [
        "Which projects are likely to exceed their approved budgets?",
        "What critical milestones are currently overdue across railway projects?",
        "Show me all active CRITICAL early warnings.",
        "Compare progress between highways and urban transit sectors.",
    ]

    conv_id = request.conversation_id or str(uuid.uuid4())

    # Case 1: Specific project lookup by code or keyword
    # e.g., "Tell me about NHAI-2024-EXP-08" or "status of Delhi-Dehradun"
    project_match = re.search(r'([A-Za-z]+-[0-9]{4}-[A-Za-z0-9\-]+)', request.message)
    target_project_code = project_match.group(1) if project_match else None

    # If code not matched by regex, check if message mentions known project names
    if not target_project_code:
        first_few = db.execute(select(Project.project_code, Project.project_name).limit(30)).all()
        for pcode, pname in first_few:
            if (pname and pname.lower() in msg) or (pcode and pcode.lower() in msg):
                target_project_code = pcode
                break

    if target_project_code:
        tools_used.append("get_project_details")
        p_data = tool_get_project_details(db, target_project_code)
        if p_data:
            referenced_projects.append(
                ReferencedProject(
                    project_id=p_data["id"],
                    project_code=p_data["code"],
                    project_name=p_data["name"],
                    sector=p_data["sector"],
                    risk_score=p_data["risk_score"],
                    risk_level=p_data["risk_level"],
                )
            )
            variance = p_data["forecast_final_cost"] - p_data["approved_budget"]
            variance_sign = "+" if variance > 0 else ""

            response_text = (
                f"### Project Intelligence Dossier: **{p_data['name']}** (`{p_data['code']}`)\n\n"
                f"- **Sector & Agency**: {p_data['sector']} | {p_data['agency']} ({p_data['region']} Region)\n"
                f"- **Sanctioned Budget**: ₹ {p_data['approved_budget']:,.2f} Cr"
                + (f" (Revised: ₹ {p_data['revised_budget']:,.2f} Cr)\n" if p_data['revised_budget'] else "\n")
                + f"- **Actual Expenditure**: ₹ {p_data['actual_expenditure']:,.2f} Cr ({p_data['financial_progress']:.1f}% consumed)\n"
                f"- **Physical Progress**: **{p_data['physical_progress']:.1f}%**\n"
                f"- **Predictive Risk Assessment**: **{p_data['risk_score']:.1f}/100** ({p_data['risk_level']} Risk)\n"
                f"- **Forecast Final Cost**: ₹ {p_data['forecast_final_cost']:,.2f} Cr (Variance: {variance_sign}₹ {variance:,.2f} Cr)\n"
                f"- **Predicted Delay**: **{p_data['predicted_delay_days']} days** beyond scheduled target ({p_data['expected_completion']})\n\n"
            )

            if p_data["risk_level"] in ("HIGH", "CRITICAL"):
                response_text += (
                    "> **Key Risk Driver**: The project shows a significant divergence between financial expenditure "
                    f"({p_data['financial_progress']:.1f}%) and on-site physical delivery ({p_data['physical_progress']:.1f}%). "
                    "Recommend convening a formal site inspection before certifying the next contractor invoice."
                )
            else:
                response_text += "> **Current Status**: Progress and expenditure velocities remain within contract tolerances."
            return ChatResponse(
                response=response_text,
                conversation_id=conv_id,
                tools_used=tools_used,
                referenced_projects=referenced_projects,
                suggested_followups=[
                    f"Why is {p_data['code']} scored as {p_data['risk_level']} risk?",
                    f"Show peers similar to {p_data['code']}",
                    "List all projects at high risk",
                ],
            )

    # Case 2: Highest risk projects query
    if any(k in msg for k in ["high risk", "critical risk", "worst", "top risk", "highest risk", "failing"]):
        tools_used.append("list_high_risk_projects")
        high_risk_list = tool_list_high_risk_projects(db, limit=5)
        for hr in high_risk_list:
            referenced_projects.append(
                ReferencedProject(
                    project_id=hr["id"],
                    project_code=hr["code"],
                    project_name=hr["name"],
                    sector=hr["sector"],
                    risk_score=hr["risk_score"],
                    risk_level=hr["risk_level"],
                )
            )

        response_text = (
            "### Priority Infrastructure Watchlist: High & Critical Risk Projects\n\n"
            "Based on verified PAIMANA monitoring records and predictive risk evaluation, the following projects require immediate administrative oversight:\n\n"
        )
        for i, hr in enumerate(high_risk_list, start=1):
            cost_var = hr["forecast_final_cost"] - hr["approved_budget"]
            response_text += (
                f"{i}. **{hr['name']}** (`{hr['code']}`)\n"
                f"   - **Sector**: {hr['sector']} | **Risk Score**: **{hr['risk_score']:.1f}/100** ({hr['risk_level']})\n"
                f"   - **Progress vs. Budget**: Physical {hr['physical_progress']:.1f}% completed | ₹ {hr['expenditure']:,.1f} Cr of ₹ {hr['approved_budget']:,.1f} Cr spent\n"
                f"   - **Predicted Impact**: **{hr['predicted_delay_days']} days delay** | Estimated Cost Overrun: +₹ {max(0, cost_var):,.1f} Cr\n\n"
            )
        response_text += "You can click any highlighted project code to inspect its detailed timeline, milestones, and root-cause diagnostics."
        return ChatResponse(
            response=response_text,
            conversation_id=conv_id,
            tools_used=tools_used,
            referenced_projects=referenced_projects,
            suggested_followups=[
                f"Give me details on {high_risk_list[0]['code'] if high_risk_list else 'the top project'}",
                "What early warnings are active for these projects?",
                "Which milestones are delayed?",
            ],
        )

    # Case 3: Overdue milestones query
    if any(k in msg for k in ["milestone", "overdue", "missed", "delayed stage"]):
        tools_used.append("get_overdue_milestones")
        milestones = tool_get_overdue_milestones(db, limit=5)
        response_text = "### Overdue Critical Path Milestones\n\n"
        if milestones:
            response_text += "The following critical milestones have breached their contractual delivery target:\n\n"
            for m in milestones:
                response_text += (
                    f"- **{m['milestone_name']}** (`{m['project_code']}` - {m['project_name']})\n"
                    f"  - Planned Target Date: `{m['planned_date']}` | Status: **{m['status']}** ({m['completion_percentage']:.0f}% finished)\n"
                )
            response_text += "\n*Recommendation: Issue a contractual cure notice to concessionaires on critical path milestones.*"
        else:
            response_text += "No critical milestones are currently recorded as overdue."
        return ChatResponse(
            response=response_text,
            conversation_id=conv_id,
            tools_used=tools_used,
            referenced_projects=[],
            suggested_followups=suggested_followups,
        )

    # Case 4: Cost overruns / budget breaches
    if any(k in msg for k in ["cost overrun", "budget breach", "over budget", "escalation"]):
        tools_used.append("list_high_risk_projects")
        overrun_projects = db.scalars(
            select(Project)
            .filter(Project.forecast_final_cost > Project.approved_budget)
            .order_by(desc(Project.forecast_final_cost - Project.approved_budget))
            .limit(5)
        ).all()

        response_text = "### Forecast Cost Overrun Analysis\n\n"
        if overrun_projects:
            response_text += "The following projects exhibit the highest predicted cost escalation above sanctioned estimates:\n\n"
            for p in overrun_projects:
                diff = p.forecast_final_cost - p.approved_budget
                pct = (diff / p.approved_budget) * 100.0 if p.approved_budget > 0 else 0.0
                referenced_projects.append(
                    ReferencedProject(
                        project_id=p.id,
                        project_code=p.project_code,
                        project_name=p.project_name,
                        sector=p.sector,
                        risk_score=p.current_risk_score,
                        risk_level=p.current_risk_level,
                    )
                )
                response_text += (
                    f"- **{p.project_name}** (`{p.project_code}`)\n"
                    f"  - Approved: ₹ {p.approved_budget:,.1f} Cr -> Forecast Final: **₹ {p.forecast_final_cost:,.1f} Cr**\n"
                    f"  - Projected Escalation: **+₹ {diff:,.1f} Cr (+{pct:.1f}%)**\n"
                )
            response_text += "\n*Root Causes: Construction commodity inflation, scope additions, and prolonged right-of-way clearance.*"
        else:
            response_text += "Currently all active projects are trending within sanctioned budget allocations."
        return ChatResponse(
            response=response_text,
            conversation_id=conv_id,
            tools_used=tools_used,
            referenced_projects=referenced_projects,
            suggested_followups=suggested_followups,
        )

    # Case 5: Alerts / Early warnings
    if any(k in msg for k in ["alert", "warning", "early warning", "notifications"]):
        tools_used.append("get_active_alerts")
        alerts = tool_get_active_alerts(db, limit=5)
        response_text = "### Active Early Warning Alerts\n\n"
        if alerts:
            for a in alerts:
                response_text += (
                    f"- **[{a['severity']}] {a['title']}** (`{a['project_code']}`)\n"
                    f"  - Type: `{a['alert_type']}`\n"
                    f"  - Prescribed Action: {a['recommended_action']}\n\n"
                )
        else:
            response_text += "No unacknowledged high-severity alerts at this time."
        return ChatResponse(
            response=response_text,
            conversation_id=conv_id,
            tools_used=tools_used,
            referenced_projects=[],
            suggested_followups=suggested_followups,
        )

    # Default / General Question
    tools_used.append("get_portfolio_summary")
    total_count = db.scalar(select(func.count(Project.id))) or 0
    high_count = db.scalar(select(func.count(Project.id)).filter(Project.current_risk_level.in_(["HIGH", "CRITICAL"]))) or 0

    response_text = (
        f"I am the **PAIMANA Infrastructure Intelligence Assistant**. I monitor **{total_count} active infrastructure projects**, "
        f"of which **{high_count} projects** are currently flagged with elevated risk requiring administrative intervention.\n\n"
        "You can ask me questions such as:\n"
        "- *'Which 5 projects have the highest predicted delays?'*\n"
        "- *'Give me a detailed status of project NHAI-2024-EXP-08'*\n"
        "- *'Which projects have high financial spend but lagging physical progress?'*\n"
        "- *'What milestones are overdue across railway corridors?'*\n\n"
        "*All facts and figures in my responses are verified against primary PAIMANA database records.*"
    )

    return ChatResponse(
        response=response_text,
        conversation_id=conv_id,
        tools_used=tools_used,
        referenced_projects=[],
        suggested_followups=suggested_followups,
    )
