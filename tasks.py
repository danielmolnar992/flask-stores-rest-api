import os

import jinja2
import requests
from dotenv import load_dotenv


load_dotenv()
MG_DOMAIN = os.getenv('MAILGUN_DOMAIN')
MG_API_KEY = os.getenv('MAILGUN_API_KEY')


template_loader = jinja2.FileSystemLoader('templates')
template_env = jinja2.Environment(loader=template_loader)


def render_template(template_filename, **context):
    return template_env.get_template(template_filename).render(**context)


def send_simple_message(to, subject, body, html):
    return requests.post(
        f"https://api.mailgun.net/v3/{MG_DOMAIN}/messages",
        auth=("api", MG_API_KEY),
        data={"from": f"My name here <mailgun@{MG_DOMAIN}>",
              "to": [to],
              "subject": subject,
              "text": body,
              'html': html}
    )


def send_user_registration_email(email, username):
    return send_simple_message(
        email,
        "Successfully signed up",
        f'Hi {username}! You have successfully signed up.',
        render_template('email/registration.html', username=username)
    )
