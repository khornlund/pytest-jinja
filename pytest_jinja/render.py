from jinja2 import Environment, FileSystemLoader
import os
import json
from datetime import datetime
from testcollections import TestCollectionFactory, TestResult


def get_context(name, json_f, sort_metadata):
    with open(json_f) as fh:
        data = json.load(fh)

    context = top_level_context(name, data)
    tests = [TestResult(test) for test in data['tests']]
    test_collection = TestCollectionFactory.build(tests, sort_metadata)
    context.update(test_collection.to_dict())
    return context


def top_level_context(name, data):
    context = {
        'report_name'     : name,
        'report_datetime' : datetime.\
                                fromtimestamp(data['created']).\
                                strftime("%Y-%m-%d %I:%M:%S"),
        'duration'        : data['duration'],
        'operating_system': data['environment']['Platform'],
        'python_version'  : data['environment']['Python'],
        'n_passed'        : data['summary']['passed'],
        'n_failed'        : data['summary']['failed'],
        'n_skipped'       : 0,  # TODO
        'n_errors'        : 0,  # TODO
        'n_xfail'         : 0,  # TODO
        'n_xpass'         : 0,  # TODO
        'n_total'         : data['summary']['total']
    }
    return context


if __name__ == '__main__':
    data = get_context('Race Test Report', 'resources/report.json', ['random_seed', 'model'])
    print(json.dumps(data, indent=4))
    # env = Environment( loader = FileSystemLoader('templates') )
    # template = env.get_template('table-row.html')

    # out_f = 'rendered.html'
    # with open(out_f, 'w') as fh:
    #     fh.write(template.render(data))