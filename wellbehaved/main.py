#coding: utf-8

import codecs
import importlib
import os
import sys
import yaml
from optparse import OptionParser

from behave.configuration import Configuration

from import_hooks import TemplateImportHooker
from log import logger, setup_logging

from utils import StackedHookDictWrapper


def find_plugins():
    '''
    Находим все плагины.

    @return Список модулей найденных плагинов
    '''
    plugins = {}
    modules_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins')

    modules = [fn for fn in os.listdir(modules_path) if fn.endswith('.py')]

    for fn in modules:
        if fn == '__init__.py' or not fn.startswith('plugin_'):
            continue

        name, ext = os.path.splitext(fn)
        plugins[name[7:]] = importlib.import_module('.plugins.{0}'.format(name),
                                                      package=__package__)
    return plugins


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

    try:
        arg_delim_index = sys.argv.index('--')
        behave_args = sys.argv[arg_delim_index+1:]
        sys.argv = sys.argv[:arg_delim_index]
    except ValueError:
        behave_args = []

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
                config = yaml.load(fp.read()) or {}
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

    sys.argv = [sys.argv[0],] + behave_args
    behave_cfg = Configuration()
    if not behave_cfg.format:
        behave_cfg.format = ['pretty',]

    from behave.runner import Runner
    runner = Runner(behave_cfg)

    if 'enabled_plugins' in config:
        runner.hooks = StackedHookDictWrapper()
        # Ищем все доступные плагины...
        plugins = find_plugins()
        plugin_configs = config.get('plugins', {})

        for p_id in config['enabled_plugins']:
            # TODO: убрать, если будет возможность подключать свои плагины
            assert p_id in plugins, 'Unknown plugin: {}!'.format(p_id)
            plugin = plugins[p_id]

            # Подключаем ещё один набор функций окружения. С точки зрения behave'а,
            # это будет одна функция, которая в свою очередь по порядку будет вызывать
            # обработчики _каждого_ плагина.
            logger.info('Loading plugin "{}"...'.format(p_id))
            custom_hooks = plugin.prepare_environment(plugin_configs.get(p_id, {}))
            logger.debug('Plugin "{}" sets hooks: {}'.format(p_id, ', '.join(custom_hooks.keys())))
            for hook, handler in custom_hooks.items():
                runner.hooks[hook] = handler

    runner.run()


if __name__ == '__main__':
    start()
