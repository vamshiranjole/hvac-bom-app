import sys
sys.path.insert(0, "/content/hvac-bom-app/backend")

from app.services.revision_compare import compare_boms

def make_bom_item(**kwargs):
    defaults = {
        "equipment_tag": "rtu-1",
        "equipment_type": "RTU",
        "manufacturer": "Carrier",
        "model_number": "48XP",
        "quantity": 1,
        "capacity": "7.5 ton",
        "voltage": "460V",
        "confidence_score": 0.95,
        "review_status": "auto_approved"
    }
    defaults.update(kwargs)
    return defaults

def test_added_item():
    old_bom = []
    new_bom = [make_bom_item(equipment_tag="rtu-1")]
    changes = compare_boms(old_bom, new_bom)
    assert any(c["change_type"] == "added" and c["equipment_tag"] == "rtu-1" for c in changes)

def test_removed_item():
    old_bom = [make_bom_item(equipment_tag="rtu-1")]
    new_bom = []
    changes = compare_boms(old_bom, new_bom)
    assert any(c["change_type"] == "removed" and c["equipment_tag"] == "rtu-1" for c in changes)

def test_modified_item():
    old_bom = [make_bom_item(equipment_tag="rtu-1", capacity="5 ton")]
    new_bom = [make_bom_item(equipment_tag="rtu-1", capacity="7.5 ton")]
    changes = compare_boms(old_bom, new_bom)
    assert any(c["change_type"] == "modified" and c["field"] == "capacity" for c in changes)

def test_no_changes():
    bom = [make_bom_item(equipment_tag="rtu-1")]
    changes = compare_boms(bom, bom)
    assert changes == []

def test_all_three_change_types():
    old_bom = [
        make_bom_item(equipment_tag="rtu-1", capacity="5 ton"),
        make_bom_item(equipment_tag="ahu-1"),
    ]
    new_bom = [
        make_bom_item(equipment_tag="rtu-1", capacity="7.5 ton"),
        make_bom_item(equipment_tag="vav-1"),
    ]
    changes = compare_boms(old_bom, new_bom)
    types = [c["change_type"] for c in changes]
    assert "added" in types
    assert "removed" in types
    assert "modified" in types
