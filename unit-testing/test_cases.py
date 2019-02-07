import autograder

import os
import sh
import yaml

class TestTravis(autograder.TestCase):
    points_possible = 1.0

    valid_test_scripts = [
        'test_rpn.py',
        'python -m unittest',
        'python3 -m unittest',
        'python -m unittest test_rpn',
        'python test_rpn.py',
        'python -m unittest -v test_rpn',
        'python -m unittest -f test_rpn.py',
        'python -m unittest test_rpn.TestBasics',
        'python3 test_rpn.py',
        'coverage run test_rpn.py',
        'coverage run -m unittest',
        'coverage run -m  unittest',
        'coverage run python3 -m unittest',
        'make',
        'make test',
        'nosetests',
        'nosetests --with-coverage',
        'nosetests --with-coverage --cover-erase --cover-package=rpn --cover-tests',
        'pytest',
    ]

    def test(self, repo_path):
        with sh.pushd(repo_path):
            if not os.path.exists('.travis.yml'):
                return self.result('No .travis.yml file', 0)
            try:
                travis = yaml.load(open('.travis.yml'))

                for script in self.valid_test_scripts:
                    if script in travis['script']:
                        return self.result('Travis set up to run tests', 1)

                print(travis['script'])
                allow = input("Give credit? [y/N] ").strip().upper()
                if len(allow) and allow[0] == 'Y':
                    return self.result('Travis set up to run tests', 1)
                else:
                    return self.result('Travis does not appear to run tests', 0)
            except Exception as exc:
                return self.result('Failed to parse .travis.yml as valid YAML',
                                   0, additional_text=str(exc))

# Test exponentiation ourselves, then monkey patch to break calculate
# function and verify that exponentiation test works
# golden lines should be
# ['>>> 8', '>>> None', '>>> -1', '>>> GoodFail']
ugly_one_liner = '''
import inspect
import traceback
import rpn
import test_rpn
c = rpn.calculate
T = test_rpn.TestBasics()
fns = inspect.getmembers(T, predicate=lambda x: inspect.ismethod(x) and 'test_' in x.__name__ and 'test_add' not in x.__name__ and 'test_subtract' not in x.__name__ and 'test_sub' not in x.__name__ and 'test_toomany' not in x.__name__ and 'test_multiplication' not in x.__name__ and 'test_multiply' not in x.__name__ and 'test_divide' not in x.__name__ and 'test_badstring' not in x.__name__)
test_exp_names = ['test_pow','test_exponent1', 'test_exponential', 'test_carat',
'test_exp', 'test_exponent', 'test_power3', 'test_exponentiation', 'test_power',
'test_expo', 'test_exponentiate', 'test_exponant', 'test_carrot', 'test_exponentiationPos',
'test_exponentiationZ', 'test_exponentiationNeg']

if len(fns) > 1:
    for f in fns:
        if f[0] in test_exp_names:
            test_fn = f[1]
            break
    else:
        print(fns)
        assert(len(fns) == 1)
elif len(fns) == 0:
    test_fn = None
else:
    test_fn = fns[0][1]
try:
    print(">>> {}".format(rpn.calculate("2 3 ^")))
except Exception as e:
    print(">>> Fail our ^ test. " + traceback.format_exc().replace("\\n", "ç"))
try:
    if test_fn:
        print(">>> {}".format(test_fn()))
    else:
        print(">>> !! NO TEST FN")
except Exception as e:
    print(">>> Fail to pass student ^ test function. " + traceback.format_exc().replace("\\n", "ç"))
test_rpn.rpn.calculate = lambda x: -1 if "^" in x else c(x)
try:
    print(">>> {}".format(rpn.calculate("2 3 ^")))
except Exception as e:
    print(">>> Fail ^ after monkey patch. " + traceback.format_exc().replace("\\n", "ç"))
try:
    if test_fn:
        print(">>> {}".format(test_fn()))
    else:
        print(">>> !! NO TEST FN")
except T.failureException:
    print(">>> GoodFail")
except Exception as e:
    print(">>> Fail ^ (bad) test function threw an unknown exception. " + traceback.format_exc().replace("\\n", "ç"))
'''

class TestExponentiation(autograder.TestCase):
    def get_lines(self, repo_path):
        with sh.pushd(repo_path):
            a = sh.python3('-c', ugly_one_liner)
            lines = [x for x in a.stdout.decode('utf-8').split('\n') if '>>>' in x]
            return lines

class TestExponentiationGood(TestExponentiation):
    points_possible = 1

    def test(self, repo_path):
        lines = self.get_lines(repo_path)

        if lines[1] == '>>> None':
            return self.result('Test case passes valid exponentiation function', 1)
        elif lines[1] == '>>> !! NO TEST FN':
            return self.result('Could not find test case for exponentiation', 0)
        else:
            return self.result('Testing for valid exponentiation function failed',
                               0, additional_text=lines[1].replace('ç', '\n'))

class TestExponentiationBad(TestExponentiation):
    points_possible = 1

    def test(self, repo_path):
        lines = self.get_lines(repo_path)

        if lines[3] == '>>> GoodFail':
            return self.result('Test case catches bad exponentiation implementation', 1)
        elif lines[3] == '>>> !! NO TEST FN':
            return self.result('Could not find test case for exponentiation', 0)
        else:
            return self.result('Testing that bad exponentiation function fails failed',
                0, additional_text=lines[3].replace('ç', '\n'))

class TestExponentiationImpl(TestExponentiation):
    points_possible = 1

    def test(self, repo_path):
        lines = self.get_lines(repo_path)

        if lines[0] == '>>> 8' or lines[0] == '>>> 8.0':
            return self.result('Exponentiation implementation correct', 1)
        else:
            return self.result('Testing student exponentiation function failed',
                               0, additional_text=lines[0].replace('ç', '\n'))
