# -*- coding:utf-8 -*-
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import base64
import smtplib
import os


class MailSender(object):
    _from = None
    _attachments = []

    def __init__(self, smtpSrv, from_address):
        self.smtp = smtplib.SMTP()
        self.smtp.connect(smtpSrv)
        self._from = from_address
        #self._from = 'sale_report@devenvironment_linux'

    def login(self, user, pwd):
        self.smtp.login(user, pwd)

    def add_attachment(self, attfilename, att_type=1):
        '''
            添加附件:
            att_type=1:一般附件
            att_type=2:图片附件，在邮件内显示
        '''
        if att_type == 1:
            att = MIMEText(open(attfilename, 'rb').read(), 'base64', 'utf-8')
            (filepath, filename) = os.path.split(attfilename)
            name_base64 = base64.b64encode(filename.encode('utf-8'))
            name_format = "=?UTF-8?B?" + name_base64.decode() + "?="
            att.add_header(
                'Content-Disposition',
                'attachment',
                filename=name_format)
            # encoders.encode_base64(att)
            self._attachments.append(att)
        elif att_type == 2:
            att = MIMEImage(open(attfilename, 'rb').read())
            att.add_header('Content-ID', '<image1>')
            self._attachments.append(att)

    def send(self, subject, content, to_addr=[]):
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self._from
        msg['To'] = ','.join(to_addr)
        contents = MIMEText(content, "html")
        msg.attach(contents)
        for att in self._attachments:
            msg.attach(att)
        try:
            self.smtp.sendmail(self._from, to_addr, msg.as_string())
            return True
        except Exception as e:
            print(str(e))
            return False

    def close(self):
        self.smtp.quit()


if __name__ == "__main__":
    my_mail_send = MailSender('smtp.wo.com.cn')
    subject = '测试信息'
    content = 'cescsdfsdf'
    receivers = 'zeshan.nb@alibaba-inc.com'
    my_mail_send.login('18651601825@wo.cn', '123qweASD')
    my_mail_send.send(subject, content, receivers)
    my_mail_send.close()
