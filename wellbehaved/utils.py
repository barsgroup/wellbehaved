#coding: utf-8
u'''
Вспомогательный класс подсистемы плагинов.
'''

class StackedHookDictWrapper(dict):
    u'''
    Унаследованный от *dict* класс, "прозрачно" перехватываюиbщий установку
    обработчиков шагов тестирования в environment.py.

    Каждый перехваченный обработчик добавляется в стэк, связанный
    с этим конкретным этапом тестирования и при каждом .
    '''
    def __init__(self):
        self.hook_registry = {}

    def __setitem__(self, hook, handler):
        u'''
        Перехватчик установки обработчиков из environment.py.

        :param hook: Идентификатор обработчика (см. документацию behave).
        :param handler: Функция, обрабатывающая определенный шаг тестирования.
        '''
        def wrapper(*args, **kwargs):
            u'''
            Оберточная функция, которая вызывает по очереди каждый из установленных
            извне обработчиков того или иного шага тестирования.

            :param args: Позиционные аргументы обработчика.
            :param kwargs: Словарь с ключами-значениями непозиционных аргументов.
            '''
            fnlist = self.hook_registry[hook]
            for fn in fnlist:
                fn(*args, **kwargs)

        # Беспорядочный метод заполнения окружения behave'ом заставляет
        # нас явно фильтровать список устанавливаемых значений.
        if hook in ['before_all', 'after_all', 'before_step', 'after_step',
                    'before_feature', 'after_feature', 'before_tag', 'after_tag',
                    'before_scenario', 'after_scenario']:
            if not hook in self.hook_registry:
                super(StackedHookDictWrapper, self).__setitem__(hook, wrapper)
            self.hook_registry.setdefault(hook, []).append(handler)
        else:
            super(StackedHookDictWrapper, self).__setitem__(hook, handler)
