#coding: utf-8

from setuptools import setup

setup(
    name='wellbehaved',
    version='0.1.2.0',
    description='Simple wrapper for behave with added templating support.',
    author='Kirill Borisov',
    author_email='borisov@bars-open.ru',
    url='http://src.bars-open.ru/py/m3/m3_contrib/wellbehaved',
    packages=[
        'wellbehaved',
        'wellbehaved.plugins'
    ],
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
        'jinja2==2.7.1',
        'behave==1.2.3',
        'pyyaml',
        'pyredmine',
        'coverage'
    ]
)
