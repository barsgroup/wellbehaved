#coding: utf-8

import sys

from behave.configuration import Configuration
from behave_runner import CustomBehaveRunner


def start():
    config = Configuration()
    config.format = ['pretty',]

    runner = CustomBehaveRunner(config)
    runner.run()


if __name__ == '__main__':
    start()
