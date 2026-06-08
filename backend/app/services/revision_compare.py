from app.services.bom_builder import normalize_tag

COMPARE_FIELDS = ["manufacturer", "model_number", "capacity", "voltage", "quantity"]

def compare_boms(old_bom: list, new_bom: list) -> list:
    old_map = {normalize_tag(item["equipment_tag"]): item for item in old_bom if item.get("equipment_tag")}
    new_map = {normalize_tag(item["equipment_tag"]): item for item in new_bom if item.get("equipment_tag")}

    changes = []

    for tag, item in new_map.items():
        if tag not in old_map:
            changes.append({
                "change_type": "added",
                "equipment_tag": tag,
                "field": None,
                "old_value": None,
                "new_value": item
            })

    for tag, item in old_map.items():
        if tag not in new_map:
            changes.append({
                "change_type": "removed",
                "equipment_tag": tag,
                "field": None,
                "old_value": item,
                "new_value": None
            })

    for tag in old_map:
        if tag in new_map:
            old_item = old_map[tag]
            new_item = new_map[tag]
            for field in COMPARE_FIELDS:
                old_val = old_item.get(field)
                new_val = new_item.get(field)
                if str(old_val) != str(new_val):
                    changes.append({
                        "change_type": "modified",
                        "equipment_tag": tag,
                        "field": field,
                        "old_value": old_val,
                        "new_value": new_val
                    })

    return changes
