#coding: utf-8

import os
import sys

from django.conf import settings
from django.db import transaction, connections, DEFAULT_DB_ALIAS
from django.test import TestCase
from django.test.testcases import disable_transaction_methods, restore_transaction_methods

from behave.configuration import Configuration

from behave_runner import CustomBehaveRunner

class FeatureDiscovererMetaclass(type):
    def __new__(cls, clsname, bases, attrs):        
        def _wrap_run_bdd(func_name, feature_fn):
            def test_runner(self, **kwargs):
                self.behave_configuration.paths = [feature_fn]
                runner = CustomBehaveRunner(self.behave_configuration)
                test_failed = runner.run()
                assert test_failed == False, 'BDD test %s has failed!' % func_name
            return test_runner

        handlers = []
        
        for root, dirs, files in os.walk('.'):
            if root.endswith('features'):
                features = [fn for fn in files if fn.endswith('.feature')]
                for feature in features:
                    handler_name = 'test_%s_feature' % feature[:-8]
                    attrs[handler_name] = _wrap_run_bdd(handler_name, os.path.join(root, feature))
                    handlers.append(handler_name)
        attrs['__feature_handlers'] = handlers
        return super(FeatureDiscovererMetaclass, cls).__new__(cls, clsname, bases, attrs)


class DjangoBDDTestCase(TestCase):
    __metaclass__ = FeatureDiscovererMetaclass

    def __init__(self, *args, **kwargs):
        self.use_existing_db = getattr(settings, 'WELLBEHAVED_USE_EXISTING_DB', False)
        if not self.use_existing_db:
            initial_fixtures = getattr(settings, 'WELLBEHAVED_INITIAL_FIXTURES', None)
            if initial_fixtures is not None:
                assert isinstance(initial_fixtures, list), 'WELLBEHAVED_INITIAL_FIXTURES should be list of strings!'
                self.fixtures = initial_fixtures        

        if getattr(self, 'multi_db', False):
            self.databases = connections
        else:
            self.databases = [DEFAULT_DB_ALIAS]
        super(DjangoBDDTestCase, self).__init__(*args, **kwargs)

    def _fixture_setup(self):
        u'''
        Здесь мы вынужденно перекрываем метод загрузки данных 
        из фикстур и дублируем часть его кода, т.к. monkey
        patching модуля транзакций зачем-то разместили здесь (sic!).
        '''
        if not self.use_existing_db:
            super(DjangoBDDTestCase, self)._fixture_setup()
        else:
            for db in self.databases:
                transaction.enter_transaction_management(using=db)
                transaction.managed(True, using=db)
            disable_transaction_methods()

    def _fixture_teardown(self):
        u'''
        Здесь мы вынужденно перекрываем метод снесения данных 
        из фикстур и дублируем часть его кода, т.к. восстановление
        методов транзакций зачем-то было помещено в него (sic!).
        '''
        if not self.use_existing_db:
            super(DjangoBDDTestCase, self)._fixture_teardown()
        else:
            restore_transaction_methods()
            for db in self.databases:
                transaction.rollback(using=db)
                transaction.leave_transaction_management(using=db)

    def id(self):
        return 'wellbehaved.DjangoBDDTestCase.%s' % self._testMethodName

    def setUp(self):
        # Так как behave пытается обрабатывать аргументы командной строки
        # и это пока что (<=1.2.3) не получается отключить, то приходится
        # применять жуткий хак с подменой командной строки
        old_argv = sys.argv
        sys.argv = sys.argv[:2]
        self.behave_configuration = Configuration()
        sys.argv = old_argv

        self.behave_configuration.format = getattr(settings, 'WELLBEHAVED_FORMATTER', ['pretty'])
        assert self.behave_configuration.format, 'Formatter settings should be a list!'
        self.behave_configuration.stdout_capture = False
        self.behave_configuration.stderr_capture = False

        # Пробуем получить язык, на котором написаны сценарии для behave
        self.behave_configuration.lang = getattr(settings, 'WELLBEHAVED_LANG', 'ru')

        # Установим нормальную кодировку для вывода сообщений в консоль Windows
        if sys.platform == 'win32':
            reload(sys)
            sys.setdefaultencoding('cp866')
