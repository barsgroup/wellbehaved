#coding: utf-8

import os
import unittest

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_app

from runner import ExistingDBRunner
from bdd_testcase import DjangoBDDTestCase


def suite():
    suite = unittest.TestSuite()
    runner = getattr(settings, 'TEST_RUNNER', None)
    use_existing = False
    if isinstance(runner, ExistingDBRunner):
        use_existing = True

    for root, dirs, files in os.walk('.'):
        if root.endswith('features'):
            suite.addTest(DjangoBDDTestCase('%s.features' % root,
                                            behaviour_dir=os.path.abspath(root),
                                            use_existing_db=use_existing))
    return suite
