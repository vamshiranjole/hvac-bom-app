import sys
sys.path.insert(0, "/content/hvac-bom-app/backend")

import json
from app.models.schemas import EquipmentItem
from app.services.ai_extractor import calculate_confidence

FIXTURE_PATH = "/content/hvac-bom-app/backend/tests/fixtures/sample_ai_response.json"

def test_fixture_loads():
    with open(FIXTURE_PATH) as f:
        data = json.load(f)
    assert "items" in data
    assert len(data["items"]) > 0

def test_fixture_parses_to_equipment_items():
    with open(FIXTURE_PATH) as f:
        data = json.load(f)
    items = []
    for item in data["items"]:
        eq = EquipmentItem(
            equipment_tag=item.get("equipment_tag"),
            equipment_type=item.get("equipment_type"),
            manufacturer=item.get("manufacturer"),
            model_number=item.get("model_number"),
            quantity=item.get("quantity"),
            capacity=item.get("capacity"),
            voltage=item.get("voltage"),
            low_confidence=item.get("low_confidence", False),
            source_page=1
        )
        items.append(eq)
    assert len(items) == 2
    assert items[0].equipment_tag == "RTU-1"

def test_confidence_full_item():
    item = EquipmentItem(
        equipment_tag="RTU-1", equipment_type="RTU", manufacturer="Carrier",
        model_number="48XP", quantity=1, capacity="7.5 ton", voltage="460V",
        source_page=1, low_confidence=False
    )
    score = calculate_confidence(item)
    assert score == 1.0

def test_confidence_empty_item():
    item = EquipmentItem(source_page=1, low_confidence=False)
    score = calculate_confidence(item)
    assert score == 0.25

def test_confidence_low_confidence_flag():
    item = EquipmentItem(
        equipment_tag="RTU-1", equipment_type="RTU", manufacturer="Carrier",
        model_number="48XP", quantity=1, capacity="7.5 ton", voltage="460V",
        source_page=1, low_confidence=True
    )
    score = calculate_confidence(item)
    assert score == 0.75
