# Wellbehaved

Обертка вокруг питоновского проекта behave, позволяющая автоматически прогонять feature-файлы в качестве тестов.

## Установка и использование

1. Установите пакет *wellbehaved* со стандартного PyPi-сервера "БАРС Груп":
```
pip install wellbehaved -i https://<PyPi_сервер_БАРС_Груп>/simple
```
2. Добавьте его в INSTALLED_APPS проекта:
```
INSTALLED_APPS += ('wellbehaved',)
```
3. Расположите файлы с описанием поведения (_<имя фичи>.feature_) в папках, название которых заканчивается на _features_.
4. Запустить тестирование можно с помощью обычной компанды:
```
python ./manage.py test wellbehaved
```

## Принцип работы

При запуске тестирования _wellbehaved_ обходит все поддиректории в корне проекта (местоположение _manage.py_) и ищет в них
папки _features_. Каждая найденная папка будет представлена отдельным набором тестов, в котором каждый файл с расширением 
_.feature_ будет обернут в класс **DjangoBDDTestCase**.

Для каждого модуля с папкой features создается отдельный метод:
```test_имяфайла_feature```. Таким образом, вы можете протестировать
единичную функцию системы:

	+ core
	    |
	    +- features
	              |
	              + - core_func.feature

	python ./manage.py test wellbehaved.DjangoBDDTestCase.test_core_func_feature


## Настройки

Настройки являются необязательными считываются из ```settings.py``` проекта:

1. ```WELLBEHAVED_USE_EXISTING_DB``` - использовать для тестирования существующую базу, используется вместе с 
```TEST_RUNNER = 'wellbehaved.runner.ExistingDBRunner'```

2. ```WELLBEHAVED_INITIAL_FIXTURES``` - список фикстур, который будет загружен каждым тестом. Обычно ииспользуется для занесения общих значений в справочники и по формату аналогичен аттрибуту _fixtures_ в _TestCase_.

3. ```WELLBEHAVED_FORMATTER``` - модуль форматирования, используемый _behave_ для вывода результатов. Возможные варианты описаны в [списке модулей форматирования behave][behave Formatters], по умолчанию стоит ```[pretty]```.

4. ```WELLBEHAVED_LANG``` - код языка, на котором написано описание функционала. По умолчанию стоит ```'ru'```.


## Gherkin

(здесь и далее - перевод и легкая адаптация статьи ["Writing Features - Gherkin Language"][Writing Features])

**Gherkin** - человеко-читаемый язык для описания поведения системы, который использует отступы для задания структуры документа,
(пробелы или символы табуляции). Каждая строчка начинается с одного из ключевых слов и описывает один из шагов.

Пример:

	Функция: Короткое, но исчерпывающее описание требуемого функционала
		Для того, чтобы достичь определенных целей
		В качестве определенного участника взаимодействия с системой
		Я хочу получить определенную пользу

		Сценарий: Какая-то определенная бизнес-ситуация
			Дано какое-то условие
			И ещё одно условие
			Когда предпринимается какое-то действие участником
			И им делается ещё что-то
			И вдобавок он совершил что-то ещё
			То получается какой-то проверяемый результат
			И что-то ещё случается, что мы можем проверить


Обработчик разбивает файл с тестами на функции, сценарии и входящие в них шаги. Давайте разберем 
этот пример:

1. Строка **Функция: Короткое, но исчерпывающее описание требуемого функционала** начинает собой
описание функционала и дает ему название.

2. Следующие три строчки не обрабатываются и не несут никакой смысловой нагрузке для обработчика тестов,
но они задают контекст тестирования и одновременно описывают, какую пользу мы получим от этого функционала.

3. Строка **Сценарий: Какая-то определенная бизнес-ситуация** начинает сценарий и содержит его описание.

4. Следующие 7 строчек описывают шаги теста, каждому из которых впоследствии
будет сопоставлен определенный программный код, выполняющий описанное действие.
Сопоставлению подлежат части строк лежащие после ключевых слов "Дано", "И", "Когда" и т.д.

### Функции (Feature)

Каждая функция описывается в отдельном файле с расширением _.feature_. Первая строчка
должна начинаться с ключевого слова "Функция:", за которой могут идти три строчки с описанием,
размеченные отступами. Каждая функция обычно состоит из списка сценариев. 

Каждый сценарий состоит из списка *шагов*, каждый из которых должен начинаться с одного из ключевых слов:

- Дано
- Когда
- То
- Но
- И

Шаги _"Но"_ и _"И"_ существуют исключительно для удобства чтения и по своим функциям повторяют ключевое слово,
с которого начиналась предыдущая строчка.

Вдобавок к сценариям, описание функционала может также содержать _структуры сценариев_ и _предыстории_.

### Сценарий (Scenario)

Сценарий представляет собой одну из ключевых структур в языке _Gherkin_. Каждый сценарий начинается
с ключевого слова **"Сценарий:"**, и может содержать в себе название сценария. Описание функционала
может содержать в себе один или больше сценариев, и каждый сценарий состоит из одного или более шага.

Каждый из следующих сценариев содержит три шага:

	Сценарий: Вася создает новую запись
		Дано я вошел в систему как Вася
		Когда я пытаюсь добавить запись в справочник "Лекарства"
		То мне должен быть ответ "Ваша запись успешно добавлена."

	Сценарий: Вася не может добавлять запись в справочник лечений
		Дано я вошел в систему как Вася
		Когда я пытаюсь добавить запись в справочник "Виды лечений"
		То мне должен быть ответ "У вас нет прав доступа!"


### Структура сценария (Scenario Outline)

