# utils/localization.py

_DEFAULT_MESSAGES = {
    "en": {
        "udhaar_limit_breach": "Customer's credit limit exceeded for this sale.",
        "low_stock_warn": "⚠️ Low stock: {item}",
        "insufficient_stock": "Insufficient stock for {item}, deduction pending (please update inventory).",
        "item_not_in_inventory": "Item not in inventory, stock deduction is pending.",
        "udhaar_not_found": "No open udhaar sale found.",
        "healthy": "healthy"
    }
    # Add other languages as dicts if needed, e.g. "hi", "mr", etc.
}

def get_message(key: str, lang: str, **kwargs):
    txt = _DEFAULT_MESSAGES.get(lang, _DEFAULT_MESSAGES["en"]).get(key, key)
    # .format(**kwargs) for simple var replacements
    try:
        return txt.format(**kwargs)
    except Exception:
        return txt
