#coding: utf-8

import codecs
import sys

from behave.configuration import Configuration
from import_hooks import TemplateImportHooker


def load_vars_from_pyfile(fn):
    '''
    Загрузка переменных из контекста Python-кода, хранящегося в
    указанном файле.

    @param: fn  .py файл
    @type:  fn  unicode

    @return переменные верхнего уровня из .py-файла
    @rtype  dict
    '''
    local_vars = {}

    with codecs.open(fn, 'r', 'utf-8') as fp:
        code = fp.read()
        exec code in local_vars
    return local_vars


def start():
    config = Configuration()
    config.format = ['pretty', ]

    v = load_vars_from_pyfile('vars.py')
    sys.meta_path = [TemplateImportHooker(v)]

    from behave_runner import CustomBehaveRunner
    runner = CustomBehaveRunner(config)
    runner.run()


if __name__ == '__main__':
    start()
