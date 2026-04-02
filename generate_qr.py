import qrcode

def generate_qr(ticket_id):
    path = f"static/qr_codes/{ticket_id}.png"
    img = qrcode.make(ticket_id)
    img.save(path)
    return path