#coding: utf-8

import os
import sys
import unittest

from django.db import transaction
from django.db.models import get_app
from django.test import TestCase
from django.test.simple import DjangoTestSuiteRunner, reorder_suite
from django.conf import settings

from behave.runner import Runner
from behave.configuration import Configuration


class HookDictWrapper(dict):
    def __init__(self, wrapped):
        self.wrapped = wrapped
        for hook, handler in self.wrapped.items():
            super(HookDictWrapper, self).__setitem__(hook, handler)

    def __setitem__(self, hook, handler):
        def wrap_hook(name, original_hook):
            def wrapper(*args, **kwargs):
                self.wrapped[name](*args, **kwargs)
                original_hook(*args, **kwargs)
            return wrapper

        if hook in self.wrapped:
            super(HookDictWrapper, self).__setitem__(hook, wrap_hook(hook, handler))
        else:
            super(HookDictWrapper, self).__setitem__(hook, handler)


class CustomBehaveRunner(Runner):
    def create_savepoint_before_all(self, context):
        # Т.к. behave применяет содержимое Background (Предыстория)
        # перед каждым сценарием, мы создаем точку отката транзакции
        # для возврата базы в изначальное состояние после отработки
        # сценария    
        context.__initial_savepoint = transaction.savepoint()

    def restore_savepoint_after_scenario(self, context, scenario):
        # Восстанавливаем данные после прохода сценария
        transaction.savepoint_rollback(context.__initial_savepoint)

    def __init__(self, config):
        super(CustomBehaveRunner, self).__init__(config)

        chosen_rollback_mode = getattr(settings, 'WELLBEHAVED_ROLLBACK_MODE', 'partial')
        # Режим отката БД
        rollback_hooks = {
            'partial': {
                'after_scenario': self.restore_savepoint_after_scenario,
                'before_all': self.create_savepoint_before_all
            },
            'manual': {}
        }
        self.hooks = HookDictWrapper(rollback_hooks[chosen_rollback_mode])


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

        reload(sys)
        sys.setdefaultencoding('cp866')        

    def runTest(self, result=None):
        runner = CustomBehaveRunner(self.behave_configuration)
        test_failed = runner.run()

        assert not test_failed, 'BDD test has failed.'


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