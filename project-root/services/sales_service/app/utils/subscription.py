# utils/subscription.py

import datetime

_fake_tenant_subs = {
    "stub_tenant": {
        "subscription_status": "premium",
        "subscription_end_date": datetime.date(2099, 1, 1)
    }
}

def tenant_is_premium(tenant_id: str) -> bool:
    tenant = _fake_tenant_subs.get(tenant_id)
    if tenant:
        return (
            tenant["subscription_status"] == "premium"
            and tenant["subscription_end_date"] > datetime.date.today()
        )
    return False
