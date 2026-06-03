AI_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "equipment_list",
        "schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "equipment_tag":  {"type": ["string", "null"]},
                            "equipment_type": {"type": ["string", "null"]},
                            "manufacturer":   {"type": ["string", "null"]},
                            "model_number":   {"type": ["string", "null"]},
                            "quantity":       {"type": ["string", "null"]},
                            "capacity":       {"type": ["string", "null"]},
                            "voltage":        {"type": ["string", "null"]},
                            "low_confidence": {"type": ["boolean", "null"]}
                        },
                        "required": ["equipment_tag","equipment_type","manufacturer","model_number","quantity","capacity","voltage","low_confidence"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["items"],
            "additionalProperties": False
        },
        "strict": True
    }
}
