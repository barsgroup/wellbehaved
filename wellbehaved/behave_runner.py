#coding: utf-8

from behave.runner import Runner

from utils import HookDictWrapper


class CustomBehaveRunner(Runner):

    def __init__(self, config):
        self.hooks = HookDictWrapper()
        super(CustomBehaveRunner, self).__init__(config)
