# Imports
import time
import json
import imaplib
import smtplib
from email.parser import BytesParser
from email.policy import default
from email.utils import parseaddr, make_msgid, formatdate
from email.message import EmailMessage
from datetime import datetime, timedelta
from rich.progress import track
from keys import EMAIL_USER, EMAIL_PASSWORD

MAILBOX = 'inbox'
DRAFT_FOLDER = '"[Gmail]/Drafts"'
SEND_FOLDER = '"[Gmail]/Sent Mail"'
IMAP_SERVER = 'imap.gmail.com'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465
SENT_EMAILS_FILE = './sent_emails.json'
SENT_EMAILS_DAYS = 90


########
# The following three functions handle the
# basic connection and retrieval of emails


def _mail_select(folder):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASSWORD)
    mail.select(folder)
    return mail


def _retrieve_email_message(mail, email_uid):
    result, data = mail.uid('fetch', email_uid, '(RFC822)')
    raw_email = data[0][1]
    email_message = BytesParser(policy=default).parsebytes(raw_email)
    return email_message


def _parse_email(email_uid, email_message):
    subject = email_message['subject']
    address = parseaddr(email_message['From'])

    # Walk the entire MIME tree, collect text parts
    text_plain = None
    text_html = None
    for part in email_message.walk():
        content_type = part.get_content_type()
        if content_type == 'text/plain' and text_plain is None:
            text_plain = part.get_content()
        elif content_type == 'text/html' and text_html is None:
            text_html = part.get_content()

    # Prefer plain text, fall back to HTML
    payload = text_plain or text_html or ''

    # We need this information for replies
    message_id = email_message['Message-Id']
    email_references = email_message.get('References', '')
    references = (email_references + ' ' + message_id).strip()
    reply_to = email_message['Reply-To'] or email_message['From']

    result = {
        'email_uid': email_uid,
        'message-id': message_id,
        'references': references,
        'reply_to': reply_to,
        'subject': subject,
        'address': address,
        'payload': payload,
    }
    return result

#######

#######
# Section to cover read_stored_sent_emails()


def _retrieve_sent_message(sent_uid):
    '''
    Return a sent email
    '''
    mail = _mail_select(SEND_FOLDER)
    email_message = _retrieve_email_message(mail, sent_uid)
    email = _parse_email(sent_uid, email_message)

    return email


def _retrieve_and_store_sent_emails():
    '''
    Retrieve messages that have been sent to
    get data on the tone and style of responses
    '''
    print('Retrieve and store sent emails for later access')
    mail = _mail_select(SEND_FOLDER)

    since = (datetime.now() - timedelta(days=SENT_EMAILS_DAYS)).strftime("%d-%b-%Y")

    result, data = mail.uid('search', None, f'(SINCE "{since}")')
    sent_uids = data[0].split()
    # Check all sent emails from the last SENT_EMAILS_DAYS days
    contents = []
    print(f'Found {len(sent_uids)}')
    for sent_uid in track(sent_uids, description='Processing emails'):
        email = _retrieve_sent_message(sent_uid)
        payload = email['payload']
        contents.append(payload)

    # Store all contents in a file
    with open(SENT_EMAILS_FILE, 'w') as json_file:
        json.dump(contents, json_file)


def read_stored_sent_emails():
    '''
    Retrieve the stored sent emails from the file.
    This function will be exposed as a tool.
    '''
    # Retrieve the contents from the file
    with open(SENT_EMAILS_FILE) as json_file:
        result = json.load(json_file)

    return result


#####


def _check_draft_for_email(email_uid):
    '''
    Verify if there's already a draft email responding to this email,
    and return True if it is
    '''
    source_email = _retrieve_email_uid(email_uid)

    # Retrieve all emails from draft folder
    mail = _mail_select(DRAFT_FOLDER)

    result, data = mail.uid('search', None, 'ALL')
    draft_uids = data[0].split()
    # Check all existing drafts
    for draft_uid in draft_uids:
        draft = _retrieve_draft(draft_uid)
        # Check if it responds to this email
        if draft['In-Reply-To'] == source_email['message-id']:
            return True

    return False


def _retrieve_draft(draft_uid):
    '''
    Return a draft email
    '''
    mail = _mail_select(DRAFT_FOLDER)
    draft_email = _retrieve_email_message(mail, draft_uid)
    return draft_email


def _retrieve_email_uid(email_uid):
    '''
    Retrieve a single email, based on its uid.
    Return its subject, address and text body as payload
    '''

    print(f'Retrieve email {email_uid}')

    mail = _mail_select(MAILBOX)
    email_message = _retrieve_email_message(mail, email_uid)
    email = _parse_email(email_uid, email_message)

    return email


def retrieve_last_emails():
    '''
    Retrieve all emails since a day ago
    '''
    print('retrieve_last_emails')
    mail = _mail_select(MAILBOX)

    since = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")

    result, data = mail.uid('search', None, f'(SINCE "{since}")')
    email_uids = data[0].decode().split()
    data = [_retrieve_email_uid(uid) for uid in email_uids]
    return data


def create_a_draft_reply(email_uid, content):
    '''
    This tool creates a draft as response to the specified email
    '''
    print(f'creating a draft reply for {email_uid}')

    # Retrieve the original email to get the relevant values for
    # reply
    source_email = _retrieve_email_uid(email_uid)

    # Check first that a draft reply is not already present
    if _check_draft_for_email(email_uid):
        return 'Draft already exists'

    reply = EmailMessage()
    reply['From'] = EMAIL_USER
    reply['To'] = source_email['reply_to']
    reply['Subject'] = 'Re: ' + source_email['subject'].replace('Re: ', '')
    reply['Date'] = formatdate(localtime=True)
    reply['Message-ID'] = make_msgid()

    reply['In-Reply-To'] = source_email['message-id']
    reply['References'] = source_email['references']

    reply.set_content(content)

    mail = _mail_select(DRAFT_FOLDER)
    mail.append(DRAFT_FOLDER,
                '\\Draft',
                imaplib.Time2Internaldate(time.time()),
                reply.as_bytes())

    return 'draft created'


def send_a_summary_email(summary, content):
    '''
    Send an email to yourself from your Agent with a summary of emails
    '''
    print('Sending a summary email')

    email = EmailMessage()
    email['From'] = EMAIL_USER
    email['To'] = EMAIL_USER
    email['Subject'] = summary

    email['Date'] = formatdate(localtime=True)
    email['Message-ID'] = make_msgid()

    email.set_content(content)

    # Connect to the SMTP server and send the email

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp_server:
        smtp_server.login(EMAIL_USER, EMAIL_PASSWORD)
        smtp_server.send_message(email)


if __name__ == '__main__':
    # Store the last SENT_EMAILS_DAYS days of sent emails
    # to be sure to cover the style of replies
    _retrieve_and_store_sent_emails()
