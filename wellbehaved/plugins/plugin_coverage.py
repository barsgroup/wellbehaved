#coding: utf-8

from coverage import coverage
from uuid import uuid4

from wellbehaved.log import logger

def prepare_environment(config):
    def start_coverage(context):
        logger.debug('Starting code coverage...')
        cov = coverage()
        cov.start()
        context._coverage = cov

    def stop_coverage(context):
        logger.debug('Stopping coverage...')
        log_type = config.get('type', 'report')
        kwargs = {
            'omit': ['*wellbehaved*', '*site-packages/behave*']
        }
        fn = config.get('output', 'coverage_{}'.format(uuid4().hex))
        context._coverage.stop()

        if log_type == 'report':
            fn += '.log'
            with open('{}.log'.format(fn), 'w') as fp:
                kwargs['file'] = fp
                context._coverage.report(**kwargs)
        elif log_type == 'html':
            kwargs['directory'] = config.get('output', fn)
            context._coverage.html_report(**kwargs)
        logger.info('Saving coverage info in "%s".'.format(fn))

    return {
        'before_all': start_coverage,
        'after_all': stop_coverage
    }
