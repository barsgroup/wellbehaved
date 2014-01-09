#coding: utf-8

import logging

# Настройки логирования предполагают, что программа будет запускаться
# внешним демоном и вывод будет собираться в отдельный файл.
logger = logging.getLogger('wellbehaved')
logger.setLevel(logging.DEBUG)


def setup_logging():
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
    logger.addHandler(ch)
