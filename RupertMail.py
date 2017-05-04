## Allow Rupert to send email

import smtplib

def sendEmailToAdmin(subject, message):
    sender = 'no-reply@rupert.io'
    receivers = ['LUKE@REBELSCUM.COM']

    from_str = "From: Rupert <%s> \n" % (sender)
    to_str = "To: Luke Skywalker <LUKE@REBELSCUM.COM> \n"
    sub_str = "Subject: %s \n" % (subject)
    content = from_str + to_str + sub_str + message

    try:
        smtpObj = smtplib.SMTP('smtp.ilait.se', 587)
        smtpObj.starttls()
        smtpObj.login('EMAIL_USERNAME', 'EMAIL_PASSWORD')
        smtpObj.sendmail(sender, receivers, content)
        smtpObj.quit()

    # TODO: Setup proper exeption hanlding
    except SMTPException:
       pass
