from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3, uuid, os
import razorpay
from utils.generate_qr import generate_qr
from utils.generate_pdf import create_ticket_pdf
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- EMAIL CONFIG ----------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'yourgmail@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_app_password'
app.config['MAIL_USE_TLS'] = True

mail = Mail(app)

# ---------- RAZORPAY ----------
RAZORPAY_KEY_ID = "your_key_id"
RAZORPAY_SECRET = "your_secret"
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_SECRET))

# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect("database.db")

# ---------- HOME ----------
@app.route('/')
def home():
    return render_template("index.html")

# ---------- REGISTER ----------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        conn.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)",
                     (name,email,password))
        conn.commit()
        return redirect('/login')

    return render_template("register.html")

# ---------- LOGIN ----------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email,password)
        ).fetchone()

        if user:
            session['user_id'] = user[0]
            session['name'] = user[1]
            session['email'] = user[2]
            return redirect('/dashboard')

    return render_template("login.html")

# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()
    tickets = conn.execute(
        "SELECT event_name, ticket_id, qr_code FROM tickets WHERE user_id=?",
        (session['user_id'],)
    ).fetchall()

    return render_template("dashboard.html", tickets=tickets)

# ---------- PAYMENT ----------
@app.route('/pay', methods=['POST'])
def pay():
    if 'user_id' not in session:
        return redirect('/login')

    event = request.form.get('event')

    if not event:
        return "❌ Event name missing (fix form input)"

    amount = 50000

    payment = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    return render_template(
        "payment.html",
        order_id=payment['id'],
        amount=amount,
        key_id=RAZORPAY_KEY_ID,
        event=event
    )

# ---------- SUCCESS + EMAIL ----------
@app.route('/success', methods=['POST'])
def success():
    if 'user_id' not in session:
        return redirect('/login')

    event = request.form['event']
    ticket_id = str(uuid.uuid4())[:8]

    qr_path = generate_qr(ticket_id)
    pdf_path = create_ticket_pdf(session['name'], event, ticket_id, qr_path)

    conn = get_db()
    conn.execute(
        "INSERT INTO tickets (user_id,event_name,ticket_id,qr_code,pdf) VALUES (?,?,?,?,?)",
        (session['user_id'], event, ticket_id, qr_path, pdf_path)
    )
    conn.commit()

    # EMAIL
    msg = Message(
        subject="🎟️ Your Ticket",
        sender=app.config['MAIL_USERNAME'],
        recipients=[session['email']]
    )

    msg.body = f"""
Hello {session['name']},
Your ticket for {event} is confirmed.

Ticket ID: {ticket_id}
"""

    with app.open_resource(pdf_path) as f:
        msg.attach("ticket.pdf", "application/pdf", f.read())

    mail.send(msg)

    return send_file(pdf_path, as_attachment=True)

# ---------- DOWNLOAD ----------
@app.route('/download/<ticket_id>')
def download(ticket_id):
    conn = get_db()
    ticket = conn.execute(
        "SELECT pdf FROM tickets WHERE ticket_id=?",
        (ticket_id,)
    ).fetchone()

    if ticket:
        return send_file(ticket[0], as_attachment=True)

    return "Not found"

# ---------- ADMIN ----------
@app.route('/admin')
def admin():
    conn = get_db()
    users = conn.execute("SELECT * FROM users").fetchall()
    tickets = conn.execute("SELECT * FROM tickets").fetchall()
    return render_template("admin.html", users=users, tickets=tickets)

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------- RUN ----------
if __name__ == "__main__":
    os.makedirs("static/qr_codes", exist_ok=True)
    os.makedirs("static/tickets", exist_ok=True)
    app.run(debug=True)