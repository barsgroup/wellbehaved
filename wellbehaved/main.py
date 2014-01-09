#coding: utf-8

import codecs
import sys
import yaml
from optparse import OptionParser

from behave.configuration import Configuration

from import_hooks import TemplateImportHooker
from log import logger, setup_logging


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
    setup_logging()
    config = {}

    opt_parser = OptionParser()
    opt_parser.add_option('', '--var-file', dest='var_file',
                          help='Load template variables from .py file.',
                          metavar='<FILE>')
    opt_parser.add_option('', '--cfg-file', dest='cfg_file',
                          help='Load configuration from YAML file.',
                          metavar='<FILE>')
    (options, args) = opt_parser.parse_args()

    if options.cfg_file:
        try:
            with open(options.cfg_file, 'r') as fp:
                config = yaml.load(fp.read())
        except Exception as ex:
            logger.error('Can\'t load {0}: {1}'.format(options.cfg_file, unicode(ex)))
        else:
            logger.info('Loaded configuration from {0}.'.format(options.cfg_file))

    if options.var_file:
        template_vars = load_vars_from_pyfile(options.var_file)
        # Есть смысл включать режим шаблонизации только при наличии переменных,
        # ради которых все и затевалось
        if template_vars:
            template_vars.pop('__builtins__', {})
            sys.meta_path = [TemplateImportHooker(template_vars)]

    # Так как behave пытается обрабатывать аргументы командной строки
    # и это пока что (<=1.2.3) не получается отключить, то приходится
    # применять жуткий хак с подменой командной строки
    old_argv = sys.argv
    sys.argv = sys.argv[:1]
    config = Configuration()
    config.format = ['pretty', ]
    sys.argv = old_argv

    from behave_runner import CustomBehaveRunner
    runner = CustomBehaveRunner(config)
    runner.run()


if __name__ == '__main__':
    start()
