#coding: utf-8

import os
import unittest

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_app

from bdd_testcase import DjangoBDDTestCase


def suite():    
    suite = unittest.TestSuite()
    for func_name in DjangoBDDTestCase.__feature_handlers:
        suite.addTest(DjangoBDDTestCase(func_name))
    return suite
