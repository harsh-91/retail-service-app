import weasyprint
from jinja2 import Environment, FileSystemLoader
import os

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '..', 'templates')

def generate_gst_invoice_pdf(invoice_data: dict, filename: str):
    env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))
    template = env.get_template("gst_invoice.html")
    html = template.render(invoice=invoice_data)
    weasyprint.HTML(string=html).write_pdf(target=filename)
    return filename
