def send_whatsapp_invoice(phone: str, pdf_url: str, invoice_no: str):
    # In real world: integrate with WhatsApp Business API, Twilio, Gupshup, etc.
    print(f"WhatsApp sent to {phone}: Invoice {invoice_no} Download {pdf_url}")
    # You can add logging, webhook confirmation, or retry here.
