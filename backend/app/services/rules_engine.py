import re
from app.models.schemas import EquipmentItem

def run_r_rules(items: list) -> list:
    issues = []

    for item in items:
        tag = item.equipment_tag or ""

        # R001: quantity is None
        if item.quantity is None:
            issues.append({
                "rule_id": "R001",
                "severity": "high",
                "message": f"{tag} is missing quantity.",
                "affected_tag": tag
            })

        # R002: quantity <= 0
        if item.quantity is not None:
            try:
                if float(str(item.quantity)) <= 0:
                    issues.append({
                        "rule_id": "R002",
                        "severity": "high",
                        "message": f"{tag} has invalid quantity {item.quantity}.",
                        "affected_tag": tag
                    })
            except:
                pass

        # R003: equipment_tag is None or empty
        if not item.equipment_tag:
            issues.append({
                "rule_id": "R003",
                "severity": "medium",
                "message": "Item has no equipment tag.",
                "affected_tag": None
            })

        # R004: duplicate tags
        tags = [i.equipment_tag for i in items if i.equipment_tag]
        if tags.count(item.equipment_tag) > 1 and item.equipment_tag:
            if not any(i["rule_id"] == "R004" and i["affected_tag"] == tag for i in issues):
                issues.append({
                    "rule_id": "R004",
                    "severity": "high",
                    "message": f"Duplicate tag {tag} found.",
                    "affected_tag": tag
                })

        # R005: voltage pattern check
        valid_voltages = ["120", "208", "240", "277", "460", "480"]
        if item.voltage:
            if not any(v in item.voltage for v in valid_voltages):
                issues.append({
                    "rule_id": "R005",
                    "severity": "medium",
                    "message": f"{tag} has unusual voltage {item.voltage}.",
                    "affected_tag": tag
                })

        # R006: low confidence score
        if item.confidence_score is not None and item.confidence_score < 0.80:
            issues.append({
                "rule_id": "R006",
                "severity": "medium",
                "message": f"{tag} has low confidence score {round(item.confidence_score, 2)}.",
                "affected_tag": tag
            })

        # R007: model_number is None
        if item.model_number is None:
            issues.append({
                "rule_id": "R007",
                "severity": "low",
                "message": f"{tag} is missing model number.",
                "affected_tag": tag
            })

        # R008: manufacturer is None
        if item.manufacturer is None:
            issues.append({
                "rule_id": "R008",
                "severity": "low",
                "message": f"{tag} is missing manufacturer.",
                "affected_tag": tag
            })

    return issues


def run_h_rules(items: list) -> list:
    warnings = []
    tags = [i.equipment_tag for i in items if i.equipment_tag]

    for item in items:
        tag = item.equipment_tag or ""
        eq_type = (item.equipment_type or "").upper()

        # H001: RTU without disconnect
        if "RTU" in tag.upper() and item.voltage:
            warnings.append({
                "rule_id": "H001",
                "message": f"Please verify {tag} has a disconnect switch installed.",
                "affected_tag": tag
            })

        # H002: AHU without filter reference
        if "AHU" in tag.upper():
            warnings.append({
                "rule_id": "H002",
                "message": f"Please confirm filter specification for {tag}.",
                "affected_tag": tag
            })

        # H003: Fan without voltage
        if "FAN" in eq_type and not item.voltage:
            warnings.append({
                "rule_id": "H003",
                "message": f"Please verify voltage for fan unit {tag}.",
                "affected_tag": tag
            })

        # H004: HP without voltage
        if "HP" in tag.upper() and not item.voltage:
            warnings.append({
                "rule_id": "H004",
                "message": f"Please verify voltage for heat pump {tag}.",
                "affected_tag": tag
            })

        # H005: Damper without access door
        if "DAMPER" in eq_type:
            warnings.append({
                "rule_id": "H005",
                "message": f"Please confirm access door for damper {tag}.",
                "affected_tag": tag
            })

    return warnings
