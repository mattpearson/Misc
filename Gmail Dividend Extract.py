# vim:sw=4:nu:expandtab:tabstop=4:ai

import sys
import imaplib
import getpass
import email
import datetime

def process_mailbox(M):
  rv, data = M.search(None, '(BODY "Dividend")' )
  if rv != 'OK':
      print "No messages found!"
      return

  for num in data[0].split():
      rv, data = M.fetch(num, '(RFC822)')
      if rv != 'OK':
          print "ERROR getting message", num
          return

      msg = email.message_from_string(data[0][1])
      print 'Message %s: %s' % (num, msg['Subject'])
      print 'Raw Date:', msg['Date']
      date_tuple = email.utils.parsedate_tz(msg['Date'])
      if date_tuple:
        local_date = datetime.datetime.fromtimestamp( email.utils.mktime_tz(date_tuple))
        print "Local Date:", local_date.strftime("%a, %d %b %Y %H:%M:%S")
      b = msg
      body = ""

      if b.is_multipart():
        for part in b.walk():
          ctype = part.get_content_type()
          cdispo = str(part.get('Content-Disposition'))

          if ctype == 'text/plain' and 'attachment' not in cdispo:
            body = part.get_payload(decode=True)  # decode
            break
        else:
          body = b.get_payload(decode=True)

      body = body.replace('\n', ' ').replace('\r', '')
      #print body

      print 'Matching process...'

      import re
      pattern = re.compile( '\* ([\w ]+)@\w+ \(Name: ([^\)]{1,})[^0-9]{1,}(........)[^0-9]{1,}(........).[^0-9]+(\d{1,}\.\d{1,})')
      pos = 0
      more = True
      while( more == True):
        match = pattern.search( body, pos )
        if not match:
          more = False
        else:
          print 'Symbol: ', match.group(1) # Symbol
          print 'Company: ', match.group(2) # Company name
          print 'ExDate: ', match.group(3) # Ex date
          print 'PayDate: ', match.group(4) # Pay date
          print 'Coupon: ', match.group(5) # Coupon
          print '----'
          pos = match.end()

M = imaplib.IMAP4_SSL('imap.gmail.com')

try:
    M.login('xxxxxxxxxxxx@gmail.com', getpass.getpass())
except imaplib.IMAP4.error:
    print "LOGIN FAILED!!! "
    sys.exit(1)

rv, mailboxes = M.list()
if rv == 'OK':
    print "Mailboxes:"
    print mailboxes

rv, data = M.select("INBOX")
if rv == 'OK':
    print "Processing mailbox..."
    process_mailbox(M) 
    M.close()

M.logout()

