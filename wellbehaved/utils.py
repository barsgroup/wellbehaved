#coding: utf-8


class HookDictWrapper(dict):
    u'''
    Класс, "прозрачно" перехватывающий установку обработчиков шагов
    тестирования в environment.py. В случае, если мы тоже обрабатываем
    этот шаг, то мы оборачиваем переданный обработчик таким образом,
    что наш код всегда испольняется первым.

    На данный момент используется для гарантирования срабатывания кода
    частичного отката изменения после прохождения шага сценария.
    '''

    def set_wrappers(self, wrapped):
        self.wrapped = wrapped
        # По умолчанию устанавливаем свои обработчики шагов
        for hook, handler in self.wrapped.items():
            super(HookDictWrapper, self).__setitem__(hook, handler)

    def __init__(self, wrapped=None):
        self.set_wrappers(wrapped or {})

    def __setitem__(self, hook, handler):
        '''
        Перехватчик установки обработчика очередного шага пользовательским
        кодом. Устанавливаемый обработчик будет всегда выполнятся после нашего.

        @param hook    Код события ([after|before]_[feature|step|...])
        @param handler Обработчик события из environment.py
        '''

        def wrap_hook(name, original_hook):
            def wrapper(*args, **kwargs):
                self.wrapped[name](*args, **kwargs)
                original_hook(*args, **kwargs)
            return wrapper

        if hook in self.wrapped:
            super(HookDictWrapper, self).__setitem__(hook,
                                                     wrap_hook(hook, handler))
        else:
            super(HookDictWrapper, self).__setitem__(hook, handler)


class StackedHookDictWrapper(dict):
    def __init__(self):
        self.hook_registry = {}

    def __setitem__(self, hook, handler):
        def wrapper(*args, **kwargs):
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
