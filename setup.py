#coding: utf-8

from setuptools import setup

setup(
    name='m3-wellbehaved',
    version='0.1.2.1',
    license='MIT',
    description='Simple wrapper for behave with added templating support.',
    author='Kirill Borisov',
    author_email='bars@bars-open.ru',
    url='https://bitbucket.org/barsgroup/wellbehaved',
    packages=[
        'wellbehaved',
        'wellbehaved.plugins'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
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
