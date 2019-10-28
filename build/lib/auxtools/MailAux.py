import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from .tools import fetch_credentials


class MailAux():

    def __init__(self, mode='local'):

        if mode == 'local':

            self.credentials = fetch_credentials('mail.json', mode=mode)

        else:

            self.credentials = fetch_credentials(
                'credentials/mail.json', mode=mode)

        self.files = []

    def attach_file(self, filename, alias):

        self.files.append({'filename': filename, 'alias': alias})

    def send_mail(self, subject, body, sender_name, sender_mail, to, date=True):

        server = self.credentials['SMTP_SERVER']
        port = self.credentials['SMTP_PORT']
        login = self.credentials['LOGIN']
        password = self.credentials['PASSWORD']
        self.subject = subject

        mail = MIMEMultipart()

        conn = smtplib.SMTP(server, port)
        conn.ehlo()
        conn.starttls()
        conn.ehlo()
        conn.login(login, password)

        # determines current day for mail subject
        today = datetime.datetime.today()
        month_number = int(today.strftime('%m')) - 1
        month_array = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
                       'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
        month = month_array[month_number]
        date_word = str(today.strftime('%d')) + '/' + month

        mail["From"] = '"{}" <{}>'.format(sender_name, sender_mail)
        mail["To"] = to
        subject = '{} | {} | {}'.format(self.subject, sender_name, date_word)

        mail['Subject'] = Header(subject, 'utf-8')

        for f in self.files:

            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(f['filename'], "rb").read())
            encoders.encode_base64(part)

            part.add_header(
                'Content-Disposition', 'attachment; filename="' + f['alias'] + '"')

            mail.attach(part)

        # build message, send mail
        msgText = MIMEText(body, 'html', 'utf-8')

        mail.attach(msgText)

        conn.sendmail(mail["From"], mail["To"].split(','), mail.as_string())

        return True

    def handle_errors(self, subject, array, sender_name, sender_mail, to):

        body = '<b>Errors:</b><br><br>'

        for error in array:

            body += '<br>{}'.format(error)

        self.send_mail(subject, body, sender_name, sender_mail, to)
