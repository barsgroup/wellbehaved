#coding: utf-8

from jinja2 import Environment

import imp
import sys

from wellbehaved.log import logger


class TemplateImportHooker(object):
    u'''
    Импорт-хук, который оборачивает стандартную функцию разбора фиич
    и трактует каждую из них как шаблон для Jinja2.

    Выполнено это через подмену функции *parse_feature* модуля
    **behave.parser**.
    '''

    def __init__(self, vars=None):
        u'''
        Конструктор, сохраняющий переменные в классе.

        :params vars: Переменные контекста для шаблонизатора.
        '''
        self.vars = vars or {}
        self.path = None
        logger.debug("Template variables: {0}".format(vars))

    def find_module(self, name, path=None):
        u'''
        Фильтр модулей, которые обрабатываются этим хуком.

        :param name: Имя импортируемого модуля.
        :param path: Путь к импортируемому модулю.
        '''
        if name == 'behave.parser':
            self.path = path
            return self
        return None

    def load_module(self, name):
        u'''
        Загрузчик модуля, который подменяет функцию разбора feature-файла
        нашей, которая предварительно преобразует её через шаблонизатор.

        :param name: Имя модуля, во избежание повторной обработки.
        '''
        if name in sys.modules:
            return sys.modules[name]

        last_name = name.split('.')[-1]
        module_info = imp.find_module(last_name, self.path)
        module = imp.load_module(name, *module_info)

        old_fn = getattr(module, 'parse_feature')

        def new_parse(data, language=None, filename=None):
            u'''
            Заменяющая стандартный парсер функция, которая предварительно
            прогоняет считанное содержимое файла через шаблонизатор.
            '''
            if filename:
                logger.debug('Processing template: {0}'.format(filename))

            data = Environment().from_string(data).render(self.vars)
            return old_fn(data, language=language, filename=filename)

        setattr(module, 'parse_feature', new_parse)
        sys.modules[name] = module

        return module
