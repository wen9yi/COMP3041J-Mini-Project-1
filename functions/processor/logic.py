import re


def process_event(data):
    """Process a submission payload and return a structured evaluation result."""
    required_fields = ["title", "description", "location", "date", "organiser"]
    if not all(data.get(field) for field in required_fields):
        return {
            "status": "INCOMPLETE",
            "final_status": "INCOMPLETE",
            "category": "GENERAL",
            "assigned_category": "GENERAL",
            "priority": "NORMAL",
            "assigned_priority": "NORMAL",
            "note": "Missing required information."
        }

    if not re.match(r"^\d{4}-\d{2}-\d{2}$", data["date"]):
        return {
            "status": "NEEDS REVISION",
            "final_status": "NEEDS REVISION",
            "category": "GENERAL",
            "assigned_category": "GENERAL",
            "priority": "NORMAL",
            "assigned_priority": "NORMAL",
            "note": "Invalid date format. Use YYYY-MM-DD."
        }

    if len(data["description"]) < 40:
        return {
            "status": "NEEDS REVISION",
            "final_status": "NEEDS REVISION",
            "category": "GENERAL",
            "assigned_category": "GENERAL",
            "priority": "NORMAL",
            "assigned_priority": "NORMAL",
            "note": "Description must be at least 40 characters."
        }

    content = f"{data['title']} {data['description']}".lower()
    if any(keyword in content for keyword in ["career", "internship", "recruitment"]):
        category = "OPPORTUNITY"
    elif any(keyword in content for keyword in ["workshop", "seminar", "lecture"]):
        category = "ACADEMIC"
    elif any(keyword in content for keyword in ["club", "society", "social"]):
        category = "SOCIAL"
    else:
        # 兜底判定：当标题和描述中没有任何分类关键词时，统一设为 GENERAL
        category = "GENERAL"

    priority_map = {
        "OPPORTUNITY": "HIGH",
        "ACADEMIC": "MEDIUM",
        "SOCIAL": "NORMAL",
        "GENERAL": "NORMAL"
    }

    final_status = "APPROVED"
    assigned_priority = priority_map[category]

    return {
        "status": final_status,
        "final_status": final_status,
        "category": category,
        "assigned_category": category,
        "priority": assigned_priority,
        "assigned_priority": assigned_priority,
        "note": "Processing successful."
    }
