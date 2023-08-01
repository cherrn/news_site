import os
import smtplib
from email.mime.text import MIMEText


def send_email(message):
    sender = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
        
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    try:
        server.login(sender, password)
        msg = MIMEText(message)
        msg['Subject'] = 'List from site!'
        server.sendmail(sender, 'igorcern3@gmail.com', msg.as_string())

        return 'OK!'
    except Exception as e:
        return f'{e}\nCheck your login or password'


def main():
    message = 'test1'
    print(send_email(message))


if __name__ == '__main__':
    main()
