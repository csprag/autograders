#!/usr/bin/env python3

import click
import csv
import json
import os
import autograder
from termcolor import cprint

import emails

def init(cli):
    cli.add_command(grade)
    cli.add_command(write_results)
    cli.add_command(write_canvas)
    cli.add_command(load_results)
    cli.add_command(write_emails)
    cli.add_command(send_emails)
    cli.add_command(print_stats)

@click.command()
@click.option('--submissions', '-s', required=True, help="Submissions file location")
@click.option('--rerun', '-r', is_flag=True, default=False)
@click.pass_obj
def grade(obj, submissions, rerun):
    '''Run the autograder'''
    cprint('Grading...', 'green')

    test_cases, submissions = obj['get_test_cases_and_submissions'](submissions)

    obj['ag'].set_test_cases(test_cases)
    obj['ag'].set_submissions(submissions)

    obj['ag'].clone(rerun)
    obj['ag'].grade()

@click.command()
@click.option('--file', '-f', default='results.json', show_default=True)
@click.pass_obj
def load_results(obj, file):
    '''Load JSON results from the autograder'''
    file = os.path.abspath(os.path.expanduser(file))
    cprint('Loading {}...'.format(file), 'green')

    obj['ag'].load_results(json.loads(open(file).read()))

@click.command()
@click.option('--file', '-f', default='results.json', show_default=True)
@click.pass_obj
def write_results(obj, file):
    '''Write JSON results from the autograder'''
    file = os.path.abspath(os.path.expanduser(file))
    cprint('Writing {}...'.format(file), 'green')

    with open(file, 'w') as outfile:
        outfile.write(obj['ag'].to_json())

@click.command()
@click.pass_obj
def print_stats(obj):
    '''Print statistics'''
    obj['ag'].print_stats()

@click.command()
@click.option('--outfile', '-o', default='scores.csv', show_default=True)
@click.pass_obj
def write_canvas(obj, outfile):
    '''Write canvas-friendly grades'''
    outfile = os.path.expanduser(outfile)
    cprint('Writing {} scores to {}...'.format(
        len(obj['ag'].get_grades()), os.path.abspath(outfile)), 'green')

    with open(outfile, 'w') as csvf:
        writer = csv.DictWriter(csvf, fieldnames=['Email', 'Total Score'])
        writer.writeheader()
        for uniq, score in obj['ag'].get_grades().items():
            writer.writerow({
                'Email': uniq,
                'Total Score': score,
            })

@click.command()
@click.pass_obj
@click.option('--assignment-name', '-n', required=True)
@click.option('--total-points', '-t', required=True)
@click.option('--regrade-date', '-r', required=True)
@click.option('--autograder-link', '-l', required=True)
@click.option('--dest', '-d', required=True)
def write_emails(obj, assignment_name, total_points, regrade_date, autograder_link, dest):
    '''Generate autograder emails but do not send'''
    dest = os.path.abspath(os.path.expanduser(dest))
    total_points = float(total_points)

    cprint('Writing {} emails to {}...'.format(len(obj['ag'].to_dict()), dest), 'green')

    if 'ceil_func' in obj:
        ceil_func = obj['ceil_func']
    else:
        ceil_func = lambda x: x

    emails.write_emails(obj['ag'].to_dict(), assignment_name, total_points,
            regrade_date, autograder_link, dest, ceil_func)

@click.command()
@click.pass_obj
@click.option('--loc', '-l', required=True)
@click.option('--subject', '-s', required=True)
@click.option('--cc', '-c', default='')
@click.option('--smtp-host', '-h', default='smtp.mail.umich.edu', show_default=True)
@click.option('--smtp-username', '-u', required=True, help="Just your uniqname for smtp.mail.umich.edu")
@click.option('--smtp-password', '-p', prompt='SMTP password', hide_input=True)
def send_emails(obj, loc, subject, cc, smtp_host, smtp_username, smtp_password):
    '''Send pre-generated autograder emails'''
    cc = cc.split()

    emails.send_emails(loc, subject, cc, {
        'host': smtp_host,
        'user': smtp_username,
        'pass': smtp_password,
    })
