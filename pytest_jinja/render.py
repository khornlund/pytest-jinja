from jinja2 import Environment, FileSystemLoader
import os

class Test:

    @classmethod
    def to_dict(cls, result, name, duration, log):
        return {
            'result': result,
            'name': name,
            'duration': duration,
            'log': log
        }


class Data:

    @classmethod
    def to_dict(cls):
        return {
            'report_name'         : 'TestReport',
            'report_datetime'     : '2019-02-07 21:53:00',
            'username'            : 'KarlHornlund',
            'operating_system'    : 'Windows10',
            'python_version'      : '3.6.6',
            'n_tests'             : '4',
            'runtime'             : '1.05s',
            'tests_fail': [
                Test.to_dict('Failed', 'tests/tests.py::test_example[1]', 0.03, 'Reason'),
                Test.to_dict('Failed', 'tests/tests.py::test_example[3]', 0.01, 'Reason')
            ],
            'tests_pass': [
                Test.to_dict('Passed', 'tests/tests.py::test_example[0]', 0.02, ''),
                Test.to_dict('Passed', 'tests/tests.py::test_example[2]', 0.01, ''),
            ]
        }

if __name__ == '__main__':
    data = Data.to_dict()
    env = Environment( loader = FileSystemLoader('templates'))
    template = env.get_template('report_single.html')

    out_f = 'rendered.html'
    with open(out_f, 'w') as fh:
        fh.write(template.render(data))