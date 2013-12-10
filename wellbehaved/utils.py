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

        :param hook: Код события ([after|before]_[feature|step|...])
        :param handler: Обработчик события из environment.py
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
