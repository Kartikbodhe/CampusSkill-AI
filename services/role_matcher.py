"""Job Role Matcher Service for CampusSkill AI.

Scans the job-role catalog to identify and rank roles best aligned
with a student's current skill profile.
"""
from models.jobs import JobRole
from services.skill_gap import analyze_skill_gap


def recommend_matching_roles(student_profile, limit=5):
    """
    Evaluate student skills against all available job roles and rank them by match percentage.
    """
    job_roles = JobRole.query.all()
    matches = []

    for role in job_roles:
        analysis = analyze_skill_gap(student_profile, role)
        if analysis:
            matches.append({
                "role": role,
                "match_percentage": analysis["match_percentage"],
                "missing_count": analysis["missing_count"],
                "weak_count": analysis["weak_count"],
                "proficient_count": analysis["proficient_count"],
                "readiness_status": analysis["readiness_status"],
                "readiness_class": analysis["readiness_class"],
                "is_current_target": (student_profile.target_job_role_id == role.id),
            })

    # Sort descending by match percentage, then ascending by missing count
    matches.sort(key=lambda x: (x["match_percentage"], -x["missing_count"]), reverse=True)
    return matches[:limit]
