import email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import ssl
import smtplib
import datetime
import logging

class Mail:

    def __init__(self, account="", password=""):
        self.session = None
        self.sender = account
        if account == "":
            try:
                self.session = smtplib.SMTP('localhost')
                self.sender = os.getenv('USER')
            except ConnectionRefusedError as e :
                logging.error("local smtp server not setup for email account %s",account)

        elif "gmail.com" in account :
            context = ssl.SSLContext()
            connection = smtplib.SMTP('smtp.gmail.com', 587)
            connection.ehlo()
            connection.starttls(context=context)
            connection.ehlo()
            connection.login(account, password)
            self.session = connection
            self.sender = account
        else:
            logging.error("unsupport smtp type for email account %s",account)

    def write(self,html, text=""):
        if self.session is None: return
        self.msg = MIMEMultipart("alternative")
        self.msg['From'] = email.utils.formataddr(('FROM', self.sender))
        if html != "" :
            part = MIMEText(html, "html")
            self.msg.attach(part)
        if text != "":
            part = MIMEText(html, "text")
            self.msg.attach(part)

    def attach(self,filename):
        if self.session is None: return
        from email import encoders
        from email.mime.base import MIMEBase

        # Open PDF file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        self.msg.attach(part)

    def send(self,to=[],cc=[],bcc=[], subject='hello', red=False):
        if self.session is None: return
        self.msg['Subject'] = subject

        if to == [] : to = []
        if isinstance(to,str) : to = [to, ]
        if isinstance(cc,str) : cc = [cc, ]
        if isinstance(bcc,str) : bcc = [bcc, ]

        self.msg['To'] = ','.join(to) # email.utils.formataddr(('TO', to))

        if cc != [] :
            self.msg['CC'] = ','.join(cc)

        if red :
            self.msg['X-Priority'] = '1'
            self.msg['X-Message-Flag'] = 'Follow up'
            self.msg['Reply-By'] = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S") # show as RED in outlook!

        #  self.session.send_message(self.msg)
        receiver = to+cc+bcc
        logging.info("sending email from '%s' to %s, cc=%s, bcc=%s",self.sender, to, cc, bcc)
        self.session.sendmail(self.sender, receiver, self.msg.as_string())

if __name__ == '__main__':

    text = 'This is the body of the message.'
    html = """
    <html>
    <body>
    <p>Hi,<br>
    How are you?<br>
    <a href="http://www.realpython.com">Real Python</a>
    has many great tutorials.
    </p>
    </body>
    </html>
    """

    m = Mail()
    m.write(html, text)
    m.attach(__file__)
    m.send('ryan.huan.li+to@gmail.com', 'ryan.huan.li+cc@gmail.com', 'ryan.huan.li+bcc@gmail.com')

else:
    pass
