"""Skill Gap Analysis Engine for CampusSkill AI.

Deterministic, explainable rule-based engine that compares student competencies
with target role requirements and computes weighted gap scores.
"""
from models.skills import StudentSkill
from models.jobs import JobRole, JobRoleSkill


def analyze_skill_gap(student_profile, job_role):
    """
    Perform deep gap analysis between a student and a job role.
    
    Returns:
        dict: Complete structured analysis including scores, categorized skills,
              gap explanations, and actionable recommendations.
    """
    if not job_role:
        return None

    # Map student's current skills by skill_id
    student_skills_map = {
        ss.skill_id: ss
        for ss in student_profile.skills
    }

    role_skills = job_role.role_skills

    total_possible_weight = 0
    earned_weight = 0

    missing_skills = []
    weak_skills = []
    proficient_skills = []

    level_map = {"beginner": 1, "intermediate": 2, "advanced": 3}

    for rs in role_skills:
        skill = rs.skill
        importance = rs.importance_weight  # 1 (Good-to-have), 2 (Important), 3 (Critical)
        target_num = rs.numeric_target
        max_component = importance * target_num
        total_possible_weight += max_component

        student_ss = student_skills_map.get(skill.id)
        current_level_str = student_ss.proficiency_level.lower() if student_ss else "not_learned"
        current_num = level_map.get(current_level_str, 0)
        
        # Earned component capped at target requirement
        capped_num = min(current_num, target_num)
        earned_weight += (importance * capped_num)

        gap_value = target_num - current_num

        skill_info = {
            "skill_id": skill.id,
            "skill_name": skill.name,
            "category": skill.category,
            "importance_weight": importance,
            "target_proficiency": rs.min_proficiency.capitalize(),
            "current_proficiency": current_level_str.capitalize() if student_ss else "Not Learned",
            "is_required": rs.is_required,
            "gap_value": gap_value,
            "recommendation_tip": rs.recommendation_tip or f"Focus on {skill.name} practice.",
            "assessment_score": student_ss.assessment_score if student_ss else None,
            "verified": student_ss.verified if student_ss else False,
        }

        if current_num == 0:
            skill_info["status"] = "Missing"
            skill_info["status_badge"] = "danger"
            skill_info["priority"] = "High Priority" if importance >= 2 else "Medium Priority"
            missing_skills.append(skill_info)
        elif current_num < target_num:
            skill_info["status"] = "Needs Improvement"
            skill_info["status_badge"] = "warning"
            skill_info["priority"] = "High Priority" if importance == 3 else "Medium Priority"
            weak_skills.append(skill_info)
        else:
            skill_info["status"] = "Proficient"
            skill_info["status_badge"] = "success"
            skill_info["priority"] = "Maintain & Sharpen"
            proficient_skills.append(skill_info)

    # Calculate match percentage
    if total_possible_weight > 0:
        match_percentage = round((earned_weight / total_possible_weight) * 100.0, 1)
    else:
        match_percentage = 0.0

    # Categorize overall status
    if match_percentage >= 80.0:
        readiness_status = "High Match — Placement Ready"
        readiness_class = "success"
    elif match_percentage >= 50.0:
        readiness_status = "Moderate Match — Actionable Gap"
        readiness_class = "warning"
    else:
        readiness_status = "Significant Skill Gap — Roadmap Recommended"
        readiness_class = "danger"

    # Identify any additional skills the student holds
    role_skill_ids = {rs.skill_id for rs in role_skills}
    extra_skills = [
        {
            "skill_name": ss.skill.name,
            "category": ss.skill.category,
            "level": ss.proficiency_level.capitalize()
        }
        for ss in student_profile.skills
        if ss.skill_id not in role_skill_ids
    ]

    return {
        "job_role": job_role,
        "match_percentage": match_percentage,
        "earned_weight": earned_weight,
        "total_possible_weight": total_possible_weight,
        "readiness_status": readiness_status,
        "readiness_class": readiness_class,
        "missing_skills": missing_skills,
        "weak_skills": weak_skills,
        "proficient_skills": proficient_skills,
        "extra_skills": extra_skills,
        "total_required_skills": len(role_skills),
        "missing_count": len(missing_skills),
        "weak_count": len(weak_skills),
        "proficient_count": len(proficient_skills),
    }
