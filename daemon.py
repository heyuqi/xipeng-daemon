#!/usr/bin/env python

try:
    import urllib.request as urllib2
except:
    import urllib2

import hashlib

def getopts ():
    import getopt, sys

    try:
        opts, args = getopt.getopt (sys.argv[1:], "h", ["help", "srcdir=", "ftpserver=", "ftpuser=", "ftppasswd="])
    except getopt.GetoptError as err:
        # Print help information and exit:
        print str (err) # Will print something like "option -a not recognized."
        usage ()
        sys.exit (2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage ()
            sys.exit ()
        elif opt in ("--srcdir"):
            src_dir = arg
        elif opt in ("--ftpserver"):
            ftpserver  = arg
        elif opt in ("--ftpuser"):
            ftpuser = arg
        elif opt in ("--ftppasswd"):
            ftppasswd = arg
        else:
            assert False, "Unhandled option"

    return (src_dir, ftpserver, ftpuser, ftppasswd)

def checkIndexPage (src_dir):
    import os

    # Remote gets the index page
    index_html = urllib2.urlopen ("http://www.xi-peng.com/index.html")
    remote_content = index_html.read ()

    # Gets the local source index page
    local_content = None
    with open (os.path.join (src_dir, 'index.html'), mode='rb') as f:
        local_content = f.read ()

    return hashlib.md5 (remote_content) == hashlib.md5 (local_content)

def removeFtpDir (ftp, dirname):
    pwd_saved = ftp.pwd ()
    ftp.cwd (dirname)

    for filename in ftp.nlst ():
        try:
            ftp.delete (filename)
        except Exception:
            removeFtpDir (ftp, filename)

    ftp.rmd (pwd_saved + '/' + dirname)
    ftp.cwd (pwd_saved)

def uploadWebSource (src_dir, ftpserver, ftpuser, ftppasswd):
    import ftplib
    import os

    tmp_dir = 'www1'
    tmp_remove_dir = 'www-remove'

    ftp = ftplib.FTP (ftpserver, ftpuser, ftppasswd)
    if tmp_dir in ftp.nlst ():
        removeFtpDir (ftp, tmp_dir)

    ftp.mkd (tmp_dir)
    ftp.cwd (tmp_dir)

    for subdir, dirs, files in os.walk (src_dir):
        relpath = os.path.relpath (subdir, src_dir).replace ('\\', '/')

        if relpath != '.':
            ftpdir = '/' + tmp_dir + '/' + relpath
            ftp.mkd (ftpdir)
        else:
            ftpdir = '/' + tmp_dir

        for filename in files:
            with open (os.path.join (subdir, filename)) as f:
                ftp.storbinary ('STOR ' + ftpdir + '/' + filename, f)

    ftp.rename ('/www', '/' + tmp_remove_dir)
    ftp.rename ('/' + tmp_dir, '/www')

    removeFtpDir (ftp, tmp_remove_dir)
    ftp.close ()

def main ():
    src_dir, ftpserver, ftpuser, ftppasswd = getopts ()
    if not checkIndexPage (src_dir):
        uploadWebSource (src_dir, ftpserver, ftpuser, ftppasswd)

if __name__ == "__main__":
    main ()

