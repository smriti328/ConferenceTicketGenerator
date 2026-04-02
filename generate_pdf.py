from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet

def create_ticket_pdf(name, event, ticket_id, qr_path):
    path = f"static/tickets/{ticket_id}.pdf"
    doc = SimpleDocTemplate(path)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph(f"Name: {name}", styles['Normal']))
    elements.append(Paragraph(f"Event: {event}", styles['Normal']))
    elements.append(Paragraph(f"Ticket ID: {ticket_id}", styles['Normal']))
    elements.append(Image(qr_path, width=150, height=150))

    doc.build(elements)
    return path