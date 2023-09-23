import io
import csv
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from config import settings


def convert_dict_to_csv(data: dict):
    csv_buffer = io.StringIO()
    csv_writer = csv.DictWriter(csv_buffer, fieldnames=data[0].keys())
    csv_writer.writeheader()
    csv_writer.writerows(data)
    return csv_buffer.getvalue()


def send_email(email, subject, message, csv_data=None):
    smtp_obj = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
    smtp_obj.set_debuglevel(settings.SMTP_DEBUG)
    smtp_obj.login(settings.MAIL_LOGIN, settings.MAIL_PASSWORD)

    msg = MIMEMultipart()
    msg['From'] = settings.MAIL_LOGIN
    msg['To'] = email
    msg['Subject'] = subject
    message_text = message
    msg.attach(MIMEText(message_text, 'plain', 'utf-8'))

    if csv_data:
        csv_attachment = MIMEApplication(csv_data.encode('utf-8'), _subtype='csv')
        csv_attachment.add_header('content-disposition', 'attachment', filename='NewsLetter.csv')
        msg.attach(csv_attachment)

    smtp_obj.sendmail(from_addr=settings.MAIL_LOGIN, to_addrs=[email], msg=msg.as_string())
    smtp_obj.quit()


def send_code_email(email, code):
    subject = 'Авторизация в ТГ боте'
    message = f'Ваш код для авторизации в OpenGrab-боте: {code}'
    send_email(email, subject, message)


def send_news_letter_email(email, news_letter):
    subject = 'Рассылка по вашему запросу'
    message = f'Рассылка по вашему запросу'
    send_email(email, subject, message, csv_data=convert_dict_to_csv(news_letter))