import smtplib
from email.mime.text import MIMEText
from datetime import date

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_PASSWORD = "mypassword"

DATE_FORMAT = "%d/%m/%Y"
EMAIL_SPACE = ", "

import ConfigParser
config = ConfigParser.RawConfigParser()
config.read('../config/default.cfg')
SMTP_USERNAME = config.get('Company', 'email')
SMTP_PASSWORD = config.get('Company', 'email_password')
    
def send_email(subject, email_from, email_to, content):
    '''
    email_to is a list of email address
    '''
    
    msg = MIMEText(content)
    msg['Subject'] = subject + " %s" % (date.today().strftime(DATE_FORMAT))
    msg['To'] = EMAIL_SPACE.join(email_to)
    msg['From'] = email_from
    mail = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    mail.starttls()
    mail.login(SMTP_USERNAME, SMTP_PASSWORD)
    mail.sendmail(email_from, email_to, msg.as_string())
    mail.quit()

if __name__=='__main__':
    subject = "Demo"
    email_from = SMTP_USERNAME
    email_to = [SMTP_USERNAME]
    content = "Test Content"
    send_email(subject, email_from, email_to, content)