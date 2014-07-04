#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import urllib.request as urllib2
except:
    import urllib2
import ftplib
import hashlib
import tempfile
import os

RETRY_TIMES = 10
verbose = False

def getopts ():
    import getopt, sys

    try:
        opts, args = getopt.getopt (sys.argv[1:], "h", ["help", "srcdir=", "ftpserver=", "ftpuser=", "ftppasswd=", "sendmail"])
    except getopt.GetoptError as err:
        # Print help information and exit:
        print str (err) # Will print something like "option -a not recognized."
        sys.exit (2)

    sendmail = False
    ftpserver = None
    ftpuser = None
    ftppasswd = None

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            sys.exit ()
        elif opt in ("--srcdir"):
            src_dir = arg
        elif opt in ("--ftpserver"):
            ftpserver  = arg
        elif opt in ("--ftpuser"):
            ftpuser = arg
        elif opt in ("--ftppasswd"):
            ftppasswd = arg
        elif opt in ("--sendmail"):
            sendmail = True
        else:
            assert False, "Unhandled option"

    return (src_dir, ftpserver, ftpuser, ftppasswd, sendmail)

def checkIndexPage (src_dir):
    # Remote gets the index page
    index_html = urllib2.urlopen ("http://www.xi-peng.com/index.html")
    remote_content = index_html.read ()

    # Gets the local source index page
    local_content = None
    with open (os.path.join (src_dir, 'index.html'), mode='rb') as f:
        local_content = f.read ()

    return hashlib.md5 (remote_content).digest () == hashlib.md5 (local_content).digest ()

def sendWarningEmail ():
    from email.mime.text import MIMEText
    import smtplib

    sender = 'hyq@c3p-group.com'
    recipients = ['hyq@c3p-group.com', 'jzh@c3p-group.com', 'yxj@c3p-group.com']

    msg = MIMEText ('HYQ: The xi-peng.com website had been hacked.')
    msg['Subject'] = 'xi-peng.com website had been hacked.'
    msg['From'] = sender
    msg['To'] = ', '.join (recipients)

    s = smtplib.SMTP ('localhost')
    s.sendmail (sender, recipients, msg.as_string ())
    s.quit ()

def syncSource (subdir, ftpdir, filename, ftpserver, ftpuser, ftppasswd):
    if verbose:
        print ftpdir + '/' + filename

    # Gets the local source index page
    local_content = None
    with open (os.path.join (subdir, filename), mode='rb') as f:
        local_content = f.read ().replace('\r\n', '\n')

    remote_content = None
    try:
        ftp = ftplib.FTP (ftpserver)
        ftp.set_pasv (True)
        ftp.login (ftpuser, ftppasswd)

        fw = tempfile.NamedTemporaryFile (mode='wb', delete=False)
        ftp.retrbinary ('RETR ' + ftpdir + '/' + filename, fw.write)
        fw.close ()

        with open (fw.name, mode='rb') as fr:
            remote_content = fr.read ().replace('\r\n', '\n')

        if os.path.exists (fw.name):
            os.remove (fw.name)
    except:
        pass

    if hashlib.md5 (local_content).digest () != hashlib.md5 (remote_content).digest ():
        print 'Fixing %s' % (ftpdir + '/' + filename)

        with open (os.path.join (subdir, filename), mode='rb') as f:
            ftp.storbinary ('STOR ' + ftpdir + '/' + filename, f)

    ftp.close ()

def ftpRemove (ftp, filename):
    try:
        ftp.delete (filename)
    except Exception:
        pwd_saved = ftp.pwd ()
        ftp.cwd (filename)

        for f in ftp.nlst ():
            ftpRemove (ftp, f)

        ftp.rmd (pwd_saved + '/' + filename)
        ftp.cwd (pwd_saved)

def uploadWebSource (src_dir, ftpserver, ftpuser, ftppasswd):
    for subdir, dirs, files in os.walk (src_dir):
        relpath = os.path.relpath (subdir, src_dir).replace ('\\', '/')

        if relpath == '.':
            ftpdir = '/www'
        else:
            ftpdir = '/www/' + relpath

        for filename in files:
            for x in range (RETRY_TIMES):
                try:
                    syncSource (subdir, ftpdir, filename, ftpserver, ftpuser, ftppasswd)
                    break
                except:
                    pass

        for x in range (RETRY_TIMES):
            try:
                ftp = ftplib.FTP (ftpserver)
                ftp.set_pasv (True)
                ftp.login (ftpuser, ftppasswd)

                ftp.cwd (ftpdir)

                remote_files = ftp.nlst ()
                for remote_filename in remote_files:
                    if (not remote_filename in files) and (not remote_filename in dirs):
                        print 'Removing ' + remote_filename
                        ftpRemove (ftp, remote_filename)

                ftp.close ()

                break
            except:
                pass

def run (src_dir, ftpserver, ftpuser, ftppasswd):
    if not checkIndexPage (src_dir):
        uploadWebSource (src_dir, ftpserver, ftpuser, ftppasswd)

def main ():
    src_dir, ftpserver, ftpuser, ftppasswd, sendmail = getopts ()
    if sendmail:
        if not checkIndexPage (src_dir):
            sendWarningEmail ()
    else:
        run (src_dir, ftpserver, ftpuser, ftppasswd)

if __name__ == "__main__":
    main ()

# vim: softtabstop=4 shiftwidth=4 expandtab
