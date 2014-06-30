#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import urllib.request as urllib2
except:
    import urllib2
import hashlib

def checkIndexPage ():
    import os

    # Remote gets the index page
    index_html = urllib2.urlopen ("http://www.xi-peng.com/index.html")
    remote_content = index_html.read ()

    return hashlib.md5 (remote_content).hexdigest () == r"39c014834553073ac72cde7a0912211b"

def sendWarningEmail ():
    import email
    
    sender = 'hyq@c3p-group.com'
    recipients = ['hyq@c3p-group.com']

    msg = email.mime.text. MIMEText (u'HYQ: Xi-peng.com 主页已被修改', 'plain', 'utf-8')
    msg['Subject'] = u'Xi-peng.com 主页已被修改'
    msg['From'] = sender
    msg['To'] = u', '.join (recipients)
    
    s = smtplib.SMTP ('localhost')
    s.sendmail (sender, recipients, msg.as_string ())
    s.quit ()

def main ():
    if not checkIndexPage ():
        sendWarningEmail ()

if __name__ == "__main__":
    main ()

