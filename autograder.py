#!/usr/bin/env python3

import numpy
import json
import sh
import os
import pprint
from collections import defaultdict, Counter, OrderedDict
from termcolor import cprint

class ImmutableDict(OrderedDict):
    def __setitem__(self, key, value):
        if key in self:
            raise LookupError('{} already returned'.format(key))
        OrderedDict.__setitem__(self, key, value)

class TestCaseResult:
    def __init__(self, message, score, points_possible, additional_text=''):
        self.message = message
        self.score = float(score)
        self.points_possible = float(points_possible)
        self.additional_text = additional_text

    def __repr__(self):
        return self.message

class TestCase:
    def __repr__(self):
        return self.__class__.__name__

    def result(self, message, score, additional_text=None):
        return TestCaseResult(message, float(score), self.points_possible, additional_text)

    def test(self, submission):
        raise NotImplementedError('Subclasses must override this')

class TestRunner:
    def __init__(self, test_cases, logger=lambda *args: None):
        self.test_cases = test_cases
        self.log = logger

    def test_submission(self, submission):
        result = ImmutableDict()

        for test_case in self.test_cases:
            key = str(test_case)
            try:
                result[key] = test_case.test(submission)
            except sh.ErrorReturnCode as e:
                result[key] = test_case.result('Uncaught shell exception', 0,
                        additional_text=e.stderr.decode('utf-8'))
            except Exception as e:
                result[key] = test_case.result('Uncaught exception', 0,
                        additional_text=str(e))

            self.log('{}: {} [{}/{}]'.format(test_case, result[key],
                result[key].score, float(test_case.points_possible)))

            if result[key].additional_text:
                self.log(result[key].additional_text, indent=4, color='red')

        return result

class Autograder:
    def __init__(self):
        self.results = ImmutableDict()
        self.grades = ImmutableDict()

    def log(self, message, indent=0, color=None):
        for line in message.splitlines():
            cprint(' '*indent + line, color)

    def set_submissions(self, submissions):
        self.submissions = submissions

    def set_test_cases(self, test_cases):
        self.test_runner = TestRunner(
            test_cases,
            lambda msg, indent=0, color=None: self.log(msg, indent=indent+2, color=color)
        )

    def clone(self, rerun=False):
        for uniq in list(self.submissions.keys()):
            # don't use .items() because we're deleting things
            submission = self.submissions[uniq]

            if os.path.isdir(submission[1]) and not rerun:
                self.log('{} exists, run with rerun=True to re-clone'.format(submission[1]))
                continue

            self.log('Cloning {} into {} for {}'.format(submission[0], submission[1], uniq))

            sh.rm('-Rf', submission[1])
            sh.mkdir('-p', submission[1])
            try:
                sh.git('clone', submission[0], submission[1])
            except sh.ErrorReturnCode as e:
                err = e.stderr.decode('utf-8')
                self.log(err, color='red')
                self.results[uniq] = {
                    'Clone': TestCaseResult('Failed', 0., 0., additional_text=err)
                }

                # clean up
                sh.rm('-Rf', submission[1])

                # don't try and run test cases here, we failed
                del self.submissions[uniq]

    def grade(self):
        for key, submission in self.submissions.items():
            self.log('Grading {}'.format(key))
            self.results[key] = self.test_runner.test_submission(submission[1])

        for key, results in self.results.items():
            self.grades[key] = sum([r.score for _, r in results.items()])

    def get_results(self):
        return self.results

    def load_results(self, data):
        for uniq, result in data.items():
            self.grades[uniq] = result['score']
            self.results[uniq] = ImmutableDict()
            for testcase, testcase_result in result['test_case_results'].items():
                self.results[uniq][testcase] = TestCaseResult(**testcase_result)

    def to_dict(self):
        uniq_to_result = ImmutableDict()
        for uniq, result in self.results.items():
            uniq_to_result[uniq] = {
                'score': self.grades[uniq],
                'test_case_results': {k: v.__dict__ for k, v in result.items()}
            }

        return uniq_to_result

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)

    def get_grades(self):
        return self.grades

    def print_stats(self):
        pp = pprint.PrettyPrinter()

        # Results
        r_counter = defaultdict(Counter)
        for result in self.results.values():
            for test, result in result.items():
                r_counter[str(test)][str(result)] += 1

        pp.pprint(r_counter)

        # Grades
        grades_arr = list(self.grades.values())
        stats = {
            'min': numpy.min(grades_arr),
            'max': numpy.max(grades_arr),
            'mean': numpy.mean(grades_arr),
            'median': numpy.median(grades_arr),
            'stdev': numpy.std(grades_arr),
            'n': len(grades_arr),
        }

        pp.pprint(stats)
