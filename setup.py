#coding: utf-8

from setuptools import setup

setup(
    name='wellbehaved',
    packages=['wellbehaved'],
    version='0.1.0',
    description='Simple Django Test Runner for the behave BDD module '
                'with i18n support',
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
    entry_points={
        'console_scripts': [
            'wellbehaved = wellbehaved.main:start',
        ]
    },
    install_requires=[
        'behave==1.2.3'
    ]
)
