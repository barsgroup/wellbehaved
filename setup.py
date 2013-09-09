#coding: utf-8

from setuptools import setup

setup(
    name='wellbehaved',
    packages=['wellbehaved'],
    version='0.0.6',
    description='Simple Django Test Runner for the Behave BDD module with i18n support',
    author='Kirill Borisov',
    author_email='borisov@bars-open.ru',
    url='http://src.bars-open.ru/py/WebEdu/tools/wellbehaved',
    classifiers=[
        'Programming Language :: Python :: 2.6',
        'Framework :: Django',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Testing',
    ],
    install_requires=[
        'Django==1.4',
        'behave==1.2.3',
    ]
)
