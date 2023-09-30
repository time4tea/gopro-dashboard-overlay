# Copyright (c) 2016-18, Venkatesh-Prasad Ranganath
#
# BSD 3-clause License
#
# Author: Venkatesh-Prasad Ranganath (rvprasad)

import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Treat non-assertion and non-pytest.fail failures as test errors."""
    outcome = yield
    test_report = outcome.get_result()

    if call.excinfo and test_report.outcome == 'failed':
        when = call.when
        excinfo = call.excinfo
        if when == "call" and \
            excinfo.typename != "AssertionError" and \
                excinfo.typename != "Failed":
            when = 'setup'
        test_report.longrepr = item.repr_failure(excinfo)
        test_report.when = when
