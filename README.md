# Wellbehaved

Обертка вокруг питоновского проекта ```behave``` (который, в свою очередь, является портом ```Cucumber``` из Ruby), позволяющая автоматически прогонять feature-файлы в качестве Django-тестов.

## Использование

* Установите пакет ```wellbehaved``` со стандартного PyPi-сервера "БАРС Груп":
```
pip install wellbehaved -i https://<PyPi_сервер_БАРС_Груп>/simple
```

* Добавьте его в ```INSTALLED_APPS``` проекта:
```
INSTALLED_APPS += ('wellbehaved',)
```
 * Расположите файлы с описанием поведения (_<имя фичи>.feature_) одним из следующих способов:
    * одна из списка папок, указанного в настройке ```WELLBEHAVED_SEARCH_DIRECTORIES```;
    * в одной из подпапок корня проекта (настройка ```PROJECT_ROOT```)
 * Запустить тестирование можно с помощью обычной команды:
```
python ./manage.py test wellbehaved
```

## Контакты

С вопросами по доработкам, применению и с сообщениями об ошибках пишите на <borisov@bars-open.ru>

## Благодарности

* Юле Касимовой (<kasimova@bars-open.ru>) - самоотверженное участие в тестировании продукта;
* Сергею Чипиге (<svchipiga@bars-open.ru>) - нахождение багов;
* Вадиму Малышеву (<vvmalyshev@bars-open.ru>) - продавливании идеи изучения концепций BDD.


## Ссылки

- [Writing Features - Gherkin Language][Writing Features]
- [Behavior Driven Development (from behave documentation)][Behavior Driven Development]
- [List of behave formatters][behave Formatters]

[Writing Features]: http://docs.behat.org/guides/1.gherkin.html
[Behavior Driven Development]: http://pythonhosted.org/behave/philosophy.html
[behave Formatters]: http://pythonhosted.org/behave/formatters.html
