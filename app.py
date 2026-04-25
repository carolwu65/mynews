from flask import Flask, request, jsonify, send_from_directory
import csv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, timezone

app = Flask(__name__, static_folder='.')

# Path for storing registrations
REGISTRATIONS_FILE = 'registrations.csv'

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # Use environment variable for security

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

def send_cancellation_email(target_email, name):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"2026 未來科技研討會 <{SMTP_EMAIL}>"
        msg['To'] = target_email
        msg['Subject'] = "【取消報名確認】2026 未來科技研討會"

        body = f"""
親愛的 {name} 您好，

這封郵件是為了確認我們已收到您的請求，並已取消您在 2026 未來科技研討會的報名。

如果您之後改變主意，歡迎隨時再次前往官網報名。

期待未來有機會能為您服務！

未來科技研討會 籌備小組 敬上
"""
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Cancellation Error: {e}")
        return False

from email.mime.base import MIMEBase
from email import encoders

def send_csv_to_admin():
    try:
        msg = MIMEMultipart()
        msg['From'] = f"報名系統自動備份 <{SMTP_EMAIL}>"
        msg['To'] = SMTP_EMAIL
        tw_tz = timezone(timedelta(hours=8))
        msg['Subject'] = f"【最新報名清單備份】{datetime.now(tw_tz).strftime('%Y-%m-%d %H:%M')}"

        body = "附件為目前最新的報名清單 CSV 檔案。"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # Attach CSV file
        if os.path.exists(REGISTRATIONS_FILE):
            with open(REGISTRATIONS_FILE, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={REGISTRATIONS_FILE}",
            )
            msg.attach(part)

        # Connect and send
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Admin Backup Error: {e}")
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
        tw_tz = timezone(timedelta(hours=8))
        file_exists = os.path.isfile(REGISTRATIONS_FILE)
        with open(REGISTRATIONS_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Timestamp', 'Name', 'Email', 'Organization', 'TicketType'])
            writer.writerow([datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S"), name, email, org, ticket_type])
        
        # 2. Send Real Email to User
        email_sent = send_confirmation_email(email, name, org, ticket_type)
        
        # 3. Send Backup CSV to Admin
        send_csv_to_admin()
        
        if email_sent:
            msg = "Registration successful and confirmation email sent."
        else:
            msg = "Registration successful but failed to send email."
        
        return jsonify({"status": "success", "message": msg}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/cancel', methods=['POST'])
def cancel_registration():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        
        if not os.path.exists(REGISTRATIONS_FILE):
            return jsonify({"status": "error", "message": "No registrations found."}), 404
        
        found = False
        updated_rows = []
        header = None
        
        with open(REGISTRATIONS_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                # row structure: Timestamp, Name, Email, Organization, TicketType
                if len(row) >= 3 and row[1] == name and row[2] == email:
                    found = True
                    continue
                updated_rows.append(row)
        
        if not found:
            return jsonify({"status": "error", "message": "Matching registration not found."}), 404
            
        with open(REGISTRATIONS_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if header:
                writer.writerow(header)
            writer.writerows(updated_rows)
            
        # Send cancellation email to user
        send_cancellation_email(email, name)
        
        # Send updated CSV to admin
        send_csv_to_admin()
        
        return jsonify({"status": "success", "message": "Registration cancelled successfully."}), 200
    except Exception as e:
        print(f"Cancellation Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask server on http://localhost:8000")
    app.run(port=8000, debug=True)
