# utils/payment.py

def create_upi_payment(sale_id):
    return {
        "uri": f"upi://pay?pa=stub@upi&pn=ShopName&mc=123456&tid={sale_id}&tr=txnid",
        "qr": "stub_qr_data"
    }

def handle_payment_webhook(payload: dict):
    # Here you process webhook/callbacks from Razorpay or other providers.
    # For stub, just return success.
    return {"status": "ok"}