Достаточно часто приходится писать множество мелких сценариев, которые различаются буквально парой
переменных. Эти повторения могут быстро надоесть:

	Сценарий: удалить 5 записей из 12
		Дано есть 12 записей
		Когда я удаляю 5 записей
		То у меня должно остаться 7 записей

	Сценарий: удалить 5 записей из 20
		Дано есть 20 записей
		Когда я удаляю 5 записей
		То у меня должно остаться 15 записей

Структуры сценариев позволяют нам более кратко описывать подобные наборы сценариев
с помощью шаблонов:

	Структура сценария: удаление записей
		Дано есть <было> записей
		Когда я удаляю <удалено> записей
		То у меня должно остаться <остаток> записей

		Примеры:
			| было	| удалено | остаток |
			| 12	|    5    |   7     |
			| 20    |    5    |   15    |


Шаги указанные в структуре сценария не выполняются напрямую, но используются 
для подстановки в них значений из таблицы примеров. Каждая строчка таблицы
будет обрабатываться как отдельный сценарий с указанными значениями вместо
заглушек "было", "удалено" и "стало".

### Предыстории (Background)

Предыстории позволяют вам добавить определенный контекст ко всем сценариям в 
пределах функции. По сути, предыстория - сценарий без имени, состоящий из
шагов. Основное отличие в запуске: предыстория запускается перед каждым
сценарием:


	Функция: поддержка многих справочников

		Предыстория:
			Дано есть пользователь с именем "Вася"
			И есть справочник "Лекарства"
			И у пользователя "Вася" есть право на запись в  "Лекарство"
			И есть справочник "Виды лечений"

		Сценарий: Вася создает новую запись
			Дано я вошел в систему как Вася
			Когда я пытаюсь добавить запись в справочник "Лекарства"
			То мне должен быть ответ "Ваша запись успешно добавлена."

		Сценарий: Вася не может добавлять запись в справочник лечений
			Дано я вошел в систему как Вася
			Когда я пытаюсь добавить запись в справочник "Виды лечений"
			То мне должен быть ответ "У вас нет прав доступа!"


### Шаги

Функции состоят из шагов, также известных как _Данные_, _Действия_ и _Результаты_.

#### Данные (Givens)

Назначение шагов _Дано_ состоит в **приведение системы в известное состояние**
перед тем как пользователь (или внешняя система) начнет взаимодействие с системой
(в шагах _Когда_). Также можно рассматривать их как предусловия.

Пример: создавать объекты сущностей или настраивать БД

	Дано нет пользователей в базе
	Дано база данных пустая

Пример: вход пользователя в систему (исключение к правилу "никаких взаимодействий в шаге Дано")

	Дано я вошел в систему как "Вася"


#### Действия (Whens)

Назначение шагов _Когда_ состоит в **описании ключевого действия, совершаемого пользователем**.

Пример: взаимодействие со страницей

	Когда я открыл форму добавления учреждения
	Когда я ввел "Институт радости" в поле "Наименование"
	Когда я выбрал в поле "Тип" значение "Институт"
	Когда я нажал на кнопку "Сохранить"


#### Результаты (Thens)

Назначение шагов _То_ состоит в **наблюдении результатов выполнения действий**. Наблюдения должны быть связаны с явной пользой, которая указаны в описании функции. Также необходимо помнить, что должен проверяться _вывод системы_ (отчеты, интерфейс, сообщения), а не что-то глубоко закопанное в систему.

Хорошие советы:

- Удостоверьтесь что нечто относящееся к содержимому шагов _Дано+Когда_ содержится в выводе системы
- Проверьте, что какая-либо внешняя системе получила отправленное сообщение с ожидаемым содержимым


#### Предлоги (And, But)

Если у вас есть несколько шагов _Дано_, _Когда_, или _То_
то вы можете писать так:

	Сценарий: множественные данные
		Дано что-то первое
		Дано что-то второе
		Дано и что-то ещё
		Когда я открою свои глаза
		То я увижу что-то
		То чего-то я не увижу


...или можете использовать шаги _И_ и _Но_, превращая свой сценарий в нечто более читаемое:


	Сценарий: множественные данные
		Дано что-то первое
		И что-то второе
		И и что-то ещё
		Когда я открою свои глаза
		То я увижу что-то
		Но чего-то я не увижу


#### Таблицы

Регулярные выражения, с помощью которых программисты получают
данные из текстового описания шагов позволяют получать небольшие куски данных из самой строчки. Но бывает и такое, что необходимо передать больший объем данных в один шаг. И здесь нам на помощь придут таблицы:


	Сценарий:
		Дано существуют следующие пользователи:
			| Логин | E-mail        | Пароль |
			| user1 | user1@mail.ru | pass1  |
			| joe   | joe@gmail.com | hey    |
			| heyho | hey@hoe.com   | joe    |


## Контакты

С вопросами по доработкам, применению и с сообщениями об ошибках пишите на <borisov@bars-open.ru>

## Благодарности

* Юле Касимовой (<kasimova@bars-open.ru>) - самоотверженное участие в тестировании продукта;
* Вадиму Малышеву (<vvmalyshev@bars-open.ru>) - продавливании идеи изучения концепций BDD.


## Ссылки

- [Writing Features - Gherkin Language][Writing Features]
- [Behavior Driven Development (from behave documentation)][Behavior Driven Development]
- [List of behave formatters][behave Formatters]

[Writing Features]: http://docs.behat.org/guides/1.gherkin.html
[Behavior Driven Development]: http://pythonhosted.org/behave/philosophy.html
[behave Formatters]: http://pythonhosted.org/behave/formatters.html