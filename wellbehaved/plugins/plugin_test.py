#coding: utf-8

from ..log import logger

def prepare_environment(config):
    def printer(s):
        return lambda *a, **k: logger.debug(s)

    return {
        'before_all': printer('Hello, world!'),
        'after_all': printer('Farewell to arms.'),
        'before_step': printer('One step forward....'),
        'after_step': printer('...and two steps backwards.'),
        'before_scenario': printer('Scenario starts.'),
        'after_scenario': printer('Scenario ends.'),
        'before_feature': printer('Look! Feature!'),
        'after_feature': printer("Feature has left the building. :-(")
    }
