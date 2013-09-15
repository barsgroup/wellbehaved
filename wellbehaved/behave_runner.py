#coding: utf-8

from behave.runner import Runner

from django.conf import settings
from django.db import transaction, connections, DEFAULT_DB_ALIAS

class HookDictWrapper(dict):
    u'''
    Класс, "прозрачно" перехватывающий установку обработчиков шагов 
    тестирования в environment.py. В случае, если мы тоже обрабатываем
    этот шаг, то мы оборачиваем переданный обработчик таким образом,
    что наш код всегда испольняется первым.

    На данный момент используется для гарантирования срабатывания кода
    частичного отката изменения после прохождения шага сценария.
    '''

    def __init__(self, wrapped):
        self.wrapped = wrapped
        # По умолчанию устанавливаем свои обработчики шагов
        for hook, handler in self.wrapped.items():
            super(HookDictWrapper, self).__setitem__(hook, handler)

    def __setitem__(self, hook, handler):
        '''
        Перехватчик установки обработчика очередного шага пользовательским
        кодом. Устанавливаемый обработчик будет всегда выполнятся после нашего.

        :param hook: Код события ([after|before]_[feature|step|scenario|tag|all])
        :param handler: Обработчик события из environment.py
        '''

        def wrap_hook(name, original_hook):
            def wrapper(*args, **kwargs):
                self.wrapped[name](*args, **kwargs)
                original_hook(*args, **kwargs)
            return wrapper

        if hook in self.wrapped:
            super(HookDictWrapper, self).__setitem__(hook, wrap_hook(hook, handler))
        else:
            super(HookDictWrapper, self).__setitem__(hook, handler)


class CustomBehaveRunner(Runner):
    def create_savepoint_before_all(self, context):
        u'''
        Обработчик, срабатывающий перед началом выполнения feature.

        Так как behave применяет содержимое Background (Предыстория)
        перед каждым сценарием, мы создаем точку отката транзакции
        для возврата базы в изначальное состояние после отработки
        сценария.

        :param context: Контекстная информация текущего шага.
        '''
        context.__initial_savepoint = transaction.savepoint()

    def restore_savepoint_after_scenario(self, context, scenario):
        u'''
        Обработчик, срабатывающий после отработки сценария в feature.
        
        Восстанавливаем данные после прохода сценария, откатившись
        внутри транзакции на заранее сохраненную точку (самое начало
        обработки feature). 
        '''
        transaction.savepoint_rollback(context.__initial_savepoint)

    def __init__(self, config):
        super(CustomBehaveRunner, self).__init__(config)
        chosen_rollback_mode = getattr(settings, 'WELLBEHAVED_ROLLBACK_MODE', 'partial')
        # Режим отката изменений в БД
        rollback_hooks = {
            # Режим частичного восстановленияи, когда 
            'partial': {
                'after_scenario': self.restore_savepoint_after_scenario,
                'before_all': self.create_savepoint_before_all
            },
            'manual': {}
        }
        self.hooks = HookDictWrapper(rollback_hooks[chosen_rollback_mode])
