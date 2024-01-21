# DI в python 
Демонстрация, зачем это нужно и почему это выгодно.

Код с зависимостями:

```python
import os

class ApiClient:

    def __init__(self) -> None:
        self.api_key = os.getenv("API_KEY")  # <-- dependency
        self.timeout = int(os.getenv("TIMEOUT"))  # <-- dependency

class Service:

    def __init__(self) -> None:
        self.api_client = ApiClient()  # <-- dependency

def main() -> None:
    service = Service()  # <-- dependency
    ...

if __name__ == "__main__":
    main()
```

Код с инъекцией зависимости. Это реализация принципа ООП "Инверсия управления".

```python
import os

class ApiClient:

    def __init__(self, api_key: str, timeout: int) -> None:
        self.api_key = api_key  # <-- dependency is injected
        self.timeout = timeout  # <-- dependency is injected

class Service:

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client  # <-- dependency is injected

def main(service: Service) -> None:  # <-- dependency is injected
    ...

if __name__ == "__main__":
    main(
        service=Service(
            api_client=ApiClient(
                api_key=os.getenv("API_KEY"),
                timeout=int(os.getenv("TIMEOUT")),
            ),
        ),
    )
```

ApiClient не зависит от того, откуда берутся опции. Вы можете прочитать ключ и таймаут из конфигурационного файла или даже получить их из базы данных.

Сервис отвязан от ApiClient. Он больше не создает его. Вы можете предоставить заглушку или другой совместимый объект.

Функция main() отделена от Service. Она получает его в качестве аргумента.
Это значительно увеличило гибкость кода. Но за гибкость приходится платить.

```python
main(
    service=Service(
        api_client=ApiClient(
            api_key=os.getenv("API_KEY"),
            timeout=int(os.getenv("TIMEOUT")),
        ),
    ),
)
```

Сборный код может дублироваться, и изменить структуру приложения станет сложнее.

# TypeVar
Предположим, что у нас объявлены два класса:

```python
class Geom: pass
class Point2D(Geom): pass
```

и некая функция, которая должна создавать экземпляры переданных ей классов, унаследованных от `Geom`:

```python
def factory_point(cls_geom):
    return cls_geom()
```

Обратите внимание, здесь предполагается, что параметр `cls_geom` будет ссылаться на сам класс, а не объект класса. Почему это важно, вы сейчас увидите. Используя текущие знания по аннотации типов, первое, что приходит в голову – это прописать в функции следующие определения:

```python
def factory_point(cls_geom: Geom) -> Geom:
    return cls_geom()
```

Но нам здесь интегрированная среда сразу подсвечивает фрагмент `cls_geom()`. Почему это произошло? Как раз по той причине, что аннотация `Geom` подразумевает, что параметр `cls_geom` будет ссылаться на объекты класса `Geom`, а не на сам класс Geom. Вот это очень важно понимать, когда вы прописываете аннотации типов. Везде подразумеваются объекты тех типов, которые указываются. Но как тогда поправить эту ситуацию? Очень просто. Для этого существует специальный тип Type из модуля `typing`. Если мы перепишем аннотацию в виде:

```python
def factory_point(cls_geom: Type[Geom]) -> Geom:
    return cls_geom()
```

то никаких нарушений уже не будет. Тем самым мы указали, что параметр `cls_geom` будет ссылаться непосредственно на класс `Geom`, а не его объекты. А далее, используя переменную `cls_geom`, создается объект этого класса и возвращается функцией.

Давайте теперь воспользуемся этой функцией. Если ее вызвать так:

```python
geom = factory_point(Geom)
point = factory_point(Point2D)
```

то с аннотациями никаких конфликтов не будет. Но, если мы дополнительно аннотируем и переменные `geom` и `point` соответствующими типами:

```python
geom: Geom = factory_point(Geom)
point: Point2D = factory_point(Point2D)
```

то во второй строчке появится подсветка кода. Очевидно это из-за того, что мы явно указываем ожидаемый тип `Point2D`, а в определении функции прописан тип `Geom`. И, так как `Geom` – базовый класса для `Point2D`, то возникает конфликт аннотаций.

Для исправления таких ситуаций в Python можно описывать некие общие типы с помощью класса TypeVar. Например:

```python
T = TypeVar("T", bound=Geom)
```

