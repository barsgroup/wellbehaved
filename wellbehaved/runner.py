#coding: utf-8

import os
import unittest

from django.conf import settings
from django.db import transaction, connections, DEFAULT_DB_ALIAS
from django.test.simple import DjangoTestSuiteRunner, reorder_suite
from django.test import TestCase
from django.test.testcases import disable_transaction_methods, restore_transaction_methods

from bdd_testcase import DjangoBDDTestCase

class ExistingDBRunner(DjangoTestSuiteRunner):
    def run_tests(self, test_labels, extra_tests=None, **kwargs):
    	self.use_existing_db = getattr(settings, 'WELLBEHAVED_USE_EXISTING_DB', False)
        self.setup_test_environment()
        suite = self.build_suite(test_labels, extra_tests)

        if not self.use_existing_db:
            old_config = self.setup_databases()
            result = self.run_suite(suite)
            self.teardown_databases(old_config)
        else:
            result = self.run_suite(suite)

        return self.suite_result(suite, result)
