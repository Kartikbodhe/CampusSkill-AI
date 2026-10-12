"""Personalized Learning Roadmap Generator for CampusSkill AI.

Builds structured, 4-phase learning roadmaps tailored to the student's
actual skill gaps and target job role requirements.
"""
from datetime import datetime, timezone
from extensions import db
from models.roadmap import Roadmap, RoadmapTask
from services.skill_gap import analyze_skill_gap


# Curated learning resources for high-demand placement skills
CURATED_RESOURCES = {
    "Python": {
        "docs": "https://docs.python.org/3/tutorial/",
        "project": "Build an Automated ETL or Data Cleaning Script in Python",
        "interview": "Explain Python GIL, generators, decorators, and memory management",
    },
    "SQL": {
        "docs": "https://mode.com/sql-tutorial/",
        "project": "Build an E-commerce Multi-Table Relational Schema with Complex Window Functions",
        "interview": "Practice Joins, Group By, Indexes, CTEs, and Subqueries",
    },
    "Data Structures and Algorithms": {
        "docs": "https://leetcode.com/explore/",
        "project": "Implement standard Trees, Graphs, Sorting, and Dynamic Programming algorithms",
        "interview": "Solve 50 curated Blind-75 interview questions with complexity analysis",
    },
    "Power BI": {
        "docs": "https://learn.microsoft.com/en-us/power-bi/",
        "project": "Design an Executive Sales Performance Dashboard with DAX measures",
        "interview": "Demonstrate star schema modeling, relationships, and drill-throughs",
    },
    "Excel": {
        "docs": "https://excel-easy.com/",
        "project": "Build an interactive financial model with XLOOKUP and Pivot Charts",
        "interview": "Master VLOOKUP, INDEX-MATCH, conditional formatting, and Pivot tables",
    },
    "React": {
        "docs": "https://react.dev/learn",
        "project": "Build a responsive CRUD dashboard with Hooks, State management, and API calls",
        "interview": "Virtual DOM, useEffect dependencies, custom hooks, and state reconciliation",
    },
    "Flask": {
        "docs": "https://flask.palletsprojects.com/",
        "project": "Develop a RESTful API with Flask-SQLAlchemy, authentication, and JWT tokens",
        "interview": "Application factories, blueprints, SQLAlchemy sessions, and WSGI deployment",
    },
    "Communication": {
        "docs": "https://www.toastmasters.org/",
        "project": "Prepare and record a 3-minute STAR method pitch of your capstone project",
        "interview": "Mock behavioral interviews: leadership, conflict resolution, and teamwork",
    },
    "Aptitude": {
        "docs": "https://www.indiabix.com/aptitude/questions-and-answers/",
        "project": "Solve 100 quantitative and logical reasoning speed tests",
        "interview": "Time-management strategies for company screening rounds",
    },
}


