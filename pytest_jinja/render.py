from jinja2 import Environment, FileSystemLoader
import os
import json
from datetime import datetime


def read_json(json_f):
    with open(json_f) as fh:
        data = json.load(fh)

    context = {
        'report_name': 'Race Test Report',
        'report_datetime': datetime.fromtimestamp(data['created']).strftime("%Y-%m-%d %I:%M:%S"),
        'duration': data['duration'],
        'operating_system': data['environment']['Platform'],
        'python_version': data['environment']['Python'],
        'n_passed': data['summary']['passed'],
        'n_failed': data['summary']['failed'],
        'n_skipped': 0,  # TODO
        'n_errors': 0,  # TODO
        'n_xfail': 0,  # TODO
        'n_xpass': 0,  # TODO
        'n_total': data['summary']['total']
    }

    tests = get_tests(data)
    context['tests_pass'] = get_passes(tests)
    context['tests_fail'] = get_fails(tests)
    return context


def parse_test(test):
    d = {}
    d['nodeid'] = test['nodeid']
    d['result'] = test['outcome']
    d['random_seed'] = test['metadata']['random_seed']
    d['duration'] = round(test['setup']['duration'] + 
                     test['call']['duration'] + 
                     test['teardown']['duration'], 3)
    try:
        d['log'] = test['call']['longrepr']
    except:
        d['log'] = 'No log found.'
    return d


def get_tests(data):
    return [parse_test(test) for test in data['tests']]


def get_passes(tests):
    return [test for test in tests if test['result'] == 'passed']


def get_fails(tests):
    return [test for test in tests if test['result'] == 'failed']   


if __name__ == '__main__':
    data = read_json('resources/report.json')
    env = Environment( loader = FileSystemLoader('templates'))
    template = env.get_template('report_single.html')

    out_f = 'rendered.html'
    with open(out_f, 'w') as fh:
        fh.write(template.render(data))