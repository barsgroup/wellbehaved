#coding: utf-8

import os
import sys
import unittest

from django.db import transaction, connections, DEFAULT_DB_ALIAS
from django.db.models import get_app
from django.test import TestCase
from django.test.simple import DjangoTestSuiteRunner, reorder_suite
from django.test.testcases import disable_transaction_methods, restore_transaction_methods
from django.conf import settings

from behave.runner import Runner
from behave.configuration import Configuration


class HookDictWrapper(dict):
    u'''
    Класс, "прозрачно" перехватывающий установку обработчиков шагов 
    тестирования в environment.py. В случае, если мы тоже обрабатываем
    этот шаг, то мы оборачиваем переданный обработчик таким образом,
    что наш код всегда испольняется первым.

    На данный момент используется для гарантирования срабатывания кода
    частичного отката изменения после прохождения шага сценария.
    '''

    def __init__(self, wrapped):
        self.wrapped = wrapped
        # По умолчанию устанавливаем свои обработчики шагов
        for hook, handler in self.wrapped.items():
            super(HookDictWrapper, self).__setitem__(hook, handler)

    def __setitem__(self, hook, handler):
        '''
        Перехватчик установки обработчика очередного шага пользовательским
        кодом. Устанавливаемый обработчик будет всегда выполнятся после нашего.

        :param hook: Код события ([after|before]_[feature|step|scenario|tag|all])
        :param handler: Обработчик события из environment.py
        '''

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
        u'''
        Обработчик, срабатывающий перед началом выполнения feature.

        Так как behave применяет содержимое Background (Предыстория)
        перед каждым сценарием, мы создаем точку отката транзакции
        для возврата базы в изначальное состояние после отработки
        сценария.

        :param context: Контекстная информация текущего шага.
        '''
        context.__initial_savepoint = transaction.savepoint()

    def restore_savepoint_after_scenario(self, context, scenario):
        u'''
        Обработчик, срабатывающий после отработки сценария в feature.
        
        Восстанавливаем данные после прохода сценария, откатившись
        внутри транзакции на заранее сохраненную точку (самое начало
        обработки feature). 
        '''
        transaction.savepoint_rollback(context.__initial_savepoint)

    def __init__(self, config):
        super(CustomBehaveRunner, self).__init__(config)

        chosen_rollback_mode = getattr(settings, 'WELLBEHAVED_ROLLBACK_MODE', 'partial')
        # Режим отката изменений в БД
        rollback_hooks = {
            # Режим частичного восстановленияи, когда 
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


class DjangoBDDTestSuiteRunner(DjangoTestSuiteRunner):

    def build_suite(self, test_apps, extra_tests=None, **kwargs):
        self.use_existing_db = getattr(settings, 'WELLBEHAVED_USE_EXISTING_DB', False)

        suite = unittest.TestSuite()
        std_django_suite = DjangoTestSuiteRunner().build_suite(test_apps, **kwargs)
        suite.addTest(std_django_suite)

        for app_name in test_apps:
            app = get_app(app_name)
            module_path = os.path.dirname(app.__file__)
            behaviour_path = os.path.join(module_path, 'features')
            if os.path.isdir(behaviour_path):
                suite.addTest(DjangoBDDTestCase(behaviour_dir=behaviour_path,
                                                use_existing_db=self.use_existing_db))

        return reorder_suite(suite, (TestCase,))

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        self.setup_test_environment()
        suite = self.build_suite(test_labels, extra_tests)

        if not self.use_existing_db:
            old_config = self.setup_databases()
            result = self.run_suite(suite)
            self.teardown_databases(old_config)
        else:
            result = self.run_suite(suite)

        return self.suite_result(suite, result)