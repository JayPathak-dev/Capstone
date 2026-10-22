import os
import sys
from datetime import date, timedelta
import random

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.db.session import SessionLocal, init_db
from backend.app.models.project import Project
from backend.app.models.progress_update import ProgressUpdate
from backend.app.models.milestone import Milestone
from backend.app.models.risk_assessment import RiskAssessment
from backend.app.ml.fallback import calculate_calibrated_risk
from backend.app.services.alerts import scan_and_generate_alerts


PROJECT_DEFINITIONS = [
    # Roads & Highways
    {
        "code": "NHAI-2023-DEL-01",
        "name": "Delhi-Dehradun Economic Corridor Package 2",
        "sector": "Roads & Highways",
        "dept": "Ministry of Road Transport and Highways",
        "region": "Northern",
        "agency": "NHAI",
        "budget": 4850.0,
        "revised": 5420.0,
        "spent": 4200.0,
        "start": date(2022, 6, 1),
        "end": date(2025, 3, 31),
        "actual_prog": 58.5,
        "status": "DELAYED",
    },
    {
        "code": "NHAI-2023-BOM-04",
        "name": "Mumbai-Goa Coastal Highway Widening Section IV",
        "sector": "Roads & Highways",
        "dept": "Ministry of Road Transport and Highways",
        "region": "Western",
        "agency": "MSRDC / NHAI",
        "budget": 3600.0,
        "revised": None,
        "spent": 2980.0,
        "start": date(2021, 10, 15),
        "end": date(2024, 12, 31),
        "actual_prog": 49.0,
        "status": "DELAYED",
    },
    {
        "code": "NHAI-2024-BLR-02",
        "name": "Bengaluru Satellite Ring Road Package 3",
        "sector": "Roads & Highways",
        "dept": "Ministry of Road Transport and Highways",
        "region": "Southern",
        "agency": "NHAI",
        "budget": 5200.0,
        "revised": None,
        "spent": 3800.0,
        "start": date(2022, 1, 10),
        "end": date(2025, 9, 30),
        "actual_prog": 76.0,
        "status": "IN_PROGRESS",
    },
    {
        "code": "NHAI-2024-KOL-07",
        "name": "Varanasi-Kolkata Expressway Package 4",
        "sector": "Roads & Highways",
        "dept": "Ministry of Road Transport and Highways",
        "region": "Eastern",
        "agency": "NHAI",
        "budget": 2950.0,
        "revised": 3100.0,
        "spent": 1400.0,
        "start": date(2023, 3, 1),
        "end": date(2026, 6, 30),
        "actual_prog": 34.0,
        "status": "IN_PROGRESS",
    },
    {
        "code": "NHIDCL-2023-GHY-09",
        "name": "Zojila Tunnel Bypass and Connecting Roadways",
        "sector": "Roads & Highways",
        "dept": "Ministry of Road Transport and Highways",
        "region": "Northern",
        "agency": "NHIDCL",
        "budget": 6800.0,
        "revised": 7950.0,
        "spent": 6100.0,
        "start": date(2020, 8, 1),
        "end": date(2025, 11, 30),
        "actual_prog": 62.0,
        "status": "DELAYED",
    },
    # Railways
    {
        "code": "DFCCIL-2022-WDFC-01",
        "name": "Western Dedicated Freight Corridor (Dadri-JNPT)",
        "sector": "Railways",
        "dept": "Ministry of Railways",
        "region": "Western",
        "agency": "DFCCIL",
        "budget": 14500.0,
        "revised": 16200.0,
        "spent": 14900.0,
        "start": date(2019, 4, 1),
        "end": date(2024, 10, 31),
        "actual_prog": 88.0,
        "status": "DELAYED",
    },
    {
        "code": "RVNL-2023-RK-05",
        "name": "Rishikesh-Karanprayag Broad Gauge Rail Link",
        "sector": "Railways",
        "dept": "Ministry of Railways",
        "region": "Northern",
        "agency": "RVNL",
        "budget": 16200.0,
        "revised": 18400.0,
        "spent": 15100.0,
        "start": date(2018, 9, 15),
        "end": date(2025, 12, 31),
        "actual_prog": 68.0,
        "status": "DELAYED",
    },
    {
        "code": "NHSRCL-2023-MAHSR-01",
        "name": "Mumbai-Ahmedabad High Speed Rail (Bullet Train)",
        "sector": "Railways",
        "dept": "Ministry of Railways",
        "region": "Western",
        "agency": "NHSRCL",
        "budget": 108000.0,
        "revised": 115000.0,
        "spent": 64500.0,
        "start": date(2018, 1, 1),
        "end": date(2026, 12, 31),
        "actual_prog": 53.0,
        "status": "IN_PROGRESS",
    },
    {
        "code": "IRCON-2023-NE-08",
        "name": "Bairabi-Sairang New Railway Line Project",
        "sector": "Railways",
        "dept": "Ministry of Railways",
        "region": "North-Eastern",
        "agency": "IRCON",
        "budget": 6500.0,
        "revised": 7200.0,
        "spent": 5900.0,
        "start": date(2017, 11, 1),
        "end": date(2025, 7, 31),
        "actual_prog": 79.5,
        "status": "DELAYED",
    },
    # Urban Mass Transit
    {
        "code": "DMRC-2023-PH4-02",
        "name": "Delhi Metro Phase IV Aerocity-Tughlakabad Corridor",
        "sector": "Urban Mass Transit",
        "dept": "Ministry of Housing and Urban Affairs",
        "region": "Northern",
        "agency": "DMRC",
        "budget": 6150.0,
        "revised": None,
        "spent": 2900.0,
        "start": date(2021, 3, 1),
        "end": date(2026, 3, 31),
        "actual_prog": 44.0,
        "status": "IN_PROGRESS",
    },
    {
        "code": "BMRCL-2023-PH2A-01",
        "name": "Bengaluru Metro Phase 2A Outer Ring Road Silk Board",
        "sector": "Urban Mass Transit",
        "dept": "Ministry of Housing and Urban Affairs",
        "region": "Southern",
        "agency": "BMRCL",
        "budget": 5900.0,
        "revised": 6450.0,
        "spent": 4800.0,
        "start": date(2021, 6, 1),
        "end": date(2025, 6, 30),
        "actual_prog": 66.0,
        "status": "DELAYED",
    },
    {
        "code": "MMRDA-2024-M4-03",
        "name": "Mumbai Metro Line 4 (Wadala-Kasarvadavali Elevated)",
        "sector": "Urban Mass Transit",
        "dept": "Ministry of Housing and Urban Affairs",
        "region": "Western",
        "agency": "MMRDA",
        "budget": 14500.0,
        "revised": 16800.0,
        "spent": 12800.0,
        "start": date(2019, 1, 15),
        "end": date(2025, 12, 31),
        "actual_prog": 54.0,
        "status": "DELAYED",
    },
    {
        "code": "GMRC-2023-SURAT-01",
        "name": "Surat Metro Rail Project Phase 1",
        "sector": "Urban Mass Transit",
        "dept": "Ministry of Housing and Urban Affairs",
        "region": "Western",
        "agency": "GMRC",
        "budget": 12000.0,
        "revised": None,
        "spent": 4800.0,
        "start": date(2021, 5, 10),
        "end": date(2027, 3, 31),
        "actual_prog": 38.0,
        "status": "IN_PROGRESS",
    },
    # Power & Renewable Energy
    {
        "code": "NTPC-2023-SOL-KHAV",
        "name": "Khavda 4750MW Ultra Mega Renewable Energy Solar Park",
        "sector": "Power & Renewable Energy",
        "dept": "Ministry of Power",
        "region": "Western",
        "agency": "NTPC Renewable Energy",
        "budget": 18500.0,
        "revised": None,
        "spent": 11200.0,
        "start": date(2022, 2, 1),
        "end": date(2026, 3, 31),
        "actual_prog": 61.0,
        "status": "IN_PROGRESS",
    },
    {
        "code": "NHPC-2022-SUB-01",
        "name": "Subansiri Lower Hydroelectric Project (2000 MW)",
        "sector": "Power & Renewable Energy",
        "dept": "Ministry of Power",
        "region": "North-Eastern",
        "agency": "NHPC",
        "budget": 19800.0,
        "revised": 23200.0,
        "spent": 21500.0,
        "start": date(2015, 1, 1),
        "end": date(2025, 8, 31),
        "actual_prog": 91.0,
        "status": "DELAYED",
    },
    {
        "code": "PGCIL-2023-HVDC-04",
        "name": "Leh-Kaithal Green Energy Corridor HVDC Transmission Link",
        "sector": "Power & Renewable Energy",
        "dept": "Ministry of Power",
        "region": "Northern",
        "agency": "POWERGRID",
        "budget": 20500.0,
        "revised": None,
        "spent": 5200.0,
        "start": date(2023, 7, 1),
        "end": date(2028, 12, 31),
        "actual_prog": 24.5,
        "status": "IN_PROGRESS",
    },
    {
        "code": "THDC-2023-PUMP-02",
        "name": "Tehri Pumped Storage Plant (1000 MW)",
        "sector": "Power & Renewable Energy",
        "dept": "Ministry of Power",
        "region": "Northern",
        "agency": "THDC India",
        "budget": 4800.0,
        "revised": 5600.0,
        "spent": 4900.0,
        "start": date(2018, 5, 1),
        "end": date(2025, 4, 30),
        "actual_prog": 83.0,
        "status": "DELAYED",
    },
    # Water & Sanitation
    {
        "code": "JJM-2023-BUNDEL-01",
        "name": "Bundelkhand Piped Water Supply Surface Grid",
        "sector": "Water & Sanitation",
        "dept": "Department of Drinking Water and Sanitation",
        "region": "Central",
        "agency": "State Water & Sanitation Mission",
        "budget": 4200.0,
        "revised": 4650.0,
        "spent": 3950.0,
        "start": date(2021, 2, 1),
        "end": date(2024, 11, 30),
        "actual_prog": 78.0,
        "status": "DELAYED",
    },
    {
        "code": "NMCG-2023-VAR-03",
        "name": "Namami Gange Varanasi Comprehensive STP Infrastructure",
        "sector": "Water & Sanitation",
        "dept": "Ministry of Jal Shakti",
        "region": "Northern",
        "agency": "NMCG / UP Jal Nigam",
        "budget": 1650.0,
        "revised": None,
        "spent": 1280.0,
        "start": date(2022, 4, 1),
        "end": date(2025, 5, 31),
        "actual_prog": 74.0,
        "status": "IN_PROGRESS",
    },
    {
        "code": "NWDA-2023-KEN-01",
        "name": "Ken-Betwa River Link National Project Package A",
        "sector": "Water & Sanitation",
        "dept": "Ministry of Jal Shakti",
        "region": "Central",
        "agency": "Ken-Betwa Link Authority",
        "budget": 44605.0,
        "revised": None,
        "spent": 8200.0,
        "start": date(2022, 12, 1),
        "end": date(2030, 3, 31),
        "actual_prog": 18.0,
        "status": "IN_PROGRESS",
    },
    # Ports & Shipping
    {
        "code": "SAGAR-2023-JNPA-02",
        "name": "JNPA Fourth Container Terminal Phase II Expansion",
        "sector": "Ports & Shipping",
        "dept": "Ministry of Ports, Shipping and Waterways",
        "region": "Western",
        "agency": "JNPA / PSA",
        "budget": 3196.0,
        "revised": None,
        "spent": 2450.0,
        "start": date(2021, 3, 1),
        "end": date(2025, 4, 30),
        "actual_prog": 77.0,
        "status": "IN_PROGRESS",
    },
    {
        "code": "SAGAR-2023-VIZ-01",
        "name": "Vizhinjam International Deepwater Multipurpose Seaport",
        "sector": "Ports & Shipping",
        "dept": "Ministry of Ports, Shipping and Waterways",
        "region": "Southern",
        "agency": "VISL / Adani Ports",
        "budget": 7700.0,
        "revised": 8250.0,
        "spent": 7100.0,
        "start": date(2017, 8, 1),
        "end": date(2025, 5, 31),
        "actual_prog": 89.0,
        "status": "IN_PROGRESS",
    },
    {
        "code": "SAGAR-2024-VAD-01",
        "name": "Vadhavan Mega All-Weather Port Development",
        "sector": "Ports & Shipping",
        "dept": "Ministry of Ports, Shipping and Waterways",
        "region": "Western",
        "agency": "VPPL",
        "budget": 76220.0,
        "revised": None,
        "spent": 3800.0,
        "start": date(2023, 9, 1),
        "end": date(2030, 12, 31),
        "actual_prog": 6.5,
        "status": "IN_PROGRESS",
    },
]


