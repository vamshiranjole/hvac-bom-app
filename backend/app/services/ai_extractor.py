import json
import openai
from app.config import settings
from app.models.schemas import EquipmentItem

client = openai.OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

def extract_equipment(page_content: str, source_page: int) -> list:
    prompt = f"""You are reading HVAC equipment schedules.
Extract every piece of equipment from the content below.
Return a JSON object with key "items" as a list.
Each item must have these exact keys:
equipment_tag, equipment_type, manufacturer, model_number, quantity, capacity, voltage, low_confidence

Use null for missing values. Set low_confidence=true if unsure.

Page content:
{page_content}
"""
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}]
        )
        parsed = json.loads(response.choices[0].message.content)
        items = []
        for item in parsed.get("items", []):
            try:
                eq = EquipmentItem(
                    equipment_tag=item.get("equipment_tag"),
                    equipment_type=item.get("equipment_type"),
                    manufacturer=item.get("manufacturer"),
                    model_number=item.get("model_number"),
                    quantity=item.get("quantity"),
                    capacity=item.get("capacity"),
                    voltage=item.get("voltage"),
                    low_confidence=item.get("low_confidence", False),
                    source_page=source_page
                )
                items.append(eq)
            except Exception as ex:
                print(f"Item parse error: {ex}")
                continue
        return items
    except Exception as e:
        print(f"AI extraction error on page {source_page}: {e}")
        return []
