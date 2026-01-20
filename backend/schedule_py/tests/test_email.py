import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.yandex.ru")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

print(f"📧 Отправка с {SMTP_USER}")

try:
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = SMTP_USER  # Отправляем себе
    msg["Subject"] = "Тест уведомлений"

    body = "Это тестовое сообщение от системы расписания. Если вы его видите - всё работает!"
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

    print("✅ Email отправлен успешно!")
except Exception as e:
    print(f"❌ Ошибка: {e}")