def seed():
    print("Initializing database tables...")
    init_db()
    db = SessionLocal()

    # Clear existing data to allow clean re-seed
    print("Clearing previous demo records...")
    db.query(Milestone).delete()
    db.query(ProgressUpdate).delete()
    db.query(RiskAssessment).delete()
    db.query(Project).delete()
    db.commit()

    print(f"Seeding {len(PROJECT_DEFINITIONS)} infrastructure projects...")
    created_projects = []

    for item in PROJECT_DEFINITIONS:
        eff_budget = item["revised"] or item["budget"]
        fin_prog = round((item["spent"] / eff_budget) * 100.0, 2)

        p = Project(
            project_code=item["code"],
            project_name=item["name"],
            sector=item["sector"],
            department=item["dept"],
            region=item["region"],
            implementing_agency=item["agency"],
            approved_budget=item["budget"],
            revised_budget=item["revised"],
            actual_expenditure=item["spent"],
            planned_start_date=item["start"],
            expected_completion_date=item["end"],
            current_physical_progress=item["actual_prog"],
            current_financial_progress=fin_prog,
            project_status=item["status"],
        )
        db.add(p)
        db.flush()

        # Generate 6-8 monthly progress updates for history
        total_months = 7
        curr_phys = item["actual_prog"]
        curr_spent = item["spent"]
        updates = []

        for m_idx in range(total_months, 0, -1):
            report_dt = date.today() - timedelta(days=m_idx * 30)
            phys_val = max(5.0, round(curr_phys - (m_idx * random.uniform(2.5, 4.0)), 1))
            plan_val = min(100.0, round(phys_val + random.uniform(2.0, 9.0), 1))
            spent_val = max(100.0, round(curr_spent - (m_idx * (curr_spent / 12.0) * random.uniform(0.7, 1.2)), 1))

            issue = None
            if plan_val - phys_val > 5.0:
                issues_pool = [
                    "Delay in forest diversion clearance for 42 hectares",
                    "Right of Way (RoW) encumbrance between chainage 30km and 48km",
                    "Contractor quarry permit pending state environmental approval",
                    "Unseasonal monsoon rains causing bridge pier foundation inundation",
                    "High-tension utility line relocation pending state power utility approval",
                ]
                issue = random.choice(issues_pool)

            u = ProgressUpdate(
                project_id=p.id,
                reporting_date=report_dt,
                planned_progress=plan_val,
                actual_progress=phys_val,
                cumulative_expenditure=spent_val,
                reported_issues=issue,
                data_source="PAIMANA_PORTAL",
            )
            db.add(u)
            updates.append(u)

        # Generate standard key milestones
        milestone_templates = [
            ("Detailed Design & Environmental Clearance", 0.15),
            ("Land Acquisition & Right-of-Way Handover", 0.35),
            ("Substructure & Major Civil Earthworks", 0.60),
            ("Superstructure & Critical Equipment Erection", 0.85),
            ("Integrated Testing, Trial Run & Commissioning", 1.00),
        ]

        overdue_count = 0
        max_delay = 0

        for order, (m_name, target_frac) in enumerate(milestone_templates, start=1):
            total_duration_days = (item["end"] - item["start"]).days
            milestone_dt = item["start"] + timedelta(days=int(total_duration_days * target_frac))

            # Status determination
            if curr_phys >= (target_frac * 100.0):
                m_status = "COMPLETED"
                m_comp = 100.0
                m_actual_dt = milestone_dt - timedelta(days=random.randint(0, 15))
            elif milestone_dt < date.today():
                m_status = "DELAYED"
                m_comp = round(max(10.0, curr_phys / target_frac), 1)
                m_actual_dt = None
                overdue_count += 1
                max_delay = max(max_delay, (date.today() - milestone_dt).days)
            else:
                m_status = "PENDING"
                m_comp = round(max(0.0, curr_phys / target_frac * 0.5), 1)
                m_actual_dt = None

            m = Milestone(
                project_id=p.id,
                milestone_name=m_name,
                planned_date=milestone_dt,
                actual_date=m_actual_dt,
                status=m_status,
                completion_percentage=min(100.0, m_comp),
                order_index=order,
            )
            db.add(m)

        # Calculate calibrated risk
        planned_latest = curr_phys + (random.uniform(4.0, 14.0) if item["status"] == "DELAYED" else 3.0)
        risk = calculate_calibrated_risk(
            approved_budget=p.approved_budget,
            revised_budget=p.revised_budget,
            actual_expenditure=p.actual_expenditure,
            planned_progress=planned_latest,
            actual_progress=p.current_physical_progress,
            planned_start_date=p.planned_start_date,
            expected_completion_date=p.expected_completion_date,
            overdue_milestones_count=overdue_count,
            max_milestone_delay_days=max_delay,
            recent_progress_delta_3m=random.uniform(2.0, 6.0),
            recent_expenditure_delta_3m=random.uniform(3.0, 8.0),
        )

        p.current_risk_score = risk["risk_score"]
        p.current_risk_level = risk["risk_level"]
        p.predicted_delay_days = risk["predicted_delay_days"]
        p.forecast_final_cost = risk["expected_final_cost"]

        # Persist risk assessment
        ra = RiskAssessment(
            project_id=p.id,
            cost_overrun_probability=risk["cost_overrun_probability"],
            delay_probability=risk["delay_probability"],
            expected_final_cost=risk["expected_final_cost"],
            predicted_delay_days=risk["predicted_delay_days"],
            risk_score=risk["risk_score"],
            risk_level=risk["risk_level"],
            model_version="calibrated-heuristic-v1.0",
            is_fallback=True,
            explanation=risk["explanation"],
        )
        db.add(ra)
        created_projects.append(p)

    db.commit()
    print("Projects and updates committed successfully.")

    # Scan and trigger early warning alerts
    print("Evaluating early warning detection rules...")
    alert_count = 0
    for p in created_projects:
        alerts = scan_and_generate_alerts(db, p)
        alert_count += len(alerts)

    db.commit()
    db.close()
    print(f"Database seeded successfully! Created {len(created_projects)} projects, {alert_count} active early warnings.")


if __name__ == "__main__":
    seed()
