CS Pragmatics - Autograders
------------------

An assortment of scripts to help manage autograding of assignments.

### Working with the CLI

1. Grab the `grade.py` from an existing assignment
1. Implement `get_test_cases_and_submissions`, which must return 
    `test_cases` and `submissions`. This gets injected into the cli.
1. `grade.py` is the entrypoint for `cli.py`. In your directory, call
   `grade.py --help` for more usage information.

#### Common tasks:

```bash
# grade everything in a given submissions file
# will clone but throw away the grades
$ ./grade.py grade --submissions ~/Downloads/c4cs-rpn-repos.csv 

# you really want to chain commands (write results.json and scores.csv):
$ ./grade.py grade -s ~/Downloads/c4cs-rpn-repos.csv write_results write_canvas print_stats

# you can also load the results back up from results.json:
$ ./grade.py load_results print_stats

# write emails but don't send
$ ./grade.py load_results write_emails \
    --assignment-name="Homework 10" \
    --total-points=4 \
    --regrade-date="April 7" \
    --autograder-link="https://google.com" \
    --dest="/tmp/hw10_emails"

# send the emails
$ ./grade.py send_emails \
    --loc="/tmp/hw10_emails" \
    --subject="[c4cs] HW10 Graded" \
    --smtp-username="csprag-admin" \
    --cc="csprag-admin@umich.edu"

# and each command and subcommand has help
$ ./grade.py load_results --help

```

### Creating a new autograder
The `autograder.py` script contains a collection of classes.

- `Autograder` takes in a list of `TestCase`s and submissions which then
  individually get passed to `TestCase.test` by way of the `TestRunner`.
- `TestCase` returns a `TestCaseResult`.

### Dependencies
Probably a lot of them... Sorry.