Мы здесь объявили универсальный тип с именем `T` и сказали, что он должен быть или классом `Geom` или любым его дочерним классом. Далее, в самой функции, достаточно прописать этот тип:

```python
def factory_point(cls_geom: Type[T]) -> T:
    return cls_geom()
```

и он будет автоматически вычисляться при вызове функции. Когда передается класс `Geom`, то `T` будет соответствовать этому типу, а когда передается `Point2D` – то тип `T` будет `Point2D`. И так далее. Вот смысл универсальных типов при формировании аннотаций.

Для полноты картины сразу отмечу здесь, что класс TypeVar можно использовать и в таких вариациях:

```
T = TypeVar("T")   # T – произвольный тип без ограничений
```

```
T = TypeVar("T", int, float)   # T – тип связанный только с типами int и float
```

Подробнее обо всем этом можно почитать в официальной документации. Но я не вижу большого смысла глубоко погружаться в эту тему, т.к. различные вариации данного класса используются на практике не часто.

В Pydantic, `TypeVar` используется для создания обобщенных типов. Обобщенные типы позволяют указывать параметризованные типы данных, которые могут быть использованы в различных контекстах. Вот примеры использования `TypeVar` в Pydantic:

Пример 1: Определение обобщенного типа с использованием `TypeVar`

pythonCopy Code

```python
from typing import TypeVar 
from pydantic import BaseModel  
T = TypeVar('T')  # Определение обобщенного типа 'T'  
class GenericResponse(BaseModel):     
	data: T  
response = GenericResponse[str](data="Hello, World!")  # Создание экземпляра GenericResponse с обобщенным типом str
print(response.data)  # Вывод: Hello, World!
```

В этом примере мы определяем обобщенный тип `T` с помощью `TypeVar('T')`. Затем мы создаем класс `GenericResponse`, который имеет поле `data` типа `T`. Мы можем создавать экземпляры `GenericResponse` с различными типами для `data`.

Пример 2: Использование `TypeVar` в качестве аргументов функции

pythonCopy Code

```python
from typing import Callable, TypeVar 
from pydantic import BaseModel  
T = TypeVar('T')  

def process_data(data: T, callback: Callable[[T], T]) -> T:     return callback(data)  

def double_value(value: int) -> int:     
	return value * 2  

input_data = 5 
result = process_data(input_data, double_value) 
print(result)  # Вывод: 10
```

В этом примере мы определяем функцию `process_data`, которая принимает обобщенный аргумент `data` и обратный вызов `callback`. Мы передаем `input_data` в `process_data`, а также функцию `double_value`, которая удваивает значение. Результатом будет удвоенное значение `input_data`.

Надеюсь, эти примеры помогут вам понять, как использовать `TypeVar` в Pydantic для создания обобщенных типов.

# Мета программирование

