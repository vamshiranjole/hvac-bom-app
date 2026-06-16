import sys
sys.path.insert(0, "/content/hvac-bom-app/backend")

from app.models.schemas import EquipmentItem
from app.services.rules_engine import run_r_rules, run_h_rules

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

def test_r001_missing_quantity():
    item = make_item(quantity=None)
    issues = run_r_rules([item])
    assert any(i["rule_id"] == "R001" for i in issues)

def test_r001_no_trigger():
    item = make_item(quantity=2)
    issues = run_r_rules([item])
    assert not any(i["rule_id"] == "R001" for i in issues)

def test_r002_zero_quantity():
    item = make_item(quantity=0)
    issues = run_r_rules([item])
    assert any(i["rule_id"] == "R002" for i in issues)

def test_r002_no_trigger():
    item = make_item(quantity=1)
    issues = run_r_rules([item])
    assert not any(i["rule_id"] == "R002" for i in issues)

def test_r003_missing_tag():
    item = make_item(equipment_tag=None)
    issues = run_r_rules([item])
    assert any(i["rule_id"] == "R003" for i in issues)

def test_r003_no_trigger():
    item = make_item(equipment_tag="RTU-1")
    issues = run_r_rules([item])
    assert not any(i["rule_id"] == "R003" for i in issues)

def test_r004_duplicate_tags():
    item1 = make_item(equipment_tag="RTU-1")
    item2 = make_item(equipment_tag="RTU-1")
    issues = run_r_rules([item1, item2])
    assert any(i["rule_id"] == "R004" for i in issues)

def test_r004_no_trigger():
    item1 = make_item(equipment_tag="RTU-1")
    item2 = make_item(equipment_tag="RTU-2")
    issues = run_r_rules([item1, item2])
    assert not any(i["rule_id"] == "R004" for i in issues)

def test_r005_bad_voltage():
    item = make_item(voltage="999V")
    issues = run_r_rules([item])
    assert any(i["rule_id"] == "R005" for i in issues)

def test_r005_no_trigger():
    item = make_item(voltage="460V")
    issues = run_r_rules([item])
    assert not any(i["rule_id"] == "R005" for i in issues)

def test_r006_low_confidence():
    item = make_item(confidence_score=0.50)
    issues = run_r_rules([item])
    assert any(i["rule_id"] == "R006" for i in issues)

def test_r006_no_trigger():
    item = make_item(confidence_score=0.95)
    issues = run_r_rules([item])
    assert not any(i["rule_id"] == "R006" for i in issues)

def test_r007_missing_model():
    item = make_item(model_number=None)
    issues = run_r_rules([item])
    assert any(i["rule_id"] == "R007" for i in issues)

def test_r007_no_trigger():
    item = make_item(model_number="48XP")
    issues = run_r_rules([item])
    assert not any(i["rule_id"] == "R007" for i in issues)

def test_r008_missing_manufacturer():
    item = make_item(manufacturer=None)
    issues = run_r_rules([item])
    assert any(i["rule_id"] == "R008" for i in issues)

def test_r008_no_trigger():
    item = make_item(manufacturer="Carrier")
    issues = run_r_rules([item])
    assert not any(i["rule_id"] == "R008" for i in issues)

def test_h001_rtu_disconnect():
    item = make_item(equipment_tag="RTU-1", voltage="460V")
    warnings = run_h_rules([item])
    assert any(w["rule_id"] == "H001" for w in warnings)

def test_h002_ahu_filter():
    item = make_item(equipment_tag="AHU-1")
    warnings = run_h_rules([item])
    assert any(w["rule_id"] == "H002" for w in warnings)

def test_h_rules_advisory_wording():
    item = make_item(equipment_tag="RTU-1", voltage="460V")
    warnings = run_h_rules([item])
    for w in warnings:
        msg = w["message"].lower()
        assert "verify" in msg or "confirm" in msg
