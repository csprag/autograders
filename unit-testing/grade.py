#!/usr/bin/env python3

import click
import csv
import json
import sys

sys.path.append('..')

import cli

from test_cases import *

def score_to_final(score):
    if score > 2.:
        return 4.
    if score > .25:
        return 2.
    return 0.

def get_test_cases_and_submissions(submissionsf):
    uniq_to_repo = {}

    def gen_submissions():
        for uniq, repo in uniq_to_repo.items():
            yield uniq, (repo, '/tmp/c4cs-rpn/{}'.format(uniq))

    with open(submissionsf) as csvf:
        for row in csv.DictReader(csvf):
            uniq = row['Email Address'].split('@')[0]
            repo = row['Link to your Github repository']
            uniq_to_repo[uniq] = repo

    test_cases = [
        TestTravis(),
        TestExponentiationGood(),
        TestExponentiationBad(),
        TestExponentiationImpl(),
    ]

    submissions = {
        uniq: submission for uniq, submission in gen_submissions()
    }

    return test_cases, submissions

@click.group(chain=True)
def run_cli():
    pass

cli.init(run_cli)

run_cli(obj={
    'get_test_cases_and_submissions': get_test_cases_and_submissions,
    'ceil_func': score_to_final,
    'ag': autograder.Autograder(),
})
