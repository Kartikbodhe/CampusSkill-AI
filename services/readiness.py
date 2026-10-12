"""Placement Readiness Calculator for CampusSkill AI.

Computes a transparent, explainable composite readiness score across technical competencies,
aptitude, data structures & algorithms (DSA), communication, and empirical assessment metrics.
"""
from services.skill_gap import analyze_skill_gap


DEFAULT_WEIGHTS = {
    "technical": 0.40,
    "aptitude": 0.20,
    "dsa": 0.20,
    "communication": 0.10,
    "assessment": 0.10,
}


def _score_from_level_or_assessment(student_skills, attempts, skill_names, category_name):
    """
    Helper to calculate component score (0-100) favoring empirical assessment
    over self-reported values.
    """
    # 1. Check empirical assessment attempts for this category
    matching_attempts = [
        att for att in attempts
        if att.assessment and (
            att.assessment.category.lower() == category_name.lower() or
            any(name.lower() in att.assessment.title.lower() for name in skill_names)
        )
    ]
    if matching_attempts:
        # Average of highest attempt scores
        best_score = max(att.score for att in matching_attempts)
        return best_score, False  # verified empirical

    # 2. Check self-reported skills
    skill_level_weights = {"beginner": 35.0, "intermediate": 70.0, "advanced": 95.0}
    matching_skills = [
        ss for ss in student_skills
        if ss.skill and (
            any(name.lower() in ss.skill.name.lower() for name in skill_names) or
            ss.skill.category.lower() == category_name.lower()
        )
    ]

    if matching_skills:
        levels = [skill_level_weights.get(ss.proficiency_level.lower(), 30.0) for ss in matching_skills]
        return round(sum(levels) / len(levels), 1), True  # self-reported provisional

    return 0.0, True  # no data


def calculate_placement_readiness(student_profile, weights=None):
    """
    Calculate explainable placement readiness score.
    
    Formula:
      Composite Score = (Technical * W_tech) + (Aptitude * W_apt) + 
                        (DSA * W_dsa) + (Communication * W_comm) + (Assessments * W_assess)
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    student_skills = student_profile.skills or []
    attempts = student_profile.assessment_attempts or []

    # 1. Technical Score:
    if student_profile.target_job_role:
        gap_res = analyze_skill_gap(student_profile, student_profile.target_job_role)
        technical_score = gap_res["match_percentage"] if gap_res else 0.0
    else:
        # Fallback to general technical skills
        tech_skills = [ss for ss in student_skills if ss.skill.category.lower() in ["programming", "database", "web development", "data science", "technical"]]
        if tech_skills:
            lvl_pts = {"beginner": 40.0, "intermediate": 75.0, "advanced": 95.0}
            technical_score = round(sum(lvl_pts.get(ss.proficiency_level.lower(), 40.0) for ss in tech_skills) / len(tech_skills), 1)
        else:
            technical_score = 0.0

    # 2. Aptitude Score
    aptitude_score, apt_prov = _score_from_level_or_assessment(
        student_skills, attempts, ["Aptitude", "Quantitative", "Logical Reasoning", "Problem Solving"], "Aptitude"
    )

    # 3. DSA Score
    dsa_score, dsa_prov = _score_from_level_or_assessment(
        student_skills, attempts, ["Data Structures", "Algorithms", "DSA"], "DSA"
    )

    # 4. Communication Score
    communication_score, comm_prov = _score_from_level_or_assessment(
        student_skills, attempts, ["Communication", "Verbal", "Soft Skills"], "Communication"
    )

    # 5. Assessment Activity Score (0-100 based on verified tests passed)
    if attempts:
        passed_count = sum(1 for att in attempts if att.passed)
        avg_score = sum(att.score for att in attempts) / len(attempts)
        assessment_score = round(min(100.0, (avg_score * 0.7) + (min(passed_count, 5) * 6)), 1)
    else:
        assessment_score = 0.0

    # Composite weighted readiness score
    overall_score = round(
        (technical_score * weights["technical"]) +
        (aptitude_score * weights["aptitude"]) +
        (dsa_score * weights["dsa"]) +
        (communication_score * weights["communication"]) +
        (assessment_score * weights["assessment"]),
        1
    )

    has_attempts = len(attempts) > 0
    is_provisional = not has_attempts or (apt_prov and dsa_prov and comm_prov)

    # Classification
    if overall_score >= 75.0:
        band = "Placement Ready"
        badge_class = "success"
    elif overall_score >= 50.0:
        band = "Moderate Preparedness"
        badge_class = "warning"
    else:
        band = "Needs Comprehensive Preparation"
        badge_class = "danger"

    return {
        "overall_score": overall_score,
        "band": band,
        "badge_class": badge_class,
        "is_provisional": is_provisional,
        "has_attempts": has_attempts,
        "breakdown": {
            "technical": {
                "score": technical_score,
                "weight_percent": int(weights["technical"] * 100),
                "weighted_contribution": round(technical_score * weights["technical"], 1),
                "label": "Role-Specific Technical Skills",
            },
            "aptitude": {
                "score": aptitude_score,
                "weight_percent": int(weights["aptitude"] * 100),
                "weighted_contribution": round(aptitude_score * weights["aptitude"], 1),
                "label": "Aptitude & Problem Solving",
                "is_provisional": apt_prov,
            },
            "dsa": {
                "score": dsa_score,
                "weight_percent": int(weights["dsa"] * 100),
                "weighted_contribution": round(dsa_score * weights["dsa"], 1),
                "label": "Data Structures & Algorithms",
                "is_provisional": dsa_prov,
            },
            "communication": {
                "score": communication_score,
                "weight_percent": int(weights["communication"] * 100),
                "weighted_contribution": round(communication_score * weights["communication"], 1),
                "label": "Communication & Professional Presence",
                "is_provisional": comm_prov,
            },
            "assessment": {
                "score": assessment_score,
                "weight_percent": int(weights["assessment"] * 100),
                "weighted_contribution": round(assessment_score * weights["assessment"], 1),
                "label": "Verified Practice Test History",
            },
        },
        "disclaimer": "This readiness index is an educational metric calculated from skill gaps and practice performance. It provides guidance and does not guarantee employer hiring decisions.",
    }