def generate_or_update_roadmap(student_profile, job_role):
    """
    Generate or rebuild a personalized learning roadmap based on skill gaps.
    Preserves completed tasks if matching tasks exist.
    """
    if not job_role:
        return None

    gap_data = analyze_skill_gap(student_profile, job_role)
    if not gap_data:
        return None

    # Check for existing roadmap for this role
    roadmap = Roadmap.query.filter_by(
        student_profile_id=student_profile.id,
        target_job_role_id=job_role.id
    ).first()

    existing_completed_titles = set()
    if roadmap:
        existing_completed_titles = {t.title for t in roadmap.tasks if t.is_completed}
        # Clear existing tasks to regenerate clean plan
        RoadmapTask.query.filter_by(roadmap_id=roadmap.id).delete()
    else:
        roadmap = Roadmap(
            student_profile_id=student_profile.id,
            target_job_role_id=job_role.id,
            completion_percentage=0.0
        )
        db.session.add(roadmap)
        db.session.flush()

    tasks_to_add = []

    # 1. Target Missing Skills (Highest Priority)
    for skill_info in gap_data["missing_skills"]:
        s_name = skill_info["skill_name"]
        res = CURATED_RESOURCES.get(s_name, {})

        # Phase 1: Core Fundamentals
        tasks_to_add.append(RoadmapTask(
            roadmap_id=roadmap.id,
            title=f"Learn Core Fundamentals of {s_name}",
            category=skill_info["category"],
            phase=1,
            description=f"Study core syntax, fundamental concepts, and essential patterns for {s_name}. {skill_info['recommendation_tip']}",
            priority="High",
            estimated_hours=8,
            resource_url=res.get("docs", "https://developer.mozilla.org/"),
            is_completed=(f"Learn Core Fundamentals of {s_name}" in existing_completed_titles)
        ))

        # Phase 2: Practical Exercises
        tasks_to_add.append(RoadmapTask(
            roadmap_id=roadmap.id,
            title=f"Complete Practical Hands-on Exercises in {s_name}",
            category=skill_info["category"],
            phase=2,
            description=f"Solve 15-20 guided exercises or coding challenges utilizing {s_name}.",
            priority="High",
            estimated_hours=10,
            resource_url=res.get("docs", "https://github.com/"),
            is_completed=(f"Complete Practical Hands-on Exercises in {s_name}" in existing_completed_titles)
        ))

    # 2. Target Weak Skills (Medium/High Priority)
    for skill_info in gap_data["weak_skills"]:
        s_name = skill_info["skill_name"]
        res = CURATED_RESOURCES.get(s_name, {})

        # Phase 2: Deep Dive Practice
        tasks_to_add.append(RoadmapTask(
            roadmap_id=roadmap.id,
            title=f"Elevate {s_name} from {skill_info['current_proficiency']} to {skill_info['target_proficiency']}",
            category=skill_info["category"],
            phase=2,
            description=f"Work on intermediate to advanced patterns in {s_name}. {skill_info['recommendation_tip']}",
            priority="Medium",
            estimated_hours=6,
            resource_url=res.get("docs", "https://devdocs.io/"),
            is_completed=(f"Elevate {s_name} from {skill_info['current_proficiency']} to {skill_info['target_proficiency']}" in existing_completed_titles)
        ))

    # 3. Phase 3: Mini-Projects (Integrate role skills)
    tasks_to_add.append(RoadmapTask(
        roadmap_id=roadmap.id,
        title=f"Build Capstone Portfolio Project for {job_role.title}",
        category="Project",
        phase=3,
        description=f"Create an end-to-end portfolio project demonstrating your core skills for {job_role.title}. Document the architecture on GitHub with a clean README.",
        priority="High",
        estimated_hours=16,
        resource_url="https://github.com/",
        is_completed=(f"Build Capstone Portfolio Project for {job_role.title}" in existing_completed_titles)
    ))

    # 4. Phase 4: Interview Preparation & Placement Readiness
    tasks_to_add.append(RoadmapTask(
        roadmap_id=roadmap.id,
        title=f"Master Top 50 Technical Interview Questions for {job_role.title}",
        category="Interview",
        phase=4,
        description=f"Review standard technical questions, system design or query writing problems commonly asked by recruiters for {job_role.title} positions.",
        priority="High",
        estimated_hours=8,
        resource_url="https://neetcode.io/",
        is_completed=(f"Master Top 50 Technical Interview Questions for {job_role.title}" in existing_completed_titles)
    ))

    tasks_to_add.append(RoadmapTask(
        roadmap_id=roadmap.id,
        title="Conduct STAR Behavioral & Communication Mock Session",
        category="Soft Skills",
        phase=4,
        description="Prepare structured answers for 'Tell me about yourself', past projects, conflict resolution, and role motivation.",
        priority="Medium",
        estimated_hours=4,
        resource_url="https://www.toastmasters.org/",
        is_completed=("Conduct STAR Behavioral & Communication Mock Session" in existing_completed_titles)
    ))

    db.session.add_all(tasks_to_add)
    db.session.flush()

    # Recalculate completion
    roadmap.recalculate_completion()
    roadmap.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return roadmap
