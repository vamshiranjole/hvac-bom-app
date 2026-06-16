import sys
sys.path.insert(0, "/content/hvac-bom-app/backend")

from app.models.schemas import EquipmentItem
from app.services.bom_builder import build_bom, normalize_tag, assign_review_status

def make_item(**kwargs):
    defaults = dict(
        equipment_tag="RTU-1",
        equipment_type="RTU",
        manufacturer="Carrier",
        model_number="48XP",
        quantity=1,
        capacity="7.5 ton",
        voltage="460V",
        source_page=1,
        low_confidence=False,
        confidence_score=0.95
    )
    defaults.update(kwargs)
    return EquipmentItem(**defaults)

def test_normalize_tag_lowercase():
    assert normalize_tag("RTU-1") == "rtu-1"

def test_normalize_tag_spaces():
    assert normalize_tag("RTU 1") == "rtu-1"

def test_normalize_tag_underscore():
    assert normalize_tag("RTU_1") == "rtu-1"

def test_duplicates_merged():
    item1 = make_item(equipment_tag="RTU-1", source_page=1, confidence_score=0.90)
    item2 = make_item(equipment_tag="RTU-1", source_page=2, confidence_score=0.70)
    bom = build_bom([item1, item2], [])
    assert len(bom) == 1

def test_different_tags_not_merged():
    item1 = make_item(equipment_tag="RTU-1")
    item2 = make_item(equipment_tag="RTU-2")
    bom = build_bom([item1, item2], [])
    assert len(bom) == 2

def test_status_auto_approved():
    item = make_item(confidence_score=0.95, low_confidence=False)
    status = assign_review_status(item, [])
    assert status in ["auto_approved", "likely_ok"]

def test_status_manual_required_low_score():
    item = make_item(confidence_score=0.40, low_confidence=False)
    status = assign_review_status(item, [])
    assert status == "manual_required"

def test_status_manual_required_low_confidence_flag():
    item = make_item(confidence_score=0.90, low_confidence=True)
    status = assign_review_status(item, [])
    assert status == "manual_required"

def test_status_needs_review_high_issue():
    item = make_item(equipment_tag="RTU-1", confidence_score=0.90, low_confidence=False)
    issues = [{"rule_id": "R001", "severity": "high", "affected_tag": "RTU-1", "message": "missing qty"}]
    status = assign_review_status(item, issues)
    assert status == "needs_review"
