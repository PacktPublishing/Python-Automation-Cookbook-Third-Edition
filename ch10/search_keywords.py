# IMPORTS #
import argparse
import sys
import configparser
import feedparser
import pendulum
import mistune
import jinja2
from collections import namedtuple

import smtplib
import calendar
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# READ TEMPLATES #

# Group the email configuration parameters
# Note the 'from_' to avoid using a reserved Python keyword (from)
EmailConfig = namedtuple('EmailConfig', ['user', 'password', 'from_', 'to'])


# Get the email templates from hard disk
EMAIL_TEMPLATE_FILE = 'email_template.md'
EMAIL_STYLING_FILE = 'email_styling.html'

with open(EMAIL_TEMPLATE_FILE) as md_file:
    EMAIL_TEMPLATE = md_file.read()

with open(EMAIL_STYLING_FILE) as html_file:
    EMAIL_STYLING = html_file.read()


def get_articles(keywords, feeds):
    '''
    Retrieve a list of articles from the feeds that contain the keywords

    Each article is returned in the format:

    (title, summary, link)
    '''
    articles = []

    for feed in feeds:
        rss = feedparser.parse(feed)
        updated_raw = rss.get('updated_parsed')
        # Use as base time either the last update time or now
        if updated_raw is None:
            updated_at = pendulum.now()
        else:
            updated_at = pendulum.from_timestamp(calendar.timegm(updated_raw))

        # Calculate the oldest article we will check, 7 days ago
        time_limit = updated_at.subtract(days=7)
        for entry in rss.entries:
            # Normalise the time
            entry_time = entry.published_parsed
            if not entry_time:
                # No time for this entry, skip
                continue
            entry_time = pendulum.from_timestamp(calendar.timegm(entry_time))

            if entry_time < time_limit:
                # Skip this entry
                continue

            # Get the article reference
            title = entry.title.strip()
            summary = entry.summary.strip()
            article_reference = (title, summary, entry.link)

            for keyword in keywords:
                summary_found = keyword.lower() in summary.lower()
                title_found = keyword.lower() in title.lower()
                if summary_found or title_found:
                    articles.append(article_reference)
                    break

    return articles


def compose_email_body(articles, keywords, feed_list):
    '''
    From the list of articles, keywords and feeds, fill the email template

    Set the list in the adequate format for the template
    '''
    # Compose the list of articles
    ARTICLE_TEMPLATE = '* **{title}** {summary}: {link}'
    article_list = [ARTICLE_TEMPLATE.format(title=title, summary=summary,
                                            link=link)
                    for title, summary, link in articles]

    data = {
        'article_list': '\n'.join(article_list),
        'keywords': ', '.join(keywords),
        'feed_list': ', '.join(feed_list),
    }
    text = jinja2.Template(EMAIL_TEMPLATE).render(**data)
    html_content = mistune.html(text)
    html = jinja2.Template(EMAIL_STYLING).render(content=html_content)

    return text, html


def send_email(email_config, text_body, html_body):
    '''
    Send an email with the text and html body, using the parameters
    configured in email_config
    '''
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Weekly report'
    msg['From'] = email_config.from_
    msg['To'] = email_config.to

    part_plain = MIMEText(text_body, 'plain')
    part_html = MIMEText(html_body, 'html')

    msg.attach(part_plain)
    msg.attach(part_html)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(email_config.user, email_config.password)
        server.sendmail(email_config.from_, [email_config.to], msg.as_string())


def main(keywords, feeds, email_config):
    articles = get_articles(keywords, feeds)
    text_body, html_body = compose_email_body(articles, keywords, feeds)
    send_email(email_config, text_body, html_body)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(type=argparse.FileType('r'), dest='config',
                        help='config file')
    parser.add_argument('-o', dest='output', type=argparse.FileType('w'),
                        help='output file',
                        default=sys.stdout)

    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read_file(args.config)
    keywords = config['SEARCH']['keywords'].split(',')
    feeds = [feed.strip() for feed in config['SEARCH']['feeds'].split(',')]

    email_user = config['EMAIL']['user']
    email_password = config['EMAIL']['password']
    email_from = config['EMAIL']['from']
    email_to = config['EMAIL']['to']
    email_config = EmailConfig(email_user, email_password, email_from,
                               email_to)

    main(keywords, feeds, email_config)
