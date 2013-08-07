#coding: utf-8

import os
import sys
import unittest

from django.db.models import get_app
from django.test import TestCase
from django.test.simple import DjangoTestSuiteRunner, reorder_suite
from django.conf import settings

from behave.runner import Runner
from behave.configuration import Configuration


class DjangoBDDTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        self.behaviour_dir = kwargs.pop('behaviour_dir')
        
        initial_fixtures = getattr(settings, 'WELLBEHAVED_INITIAL_FIXTURES', [])
        assert isinstance(initial_fixtures, list), 'WELLBEHAVED_INITIAL_FIXTURES should be list of strings!'
        self.fixtures = initial_fixtures

        super(DjangoBDDTestCase, self).__init__(**kwargs)

    def setUp(self):
        # Так как behave пытается обрабатывать аргументы командной строки
        # и это пока что (<=1.2.3) не получается отключить, то приходится
        # применять жуткий хак с подменой командной строки
        old_argv = sys.argv
        sys.argv = sys.argv[:2]
        self.behave_configuration = Configuration()
        sys.argv = old_argv

        self.behave_configuration.paths = [self.behaviour_dir]
        self.behave_configuration.format = ['pretty']        
        self.behave_configuration.stdout_capture = False
        self.behave_configuration.stderr_capture = False

        # Пробуем получить язык, на котором написаны сценарии для behave
        self.behave_configuration.lang = getattr(settings, 'WELLBEHAVED_LANG', 'ru')

    def runTest(self, result=None):
        runner = Runner(self.behave_configuration)

        assert runner.run(), 'BDD test has failed.'


class DjangoBDDTestSuiteRunner(DjangoTestSuiteRunner):

    def build_suite(self, test_apps, extra_tests=None, **kwargs):
        suite = unittest.TestSuite()
        std_django_suite = DjangoTestSuiteRunner().build_suite(test_apps, **kwargs)
        suite.addTest(std_django_suite)

        for app_name in test_apps:
            app = get_app(app_name)

            module_path = os.path.dirname(app.__file__)
            behaviour_path = os.path.join(module_path, 'features')
            if os.path.isdir(behaviour_path):
                suite.addTest(DjangoBDDTestCase(behaviour_dir=behaviour_path))

        return reorder_suite(suite, (TestCase,))