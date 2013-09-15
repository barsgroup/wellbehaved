#coding: utf-8

import sys

from django.conf import settings
from django.db import transaction, connections, DEFAULT_DB_ALIAS
from django.test import TestCase
from django.test.testcases import disable_transaction_methods, restore_transaction_methods

from behave.configuration import Configuration
from behave_runner import CustomBehaveRunner


class DjangoBDDTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        self.behaviour_dir = kwargs.pop('behaviour_dir')
        self.use_existing_db = kwargs.pop('use_existing_db')
    
        if not self.use_existing_db:
            initial_fixtures = getattr(settings, 'WELLBEHAVED_INITIAL_FIXTURES', [])
            assert isinstance(initial_fixtures, list), 'WELLBEHAVED_INITIAL_FIXTURES should be list of strings!'
            self.fixtures = initial_fixtures

        if getattr(self, 'multi_db', False):
            self.databases = connections
        else:
            self.databases = [DEFAULT_DB_ALIAS]

        super(DjangoBDDTestCase, self).__init__(**kwargs)

    def _fixture_setup(self):
        u'''
        Здесь мы вынужденно перекрываем метод загрузки данных 
        из фикстур и дублируем часть его кода, т.к. monkey
        patching модуля транзакций зачем-то разместили здесь (sic!).
        '''
        if not self.use_existing_db:
            super(DjangoBDDTestCase, self)._fixture_setup()

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

        restore_transaction_methods()
        for db in self.databases:
            transaction.rollback(using=db)
            transaction.leave_transaction_management(using=db)             

    def setUp(self):
        # Так как behave пытается обрабатывать аргументы командной строки
        # и это пока что (<=1.2.3) не получается отключить, то приходится
        # применять жуткий хак с подменой командной строки
        old_argv = sys.argv
        sys.argv = sys.argv[:2]
        self.behave_configuration = Configuration()
        sys.argv = old_argv

        self.behave_configuration.paths = [self.behaviour_dir]
        self.behave_configuration.format = getattr(settings, 'WELLBEHAVED_FORMATTER', ['pretty'])
        assert self.behave_configuration.format, 'Formatter settings should be a list!'
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
