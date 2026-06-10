from simple_salesforce import Salesforce

def push_bom_to_salesforce(job_id: str, project_name: str, bom: list, sf_username: str, sf_password: str, sf_token: str, sf_instance_url: str):
    sf = Salesforce(
        username=sf_username,
        password=sf_password,
        security_token=sf_token,
        domain="login"
    )

    opp = sf.Opportunity.create({
        "Name": project_name,
        "StageName": "Needs Analysis",
        "CloseDate": "2026-12-31",
        "Description": f"Extracted from BOM job {job_id}. {len(bom)} items found.",
    })

    opp_id = opp["id"]
    opp_url = f"https://{sf.sf_instance}/lightning/r/Opportunity/{opp_id}/view"

    return {
        "opportunity_id": opp_id,
        "opportunity_url": opp_url,
        "items_pushed": len([i for i in bom if i.get("review_status") in ["auto_approved", "likely_ok"]])
    }
