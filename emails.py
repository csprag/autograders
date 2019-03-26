#!/usr/bin/env python3

from jinja2 import Environment, FileSystemLoader
import os
import sh
from termcolor import cprint
import time

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

def write_emails(data, assignment_name, total_points, regrade_date, autograder_link, dest, ceil_func):
    env = Environment(loader=FileSystemLoader(os.path.dirname(__file__) + '/email_templates'))
    template = env.get_template('c4cs.html')
    sh.mkdir('-p', dest)
    with sh.pushd(dest):
        for uniq, submission in data.items():
            with open(uniq, 'w') as f:
                f.write(template.render(
                    uniq=uniq,
                    assignment_name=assignment_name,
                    total_possible=total_points,
                    regrade_date=regrade_date,
                    autograder_link=autograder_link,
                    raw_score=submission['score'],
                    final_score=ceil_func(submission['score']),
                    testcases=submission['test_case_results'],
                ))

def send_email(uniqname, body, SUBJECT, CC):
    FROM = 'csprag-admin@umich.edu'
    TO = uniqname + '@umich.edu'
    REPLY_TO_ADDRESS = 'csprag-admin@umich.edu'
    encoding = 'html'

    cprint('Sending {}'.format(TO), 'green')

    msg = MIMEMultipart()
    msg['Subject'] = SUBJECT
    msg['From'] = FROM
    msg['To'] = TO
    msg['CC'] = ','.join(CC)
    msg.attach(MIMEText(body, encoding))
    msg.add_header('reply-to', REPLY_TO_ADDRESS)

    global sm

    send_to = [TO,] + CC
    sm.sendmail(FROM, send_to, msg.as_string())

def send_emails(loc, subject, cc, smtp):
    global sm
    sm = smtplib.SMTP_SSL(host=smtp['host'])
    sm.login(smtp['user'], smtp['pass'])

    with sh.pushd(loc):
        num_sent = 0;
        for uniq in os.listdir():
            with open(uniq) as f:
                send_email(uniq, f.read(), subject, cc)
                num_sent += 1
                # Be kind to the smtp server
                if num_sent % 50 == 0:
                    time.sleep(300)
                else:
                    time.sleep(1)
