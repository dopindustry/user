from flask import Flask, request, redirect, session, flash, render_template_string
import random
import smtplib
from email.mime.text import MIMEText
import os
import os


app = Flask(__name__)
app.secret_key =  os.urandom(24)

from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Get the environment variables
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

FIXED_AMOUNT = "ask them"

def generate_otp():
    return ''.join(random.choices('0123456789', k=4))

def send_email(to, subject, html_body):
    msg = MIMEText(html_body, "html")
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = to
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cedarville+Cursive&family=EB+Garamond:ital,wght@0,400..800;1,400..800&family=IBM+Plex+Serif:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;1,100;1,200;1,300;1,400;1,500;1,600;1,700&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>User Verification</title>
  <style>
    body {
      background-image: url("https://i.postimg.cc/bwjbGrZq/noise.gif");
      margin: 0;
      font-family: "EB Garamond", serif;
      background-color: #121212;
      color: #f2f2f2;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
    }
    .container {
      background-size: cover;
      background-position: center;
      width: 87%;
      max-width: 500px;
      background: #414141cb;;
      padding: 20px;
      border-radius: 16px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.5);
      position: relative;
    }
    h2 {
      text-align: center;
      margin-bottom: 20px;
      font-family: "Playfair Display", serif;
    }
    img.logo {
      display: block;
      margin: 0 auto 15px auto;
      width: 100px;
      height: auto;
      border-radius: 20px;
      align-item:left;
    }
    input, button, textarea {
      width: 90%;
      padding: 12px;
      margin-top: 10px;
      border: none;
      border-radius: 12px;
      background-color: #2a2a2a;
      color: white;
      font-size: 16px;
    font-family: "EB Garamond", serif;
    }
    button {
      margin-left:10px;
      border-radius:40px;
      background-color: #ffffff;
      font-weight: bold;
      cursor: pointer;
      transition: background 0.2s, opacity 0.3s;
    }
    input:focus, textarea:focus {
      outline: none;
      background-color: #333;
    }
    button:hover {
      background-color: #bebebe;
    }
    .alert {
      background: #333;
      padding: 10px;
      border-left: 5px solid #ffffff;
      border-radius: 10px;
      margin-bottom: 20px;
    }
    .invalid {
      border:none;
    }
    textarea {
      resize: vertical;
      min-height: 100px;
    }
    .disabled {
      opacity: 0.4;
      pointer-events: none;
    }
  </style>
  <script>
    function validateInputs() {
      const numberInput = document.querySelector('input[name="number"]');
      const messageBox = document.querySelector('textarea[name="usermsg"]');
      const submitBtn = document.getElementById('submit-btn');

      let isValid = true;

      if (numberInput && numberInput.value.length < 10) {
        numberInput.classList.add("invalid");
        isValid = false;
      } else if (numberInput) {
        numberInput.classList.remove("invalid");
      }

      if (messageBox && messageBox.value.length > 600) {
        messageBox.classList.add("invalid");
        isValid = false;
      } else if (messageBox) {
        messageBox.classList.remove("invalid");
      }

      if (submitBtn) {
        submitBtn.classList.toggle("disabled", !isValid);
      }
    }

    document.addEventListener("DOMContentLoaded", () => {
      const inputs = document.querySelectorAll("input, textarea");
      inputs.forEach(input => input.addEventListener("input", validateInputs));
      validateInputs();
    });
  </script>
</head>
<body>

  <div class="container">
    <img class="logo" src="https://i.postimg.cc/Kz9rB2dJ/dop.png" >
    <h2>User Verification</h2>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <div class="alert">
          {% for message in messages %}
            <p>{{ message }}</p>
          {% endfor %}
        </div>
      {% endif %}
    {% endwith %}

    {% if not session.get('otp_sent') %}
    <form method="post">
      <input type="text" name="name" placeholder="Full Name" required>
      <input type="email" name="gmail" placeholder="Email Address" required>
      <input type="text" name="number" placeholder="Mobile Number" required>
      <textarea name="usermsg" placeholder="Short message (less than 600 letters)"></textarea>
      <input type="hidden" name="fix" value="{{ fix }}">
      <button type="submit">Send OTP to Mail</button>
    </form>
    {% elif session.get('otp_sent') and not session.get('verified') %}
    <form method="post" action="/verify">
      <input type="text" name="otp_input" placeholder="Enter OTP" required>
      <button type="submit">Verify OTP</button>
    </form>
    {% elif session.get('verified') and not session.get('submitted') %}
    <form method="post" action="/submit">
      <button type="submit" id="submit-btn">Submit Details</button>
    </form>
    {% elif session.get('submitted') %}
    <p style="text-align:center;">Thank you.</p>
    {% endif %}
  </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        gmail = request.form['gmail']
        number = request.form['number']
        usermsg = request.form.get('usermsg', '')
        otp = generate_otp()

        session.update({
            'otp': otp,
            'name': name,
            'gmail': gmail,
            'number': number,
            'usermsg': usermsg,
            'fix': FIXED_AMOUNT,
            'otp_sent': True
        })

        otp_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background:#f9f9f9; padding:20px;">
          <div style="max-width:600px; margin:auto; background:white; border-radius:10px; padding:20px; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
            <h2 style="text-align:center; color:black;">Email Verification From DOP</h2>
            <p>Hello <strong>{name}</strong>,</p>
            <p>Use the OTP below to verify your email:</p>
            <div style="text-align:center; margin:30px 0;">
              <span style="font-size:30px; font-weight:bold; background:#f0f0f0; padding:15px 30px; border-radius:10px; letter-spacing:6px;">
                {otp}
              </span>
            </div>
            <p style="font-size:14px;">If you didn't request this, please ignore this email.</p>
          </div>
        </body>
        </html>
        """

        send_email(gmail, "Your OTP Verification Code", otp_html)
        flash("OTP sent to your email.")
        return redirect('/')

    return render_template_string(HTML_TEMPLATE, fix=FIXED_AMOUNT)

@app.route('/verify', methods=['POST'])
def verify():
    if request.form['otp_input'] == session.get('otp'):
        session['verified'] = True
        flash("OTP verified successfully.")
    else:
        flash("Incorrect OTP.")
    return redirect('/')

@app.route('/submit', methods=['POST'])
def submit():
    if not session.get('verified'):
        flash("OTP not verified.")
        return redirect('/')

    session['submitted'] = True

    body_html = f"""
    <html>
    <body style="font-family:Arial, sans-serif; padding:20px;">
      <h2>New User Submission</h2>
      <p><strong>Name:</strong> {session.get('name')}</p>
      <p><strong>Email:</strong> {session.get('gmail')}</p>
      <p><strong>Phone:</strong> {session.get('number')}</p>
      <p><strong>Fix:</strong> {session.get('fix')} Rs</p>
      <p><strong>Message:</strong><br>{session.get('usermsg')}</p>
    </body>
    </html>
    """

    send_email(SENDER_EMAIL, "New User Submission", body_html)
    flash("Submission successful. Our team will contact you soon.")
    return redirect('/')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

