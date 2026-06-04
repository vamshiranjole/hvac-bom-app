import re
from app.models.schemas import EquipmentItem

def normalize_tag(tag: str) -> str:
    if not tag:
        return ""
    tag = tag.lower().strip()
    tag = re.sub(r"[\s_]+", "-", tag)
    return tag

def assign_review_status(item: EquipmentItem, issues: list) -> str:
    tag = item.equipment_tag or ""
    item_issues = [i for i in issues if i.get("affected_tag") == tag]
    
    high_issues = [i for i in item_issues if i.get("severity") == "high"]
    medium_issues = [i for i in item_issues if i.get("severity") == "medium"]
    
    score = item.confidence_score or 0.0
    
    if score < 0.50 or item.low_confidence:
        return "manual_required"
    elif high_issues or score < 0.70:
        return "needs_review"
    elif score >= 0.70 and not high_issues and len(medium_issues) <= 1:
        return "likely_ok"
    elif score >= 0.85 and not high_issues:
        return "auto_approved"
    return "needs_review"

def build_bom(items: list, issues: list) -> list:
    groups = {}
    
    for item in items:
        key = normalize_tag(item.equipment_tag or "") + "|" + (item.equipment_type or "")
        
        if key not in groups:
            groups[key] = {"item": item, "merged_from": [f"page {item.source_page}"]}
        else:
            existing = groups[key]["item"]
            if (item.confidence_score or 0) > (existing.confidence_score or 0):
                groups[key]["merged_from"].append(f"page {item.source_page}")
                groups[key]["item"] = item
            else:
                groups[key]["merged_from"].append(f"page {item.source_page}")

    bom = []
    for key, group in groups.items():
        item = group["item"]
        merged_from = list(set(group["merged_from"]))
        review_status = assign_review_status(item, issues)
        
        bom_item = item.model_copy(update={
            "equipment_tag": normalize_tag(item.equipment_tag or ""),
        })
        
        bom.append({
            "equipment_tag": bom_item.equipment_tag,
            "equipment_type": bom_item.equipment_type,
            "manufacturer": bom_item.manufacturer,
            "model_number": bom_item.model_number,
            "quantity": bom_item.quantity,
            "capacity": bom_item.capacity,
            "voltage": bom_item.voltage,
            "confidence_score": bom_item.confidence_score,
            "review_status": review_status,
            "merged_from": merged_from,
            "source_page": bom_item.source_page
        })
    
    return bom
