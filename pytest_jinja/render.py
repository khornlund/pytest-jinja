from jinja2 import Environment, FileSystemLoader
import os
import json
from datetime import datetime


class Serialisable:

    @property
    def flat_attrs(self): 
        return []

    @property
    def serialisable_attrs(self):
        return []

    def to_dict(self):
        d = {}
        for attr_name in self.flat_attrs:
            attr = getattr(self, attr_name, None)
            if attr is None:
                raise Exception(f'Error: Could not get attr {attr_name} from {self}')
            d[attr_name] = attr

        for attr_name in self.serialisable_attrs:
            attr = getattr(self, attr_name, None)
            if attr is None:
                raise Exception(f'Error: Could not get attr {attr_name} from {self}')
            try:
                d[attr_name] = [child.to_dict() for child in attr]
            except Exception as ex:
                raise Exception(f'Error: could not serialise elements of {attr_name}. {ex}')
        return d


class TestCollectionBase(Serialisable):

    def __init__(self, tests):
        super().__init__()
        self.summarise_tests(tests)

    @property
    def flat_attrs(self):
        return [
            'name',
            'n_passed',
            'n_failed',
            'n_skipped',
            'n_errors',
            'n_xfail',
            'n_xpass',
            'n_total',
            'p_passed',
            'is_leaf',
            'child_type',
            'prefix'
        ]

    @property
    def serialisable_attrs(self):
        return ['children']


    def summarise_tests(self, tests):
        self.n_passed  = sum(1 for test in tests if test.result == 'passed')
        self.n_failed  = sum(1 for test in tests if test.result == 'failed')
        self.n_skipped = sum(1 for test in tests if test.result == 'skipped')
        self.n_errors  = sum(1 for test in tests if test.result == 'error')
        self.n_xfail   = sum(1 for test in tests if test.result == 'xfail')
        self.n_xpass   = sum(1 for test in tests if test.result == 'xpass')
        self.n_total   = len(tests)
        self.p_passed  = (self.n_passed + self.n_xfail) / (self.n_total - self.n_skipped) * 100


class TestCollectionCollection(TestCollectionBase):

    is_leaf = 0

    def __init__(self, prefix, name, tests, sort_by):
        super().__init__(tests)
        self.prefix = prefix
        self.name = name
        sort_by_copy = sort_by.copy()
        sort_criteria = sort_by_copy.pop(0)
        sorted_tests = self.sort_tests(tests, sort_criteria)
        if sort_by_copy:
            self.children = [
                TestCollectionCollection(sort_criteria, key, val, sort_by_copy) 
                for key, val in sorted_tests.items()]
        else:
            self.children = [
                TestCollection(sort_criteria, key, val) 
                for key, val in sorted_tests.items()]
        self.child_type = sort_criteria

    def sort_tests(self, tests, criteria):
        groups = {}
        for test in tests:
            key = getattr(test, criteria)
            if key in groups.keys():
                groups[key].append(test)
            else:
                groups[key] = [test]
        return groups


class TestCollection(TestCollectionBase):

    is_leaf = 1

    def __init__(self, prefix, name, tests):
        super().__init__(tests)
        self.prefix = prefix
        self.name = name
        self.children = tests
        self.child_type = 'tests'


class TestCollectionFactory:

    @classmethod
    def build(cls, tests, sort_metadata):
        if sort_metadata:
            return TestCollectionCollection('', 'Results', tests, sort_metadata)
        else:
            return TestCollection('', 'Results', tests)


class TestResult(Serialisable):

    def __init__(self, test_dict):
        super().__init__()
        self.nodeid = test_dict['nodeid']
        self.result = test_dict['outcome']
        self.duration = round(
            test_dict['setup']['duration'] + 
            test_dict['call']['duration'] + 
            test_dict['teardown']['duration'], 3)

        self._flat_attrs = [
            'nodeid',
            'result',
            'duration',
            'log'
        ]

        for key, val in test_dict['metadata'].items():
            setattr(self, key, val)
            self._flat_attrs.append(key)

        try:
            self.log = test_dict['call']['longrepr']
        except:
            self.log = 'No log found.'

    @property
    def flat_attrs(self):
        return self._flat_attrs


def get_context(name, json_f, sort_metadata):
    with open(json_f) as fh:
        data = json.load(fh)

    context = top_level_context(name, data)
    tests = [TestResult(test) for test in data['tests']]
    test_collection = TestCollectionFactory.build(tests, sort_metadata)
    context['children'] = [test_collection.to_dict()]
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
        'n_tests'         : data['summary']['total']
    }
    return context


if __name__ == '__main__':
    data = get_context('Race Test Report', 'resources/report.json', ['random_seed', 'model'])
    with open('context.json', 'w') as fh:
        json.dump(data, fh, indent=4)
    env = Environment( loader = FileSystemLoader('templates') )
    template = env.get_template('report.html')

    out_f = 'rendered.html'
    with open(out_f, 'w') as fh:
        fh.write(template.render(data))