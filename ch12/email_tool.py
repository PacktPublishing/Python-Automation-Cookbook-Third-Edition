# Imports
import imaplib
from email.parser import BytesParser
from email.policy import default
from email.utils import parseaddr
from datetime import datetime, timedelta
from keys import EMAIL_USER, EMAIL_PASSWORD
try:
    from keys import MAILBOX
except ImportError:
    MAILBOX = 'inbox'


# Connect to the server and select the mailbox
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(EMAIL_USER, EMAIL_PASSWORD)

mail.select(MAILBOX)


def retrieve_email_uid(email_uid):
    '''
    Retrieve a single email, based on its uid.
    Return its subject, address and text body as payload
    '''
    result, data = mail.uid('fetch', email_uid, '(RFC822)')
    raw_email = data[0][1]

    email_message = BytesParser(policy=default).parsebytes(raw_email)
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

    return {
        'subject': subject,
        'address': address,
        'payload': payload,
    }


def retrieve_last_emails():
    '''
    Retrieve all emails since a day ago
    '''
    since = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")

    result, data = mail.uid('search', None, f'(SINCE "{since}")')
    email_uids = data[0].split()
    # We retrieve only the last 20 emails, to simplify
    email_uids = email_uids[-20:]
    data = [retrieve_email_uid(uid) for uid in email_uids]
    return data


if __name__ == '__main__':
    # Test that the retrieval of emails is successful
    for index, email in enumerate(retrieve_last_emails()):
        print(index, email['subject'])