Для создания функций служит некий встроенный класс `function`. Посмотрим, что мы сможем сделать с его помощью. Для этого возьмем заготовку из встроенного модуля [types](https://docs.python.org/3/library/types.html#module-types)

```python
>>> from types import FunctionType
>>> FunctionType
<class 'function'>
>>> help(FunctionType)

class function(object)
 |  function(code, globals[, name[, argdefs[, closure]]])
 |
 |  Create a function object from a code object and a dictionary.
 |  The optional name string overrides the name from the code object.
 |  The optional argdefs tuple specifies the default argument values.
 |  The optional closure tuple supplies the bindings for free variables.
```

Давайте теперь попробуем создать новую функцию, не прибегая к её объявлению через `def`. Для этого нам потребуется научиться создавать объекты кода с помощью встроенной в интерпретатор функции [compile](https://docs.python.org/3/library/functions.html#compile):

```python
# создаем объект кода, который выводит строку "Hello, world!"
>>> code = compile('print("Hello, world!")', '<repl>', 'eval')
>>> code
<code object <module> at 0xdeadbeef, file "<repl>", line 1>
# создаем функцию, передав в конструктор объект кода, 
# глобальные переменные и название функции
>>> func = FunctionType(code, globals(), 'greetings')
>>> func
<function <module> at 0xcafefeed>
>>> func.__name__
'greetings'
>>> func()
Hello, world!
```

Отлично! С помощью мета-инструментов мы научились создавать функции «на лету», однако на практике подобное знание используется редко. Теперь давайте взглянем, как создаются объекты-классы и объекты-экземпляры этих классов:

```python
>>> class User: pass
>>> user = User()
>>> type(user)
<class '__main__.User'>
>>> type(User)
<class 'type'>
```

Вполне очевидно, что класс `User` используется для создания экземпляра `user`, намного интереснее посмотреть на класс `type`, который используется для создания самого класса `User`. Вот здесь мы и обратимся ко второму варианту вызова встроенной функции `type`, которая по совместительству является метаклассом для любого класса в Python. Метакласс по определению – это класс, экземпляром которого является другой класс. Метаклассы позволяют нам настраивать процесс создания класса и частично управлять процессом создания экземпляра класса.

Посмотрим, как можно, используя только вызов `type`, сконструировать совершенно новый класс:

```python
>>> User = type('User', (), {})
>>> User
<class '__main__.User'>
```

Как видим, нам не требуется использовать ключевое слово `class`, чтобы создать новый класс, функция `type` справляется и без этого, теперь давайте рассмотрим пример посложнее:

```python
class User:  
    def __init__(self, name):  
        self.name = name  

class SuperUser(User):  
    """Encapsulate domain logic to work with super users"""  
    group_name = 'admin'  

    @property  
    def login(self):  
        return f'{self.group_name}/{self.name}'.lower()

# Теперь создадим аналог класса SuperUser "динамически" 
CustomSuperUser = type(
    # Название класса
    'SuperUser',
    # Список классов, от которых новый класс наследуется
    (User, ),  
    # Атрибуты и методы нового класса в виде словаря
    {  
        '__doc__': 'Encapsulate domain logic to work with super users',  
        'group_name': 'admin',  
        'login': property(lambda self: f'{self.group_name}/{self.name}'.lower()),  
    }  
)  

assert SuperUser.__doc__ == CustomSuperUser.__doc__
assert SuperUser('Vladimir').login == CustomSuperUser('Vladimir').login
```

Как видно из примеров выше, описание классов и функций с помощью ключевых слов `class` и `def` – это всего лишь синтаксический сахар и любые типы объектов можно создавать обычными вызовами встроенных функций. А теперь, наконец, поговорим о том, как можно использовать динамическое создание классов в реальных проектах.

## Динамическое создание форм и валидаторов

Иногда нам требуется провалидировать информацию от пользователя или из других внешних источников согласно заранее известной схеме данных. Например, мы хотим изменять форму логина пользователя из админки – удалять и добавлять поля, менять стратегию их валидации и т.д
  
Для иллюстрации, попробуем динамически создать [Django](https://www.djangoproject.com/)-форму, описание схемы которой хранится в следующем `json` формате:

```json
{
    "fist_name": { "type": "str", "max_length": 25 }, 
    "last_name": { "type": "str", "max_length": 30 }, 
    "age": { "type": "int", "min_value": 18, "max_value": 99 }
}
```

Теперь на основе описания выше создадим набор полей и новую форму с помощью уже известной нам функции `type`:

```python
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'type_annotation.settings')
django.setup()

import json
from django import forms

fields_type_map = {
	'str': forms.CharField,
	'int': forms.IntegerField,
}

deserialized_form_description: dict = {
	"fist_name": { "type": "str", "max_length": 25 },
    "last_name": { "type": "str", "max_length": 30 },
		"age": { "type": "int", "min_value": 18, "max_value": 99 }
}

form_attrs = {}

# выбираем класс объекта поля в форме в зависимости от его типа
for field_name, field_description in deserialized_form_description.items():
     field_class = fields_type_map[field_description.pop('type')]
     form_attrs[field_name] = field_class(**field_description)

user_form_class = type('DynamicForm', (forms.Form, ), form_attrs)

form = user_form_class({'age': 101})

In [9]: form
Out[9]: <DynamicForm bound=True, valid=Unknown, fields=(fist_name;last_name;age)>

In [10]: form.is_valid()
Out[10]: False

In [11]: form.errors
Out[11]:
{'fist_name': ['This field is required.'],
 'last_name': ['This field is required.'],
 'age': ['Ensure this value is less than or equal to 99.']}
```

Супер! Теперь можно передать созданную форму в шаблон и отрендерить ее для пользователя. Такой же подход можно использовать и с другими фреймворками для валидации и представления данных ([DRF Serializers](http://www.django-rest-framework.org/api-guide/serializers/), [marshmallow](https://marshmallow.readthedocs.io/) и другие).

## Конфигурируем создание нового класса через метакласс

Выше мы рассмотрели уже «готовый» метакласс `type`, но чаще всего в коде вы будете создавать свои собственные метаклассы и использовать их для конфигурации создания новых классов и их экземпляров. В общем случае «болванка» метакласса выглядит так:

```python
class MetaClass(type):
    """
    Описание принимаемых параметров:

    mcs – объект метакласса, например <__main__.MetaClass>
    name – строка, имя класса, для которого используется 
      данный метакласс, например "User"
    bases – кортеж из классов-родителей, например (SomeMixin, AbstractUser)
    attrs – dict-like объект, хранит в себе значения атрибутов и методов класса
    cls – созданный класс, например <__main__.User>
    extra_kwargs – дополнительные keyword-аргументы переданные в сигнатуру класса
    args и kwargs – аргументы переданные в конструктор класса 
      при создании нового экземпляра
    """
    def __new__(mcs, name, bases, attrs, **extra_kwargs):
        return super().__new__(mcs, name, bases, attrs)  

    def __init__(cls, name, bases, attrs, **extra_kwargs):  
        super().__init__(cls)  

    @classmethod  
    def __prepare__(mcs, cls, bases, **extra_kwargs):  
        return super().__prepare__(mcs, cls, bases, **kwargs)  

    def __call__(cls, *args, **kwargs):  
        return super().__call__(*args, **kwargs)
```

Чтобы воспользоваться этим метаклассом для конфигурации класса `User`, используется следующий синтаксис:

```python
class User(metaclass=MetaClass):

    def __new__(cls, name):  
        return super().__new__(cls)  

    def __init__(self, name):  
        self.name = name
```

Самое интересное – это порядок, в котором интерпретатор Python вызывает метаметоды метакласса в момент создания самого класса:

1. Интерпретатор определяет и находит классы-родители для текущего класса (если они есть).
2. Интерпретатор определяет метакласс (`MetaClass` в нашем случае).
3. Вызывается метод `MetaClass.__prepare__` – он должен возвратить dict-like объект, в который будут записаны атрибуты и методы класса. После этого объект будет передан в метод `MetaClass.__new__` через аргумент `attrs`. О практическом использовании этого метода мы поговорим немного позже в примерах.
4. Интерпретатор читает тело класса `User` и формирует параметры для передачи их в метакласс `MetaClass`.
5. Вызывается метод `MetaClass.__new__` – метод-коструктор, возвращает созданный объект класса. C аргументами `name`, `bases` и `attrs` мы уже встречались, когда передавали их в функцию `type`, а о параметре `**extra_kwargs` мы поговорим немного позже. Если тип аргумента `attrs` был изменен с помощью `__prepare__`, то его необходимо конвертировать в `dict`, прежде чем передать в вызов метода `super()`.
6. Вызывается метод `MetaClass.__init__` – метод-инициализатор, с помощью которого в класс можно добавить дополнительные атрибуты и методы в объект класса. На практике используется в случаях, когда метаклассы наследуются от других метаклассов, в остальном все что можно сделать в `__init__`, лучше сделать в `__new__`. Например параметр `__slots__` можно задать **только** в методе `__new__`, записав его в объект `attrs`.
7. На этом шаге класс считается созданным.

  

А теперь создадим экземпляр нашего класса `User` и посмотрим на цепочку вызовов:

```python
user = User(name='Alyosha')
```

1. В момент вызова `User(...)` интерпретатор вызывает метод `MetaClass.__call__(name='Alyosha')`, куда передает объект класса и переданные аргументы.
2. `MetaClass.__call__` вызывает `User.__new__(name='Alyosha')` – метод-конструктор, который создает и возвращает экземпляр класса `User`
3. Далее `MetaClass.__call__` вызывает `User.__init__(name='Alyosha')` – метод-инициализатор, который добавляет новые атрибуты к созданному экземпляру.
4. `MetaClass.__call__` возвращает созданный и проинициализированный экземпляр класса `User`.
5. В этот момент экземпляр класса считается созданным.

Это описание, конечно, не покрывает все нюансы использования метаклассов, но его достаточно, чтобы начать применять метапрограммирование для реализации некоторых архитектурных паттернов. Вперед – к примерам!

## Абстрактные классы

И самый первый пример можно найти в стандартной библиотеке: [ABCMeta](https://docs.python.org/3/library/abc.html#abc.ABCMeta) – метакласс позволяет объявить любой наш класс абстрактным и заставить всех его наследников реализовывать заранее заданные методы, свойства и атрибуты, вот посмотрите:

```python
from abc import ABCMeta, abstractmethod  

class BasePlugin(metaclass=ABCMeta):  
    """
    Атрибут класса supported_formats и метод run обязаны быть реализованы
    в наследниках этого класса
    """
    @property  
    @abstractmethod  
    def supported_formats(self) -> list:  
        pass  

    @abstractmethod  
    def run(self, input_data: dict):  
        pass  
```

Если в наследнике не будут реализованы все абстрактные методы и атрибуты, то при попытке создать экземпляр класса-наследника мы получим `TypeError`:

```python
class VideoPlugin(BasePlugin):  

    def run(self):  
        print('Processing video...')

plugin = VideoPlugin()
# TypeError: Can't instantiate abstract class VideoPlugin 
# with abstract methods supported_formats
```

Использование абстрактных классов помогает сразу зафиксировать интерфейс базового класса и избежать ошибок при наследовании в будущем, например опечатки в названии переопределенного метода.

## Система плагинов с автоматической регистрацией

Достаточно часто метапрограммирование применяют для реализации различных паттернов проектирования. Почти любой известный фреймворк использует метаклассы для создания [registry](https://martinfowler.com/eaaCatalog/registry.html)-объектов. Такие объекты хранят в себе ссылки на другие объекты и позволяют их быстро получать в любом месте программы. Рассмотрим простой пример авторегистрации плагинов для проигрывания медиафайлов различных форматов.

Реализация метакласса:

```python
class RegistryMeta(ABCMeta):
    """
    Метакласс, который создает реестр из классов наследников.
    Реестр хранит ссылки вида "формат файла" -> "класс плагина"
    """
    _registry_formats = {}  

    def __new__(mcs, name, bases, attrs):  
        cls: 'BasePlugin' = super().__new__(mcs, name, bases, attrs)  

        # не обрабатываем абстрактные классы (BasePlugin)
        if inspect.isabstract(cls):  
            return cls  

        for media_format in cls.supported_formats:  
            if media_format in mcs._registry_formats:  
                raise ValueError(f'Format {media_format} is already registered')

            # сохраняем ссылку на плагин в реестре
            mcs._registry_formats[media_format] = cls  

        return cls  

    @classmethod  
    def get_plugin(mcs, media_format: str):  
        try:  
            return mcs._registry_formats[media_format]  
        except KeyError:  
            raise RuntimeError(f'Plugin is not defined for {media_format}')  

    @classmethod  
    def show_registry(mcs):  
        from pprint import pprint  
        pprint(mcs._registry_formats)  
```

А вот и сами плагины, реализацию `BasePlugin` возьмем из предыдущего примера:

```python
class BasePlugin(metaclass=RegistryMeta):
    ...

class VideoPlugin(BasePlugin):  
    supported_formats = ['mpg', 'mov']  
    def run(self): ...

class AudioPlugin(BasePlugin):  
    supported_formats = ['mp3', 'flac']  
    def run(self): ...
```

После выполнения этого кода интерпретатором в нашем реестре будут зарегистрированы 4 формата и 2 плагина, которые могут обрабатывать эти форматы: 

```python
>>> RegistryMeta.show_registry()
{'flac': <class '__main__.AudioPlugin'>,
 'mov': <class '__main__.VideoPlugin'>,
 'mp3': <class '__main__.AudioPlugin'>,
 'mpg': <class '__main__.VideoPlugin'>}
>>> plugin_class = RegistryMeta.get_plugin('mov')
>>> plugin_class
<class '__main__.VideoPlugin'>
>>> plugin_class().run()
Processing video...
```

Тут стоит отметить еще один интересный нюанс работы с метаклассами, благодаря неочевидному method resolution order, мы можем вызвать метод `show_registry` не только у класса `RegistyMeta`, но и у любого другого класса метаклассом которых он является:

```python
>>> AudioPlugin.get_plugin('avi')
# RuntimeError: Plugin is not found for avi
```
