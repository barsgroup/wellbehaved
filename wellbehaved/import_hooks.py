#coding: utf-8

from jinja2 import Environment

import imp
import sys


class TemplateImportHooker(object):
    def __init__(self, vars=None):
        self.vars = vars or {}

    def find_module(self, name, path=None):
        if name == 'behave.parser':
            self.path = path
            return self
        return None

    def load_module(self, name):
        if name in sys.modules:
            return sys.modules[name]

        last_name = name.split('.')[-1]
        module_info = imp.find_module(last_name, self.path)
        module = imp.load_module(name, *module_info)

        old_fn = getattr(module, 'parse_feature')

        def new_parse(data, language=None, filename=None):
            data = Environment().from_string(data).render(self.vars)
            return old_fn(data, language=language, filename=filename)

        setattr(module, 'parse_feature', new_parse)
        sys.modules[name] = module

        return module
