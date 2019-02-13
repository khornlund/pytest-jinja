
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
            'is_leaf'
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


class TestCollectionCollection(TestCollectionBase):

    is_leaf = False

    def __init__(self, name, tests, sort_by):
        super().__init__(tests)
        self.name = name
        sort_by_copy = sort_by.copy()
        sort_criteria = sort_by_copy.pop(0)
        sorted_tests = self.sort_tests(tests, sort_criteria)
        if sort_by_copy:
            self.children = [TestCollectionCollection(f'{sort_criteria}: {key}', val, sort_by_copy) 
                                for key, val in sorted_tests.items()]
        else:
            self.children = [TestCollection(f'{sort_criteria}: {key}', val) 
                                for key, val in sorted_tests.items()]

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

    is_leaf = True

    def __init__(self, name, tests):
        super().__init__(tests)
        self.name = name
        self.children = tests


class TestCollectionFactory:

    @classmethod
    def build(cls, tests, sort_metadata):
        if sort_metadata:
            return TestCollectionCollection('root', tests, sort_metadata)
        else:
            return TestCollection('root', tests)


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