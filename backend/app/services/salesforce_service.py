from simple_salesforce import Salesforce

def push_bom_to_salesforce(job_id: str, project_name: str, bom: list, sf_username: str, sf_password: str, sf_token: str, sf_instance_url: str):
    sf = Salesforce(
        username=sf_username,
        password=sf_password,
        security_token=sf_token,
        instance_url=sf_instance_url
    )

    opp = sf.Opportunity.create({
        "Name": project_name,
        "StageName": "Needs Analysis",
        "CloseDate": "2026-12-31",
        "Description": f"Extracted from BOM job {job_id}. {len(bom)} items found.",
    })

    opp_id = opp["id"]
    opp_url = f"{sf_instance_url}/lightning/r/Opportunity/{opp_id}/view"

    line_items = []
    for item in bom:
        if item.get("review_status") not in ["auto_approved", "likely_ok"]:
            continue
        try:
            line_items.append(sf.OpportunityLineItem.create({
                "OpportunityId": opp_id,
                "Quantity": 1,
                "UnitPrice": 0.0,
                "Description": f'{item.get("manufacturer") or ""} {item.get("model_number") or ""}',
                "Name": item.get("equipment_type") or "Unknown Equipment",
            }))
        except:
            continue

    return {
        "opportunity_id": opp_id,
        "opportunity_url": opp_url,
        "items_pushed": len(line_items)
    }
