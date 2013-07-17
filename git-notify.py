#!/usr/bin/python
import sys,commands,re
import os.path, shutil
from smtplib import SMTP
from email.MIMEText import MIMEText

#------------------------------------#
gmail_account = ''
gmail_password = ''
marker = '@'
dst_bin = 'hooks/post-receive'
log_format = '--name-only'
#------------------------------------#
bin_name = os.path.basename(sys.argv[0])
repo_name = os.path.basename(os.getcwd())

if gmail_account=='' or gmail_password=='':
    print "Gmail account/password is not specified"
    sys.exit(-1)

def check_git_dir_or_exit():
    if not os.path.isfile('HEAD') or not os.path.isdir('hooks'):
        print 'Error: directory is not a git(bare) directory'
        sys.exit(-1)

def get_message():
    r,s = commands.getstatusoutput("git log -1 --pretty=format:'%s'")
    if r != 0:
        print 'Error: directory is not a git directory'
        sys.exit(-1)
    return s

def should_trigger_notification(s):
    if s is None or len(s)==0 or s[0]!=marker:
        return 0
    return 1

def get_commiter_email():
    r,s = commands.getstatusoutput("git log -1 --pretty=format:'%ae'")
    if r != 0:
        print 'Error: directory is not a git directory'
        sys.exit(-1)
    return s

def merge_email_list(email_list):
    emails = {}
    for em in email_list:
        if em not in emails:
            emails[em] = em
    return emails.keys()

def install():
    print "installing %s..." % bin_name
    if not os.path.isdir("hooks"):
        print "No hooks directory found"
    os.system('echo "#!/bin/sh" > '+dst_bin)
    os.system('echo "'+ __file__ + ' &" >> '+dst_bin)
    os.chmod(dst_bin,0755)
    print 'OK'

check_git_dir_or_exit()

if len(sys.argv) > 1 and sys.argv[1] == 'install':
    install()
    sys.exit(0)

force = 0
if len(sys.argv) > 1 and sys.argv[1] == '-f':
    force = 1

s = get_message()
if force==0 and should_trigger_notification(s)==0:
    sys.exit(0)

log = commands.getoutput('git log 2> /dev/null | git shortlog -s -e')
email_list = re.findall('<([\w\-\+\.]+@[\w\-\.]+)>',log+"\n "+s)
email_list = merge_email_list(email_list)

if email_list is None or len(email_list) == 0:
    sys.exit(0)

print "Igniting %s" % bin_name

for em in email_list:
    print "Nofitying to <%s>" % em

body = '# Commit log\n\n'
body += commands.getoutput('git log -1 '+log_format+' 2> /dev/null')
body += '\n\n'

host, port = 'smtp.gmail.com', 587
msg = MIMEText(body, _charset='utf-8')
msg['From'] = gmail_account
msg['To'] = ', '.join(email_list)
msg['Subject'] = '[%s] update notification' % repo_name

smtp = SMTP(host, port)
smtp.starttls()
smtp.login(gmail_account, gmail_password)
smtp.sendmail(gmail_account, email_list, msg.as_string())
smtp.quit()
