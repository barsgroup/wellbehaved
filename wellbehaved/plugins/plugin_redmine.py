#coding: utf-8

from redmine import Redmine
from ..log import logger


def prepare_environment(config):
    def before_all(context):
        logger.debug('Checking with Redmine ({host}) to skip tests.'.format(**config))
        context.redmine = Redmine(config['host'],
                                  username=config['user'],
                                  password=config['pass'])
        context._redmine_statuses = config.get('statuses', [])


    def before_feature(context, feature):
        for scenario in feature.scenarios:
            required = [t[7:] for t in scenario.tags if t.startswith('redmine')]

            for issue_id in required:
                issue = context.redmine.issues[int(issue_id)]

                if issue.status.name in context._redmine_statuses:
                    logger.debug(u'Skipping scenario "{}" (issue #{} - "{}")'.format(
                        scenario.name, issue_id, issue.status.name))
                    scenario.should_skip = True
                    break

    return {
        'before_all': before_all,
        'before_feature': before_feature
    }
