#coding: utf-8

from setuptools import setup

setup(
    name='wellbehaved',
    packages=['wellbehaved'],
    version='0.1.0.0',
    description='Simple wrapper for behave with added templating support.',
    author='Kirill Borisov',
    author_email='borisov@bars-open.ru',
    url='http://src.bars-open.ru/py/m3/m3_contrib/wellbehaved',
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
        'jinja==2.7.1',
        'behave==1.2.3'
        'pyyaml',
    ]
)
