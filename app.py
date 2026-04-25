from flask import Flask, request, jsonify, send_from_directory
import csv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = Flask(__name__, static_folder='.')

# Path for storing registrations
REGISTRATIONS_FILE = 'registrations.csv'

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "carolwu.bost@gmail.com"
SMTP_PASSWORD = "zhfl odak rlej hsuo"  # App Password

def send_confirmation_email(target_email, name, org, ticket_type):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"2026 未來科技研討會 <{SMTP_EMAIL}>"
        msg['To'] = target_email
        msg['Subject'] = "【報名成功確認】2026 未來科技研討會"

        body = f"""
親愛的 {name} 您好，

感謝您報名 2026 未來科技研討會！我們已收到您的報名資訊。

【報名明細】
-----------------------------------------
姓名：{name}
單位：{org}
票種：{ticket_type}
日期：2026 年 5 月 15-16 日
地點：台北國際會議中心 (TICC)
-----------------------------------------

請保留此郵件作為報名憑證。我們期待與您見面！

未來科技研討會 籌備小組 敬上
"""
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # Connect and send
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

# Ensure the static folders exist (assets)
if not os.path.exists('assets'):
    os.makedirs('assets')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def style():
    return send_from_directory('.', 'style.css')

@app.route('/main.js')
def main_js():
    return send_from_directory('.', 'main.js')

@app.route('/assets/<path:path>')
def send_assets(path):
    return send_from_directory('assets', path)

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        org = data.get('org')
        ticket_type = data.get('type')
        
        # 1. Save to CSV
        file_exists = os.path.isfile(REGISTRATIONS_FILE)
        with open(REGISTRATIONS_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Timestamp', 'Name', 'Email', 'Organization', 'TicketType'])
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, email, org, ticket_type])
        
        # 2. Send Real Email
        email_sent = send_confirmation_email(email, name, org, ticket_type)
        
        if email_sent:
            print(f"SUCCESS: Real email sent to {email}")
            msg = "Registration successful and confirmation email sent."
        else:
            print(f"WARNING: Data saved but email failed to send to {email}")
            msg = "Registration successful but failed to send email."
        
        return jsonify({"status": "success", "message": msg}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask server on http://localhost:8000")
    app.run(port=8000, debug=True)
