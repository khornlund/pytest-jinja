vars = [
    report_name,
    report_datetime,
    username,
    operating_system,
    python_version,
    n_tests,
    runtime,

]

test_vars = [
    result,
    name,
    duration,
    log,
]

<tbody class="failed results-table-row">
    <tr>
        <td class="col-result">{{ result }}</td>
        <td class="col-name">{{ name }}}</td>
        <td class="col-duration">{{ duration }}</td>
        <td class="col-links"></td></tr>
    <tr>
        <td class="extra" colspan="4">
            <div class="log">{{ log }}</div>
        </td>
    </tr>
</tbody>
<tbody class="passed results-table-row">
    <tr>
        <td class="col-result">{{ result }}</td>
        <td class="col-name">{{ name }}}</td>
        <td class="col-duration">{{ duration }}</td>
        <td class="col-links"></td></tr>
    <tr>
        <td class="extra" colspan="4">
            <div class="log">{{ log }}</div>
        </td>
    </tr>
</tbody>

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

    @classmethod
    def parse_json(cls, json_f):
        with open(json_f) as fh:
            data = json.load(fh)