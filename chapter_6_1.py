# ======================================================================================================================
# 합성 가능한 클래스 확장이 필요하면 메타클래스보다는 클래스 데코레이터를 사용해라.

# 메타클래스를 사용하면 클래스 생성을 다양한 방법으로 커스텀화할 수 있지만, 여전히 메타클래스로 처리할 수 없는 경우가 있다.
# 예를 들어 어떤 클래스의 모든 메서드를 감싸서 메서드에 전달되는 인자, 반환 값, 발생한 예외를 모두 출력하고 싶다고 하자.
# 다음 코드는 이런 디버깅 데코레이터를 정의한다.
from functools import wraps

def trace_func(func):
    if hasattr(func, 'tracing'):  # 단 한번만 데코레이터를 적용한다
        return func

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = None
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            result = e
            raise
        finally:
            print(f'{func.__name__}({args!r}, {kwargs!r}) -> '
                  f'{result!r}')

    wrapper.tracing = True
    return wrapper

# 다음과 같이 이 데코레이터를 새 dict 하위 클래스에 속한 여러 특별 메소드에 적용할 수 있다.
class TraceDict(dict):
    @trace_func
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @trace_func
    def __setitem__(self, *args, **kwargs):
        return super().__setitem__(*args, **kwargs)

    @trace_func
    def __getitem__(self, *args, **kwargs):
        return super().__getitem__(*args, **kwargs)

# 이 클래스의 인스턴스와 상호작용해보면 메서드가 잘 데코레이션됐는지 확인할 수 있다.
def use_decorater():
    trace_dict = TraceDict([('안녕', 1)])
    trace_dict['거기'] = 2
    trace_dict['안녕']
    try:
        trace_dict['존재하지 않음']
    except KeyError:
        pass # 키 오류가 발생할 것으로 예상함

# 이 코드의 문제점은 꾸미려는 모든 메서드를 @trace_func 데코레이터로 재정의해야한다는 것이다.
# 이런 불필요한 중복으로 인해 가동석도 나빠지고, 실수를 저지르기도 쉬워진다.
# 더 나아가 나중에 dict 상위 클래스에 메서드를 추가하면, TraceDict에서 그 메서드를 재정의하기 전까지는 데코레이터 적용이 되지 않는다.

# 이 문제를 해결하는 방법은 메타클래스를 사용해 클래스에 속한 모든 메서드를 자동으로 감싸는 것이다.
# 다음 코드는 새로 정의되는 타입의 모든 함수나 메서드를 trace_func 데코레이터로 감싸는 동작을 구현한다.
import types

trace_types = (
    types.MethodType,
    types.FunctionType,
    types.BuiltinFunctionType,
    types.BuiltinMethodType,
    types.MethodDescriptorType,
    types.ClassMethodDescriptorType)


class TraceMeta(type):
    def __new__(meta, name, bases, class_dict):
        klass = super().__new__(meta, name, bases, class_dict)

        for key in dir(klass):
            value = getattr(klass, key)
            if isinstance(value, trace_types):
                wrapped = trace_func(value)
                setattr(klass, key, wrapped)

        return klass

# 다음 코드는 TraceMeta 메타클래스를 사용해 dict 하위 클래스를 정의하고, 해당 클래스가 잘 작동하는지 확인한다.
class TraceDict(dict, metaclass=TraceMeta):
    pass

def use_decorater_2():
    trace_dict = TraceDict([('안녕', 1)])
    trace_dict['거기'] = 2
    trace_dict['안녕']
    try:
        trace_dict['존재하지 않음']
    except KeyError:
        pass # 키 오류가 발생할 것으로 예상함

# 하지만 라이브러리에 있는 메타클래스를 사용하는 경우에는 코드를 변경할 수 없기 때문에 이 방법을 사용할 수 없다.
# 또한, TraceMeta 같은 유틸리티 메타클래스를 여럿 사용하고 싶은 경우에도 사용할 수 없다. 메타클래스를 사용하는 접근 방식은
# 적용 대상 클래스에 대한 제약이 너무 많다.

# 이런 문제를 해결하고자 파이썬은 클래스 데코레이터를 지원한다. 클래스 데코레이터는 함수 데코레이터처럼 사용할 수 있다.
# 즉 클래스 선언 앞에 @기호화 데코레이터 함수를 적으면 된다. 이때 데코레이터 함수는 인자로 받은 클래스를 적절히 변경해서 재생성해야 한다.
def my_class_decorator(klass):
    klass.extra_param = '안녕'
    return klass

@my_class_decorator
class MyClass:
    pass

# 앞의 예제에서 본 TraceMeta.__new__ 메서드의 핵심 부분을 별도의 함수로 옮겨서 어떤 클래스에 속한 모든 메서드와 함수에 trace_func를
# 적용하는 클래스 데코레이터를 만들 수 있다. 이 구현은 메타클래스를 사용하는 버전보다 훨씬 짧다.
def trace(klass):
    for key in dir(klass):
        value = getattr(klass, key)
        if isinstance(value, trace_types):
            wrapped = trace_func(value)
            setattr(klass, key, wrapped)
    return klass

# 이 데코레이터를 우리가 만든 dict의 하위 클래스에 적용하면 앞에서 메타클래스를 썼을 때와 같은 결과를 얻을 수 있다.
@trace
class TraceDict(dict):
    pass

def use_decorater_better():
    print(MyClass)
    print(MyClass.extra_param)

    trace_dict = TraceDict([('안녕', 1)])
    trace_dict['거기'] = 2
    trace_dict['안녕']
    try:
        trace_dict['존재하지 않음']
    except KeyError:
        pass # 키 오류가 발생할 것으로 예상함

# 데코레이션을 적용할 클래스에 이미 메타클래스가 있어도 데코레이터를 사용할 수 있다.
class OtherMeta(type):
    pass

@trace
class TraceDict(dict, metaclass=OtherMeta):
    pass

# 클래스를 확장하면서 합성이 가능한 방법을 찾고 있다면 클래스 데코레이터가 가장 적합한 도구다.
# ======================================================================================================================
# __set_name__으로 클래스 애트리뷰트를 포시하라

# 메타클래스를 통해 사용할 수 있는 유용한 기능이 한 가지 더 있다.
# 클래스가 정의된 후 클래스가 실제로 사용되기 이전인 시점에 프로퍼티를 변경하거나 표시할 수 있는 기능이다.
# 애트리뷰트가 포함된 클래스 내부에서 애트리뷰트 사용을 좀 더 자세히 관찰하고자 디스크립터를 쓸 때 이런 접근 방식을 활용한다.

# 예를 들어 고객 데이터의 row를 표현하는 새 클래스를 정의한다고 하자.
# 데이터베이스 테이블의 각 column에 해당하는 프로퍼티를 클래스에 정의하고 싶다.
# 다음 코드는 애트리뷰트와 컬럼 이름을 연결하는 디스크립터(__get__, __set__, _delete__가 하나이상 구현된 클래스) 클래스다.

# 컬럼 이름을 Field 디스크립터에 저장하고나면, setattr 내장함수를 사용해 인스턴스별 상태를 직접 인스턴스 딕셔너리에 저장할 수 있고,
# 나중에 getattr로 인스턴스의 상태를 읽을 수 있다. 처음에는 메모리 누수를 막기 위해 weakref 내장모듈을 사용하는 것보다 이 방식이 훨씬 편리해보인다.
class Field:
    def __init__(self, name):
        self.name = name
        self.internal_name = '_' + self.name

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, '')

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)

# row를 표현하는 클래스를 정의하려면 애트리뷰트별로 해당 컬럼 이름을 지정하면된다.
class Customer:
    # 클래스 애트리뷰트
    first_name = Field('first_name')
    last_name = Field('last_name')
    prefix = Field('prefix')
    suffix = Field('suffix')

def use_set_name():
    # 이 클래스를 사용하기는 쉽다. 예상한 것처럼 Field 디스크립터가 __dict__ 인스턴스 딕셔너리를 변화시킨다.
    cust = Customer()
    print(f'이전: {cust.first_name!r} {cust.__dict__}')
    cust.first_name = '유클리드'
    print(f'이후: {cust.first_name!r} {cust.__dict__}')

# 하지만 위 클래스 정의는 중복이 많아보인다. 클래스 안에서 필드 이름을 이미 정의했는데(field_name=), 굳이 같은 정보가 들어있는 문자열을
# 다시 Field 디스크립터에게 전달(Field('first_name'))해야 할 이유가 없다.
# class Customer:
#     = 좌변과 우변의 정보가 중복된다.
#     first_name = Field('first_name')

# 문제는 우리가 Customer 클래스 정의를 읽을 때는 애트리뷰트 정의를 왼쪽에서 오른쪽으로 읽지만, 파이썬이 실제로 Customer 클래스 정의를
# 처리하는 순서는 이와 반대라는 점이다. 파이썬은 먼저 Field('first_name')을 통해 Field 생성자를 호출하고, 반환된 값을
# Customer.field_name에 등록한다. Field 인스턴스가 자신이 대입된 클래스의 애트리뷰트 이름을 알 방법은 없다.

# 이런 중복을 줄이기 위해 메타클래스를 사용할 수 있다. 메타클래스를 사용하면 class 문에 직접 훅을 걸어서 class 본문이 끝나자마자 필요한 동작을 수행할 수 있다.
# 앞의 예제의 경우, 필드 이름을 여러번 수동으로 지정하는 대신 메타클래스를 사용해 디스크립터의 Field.name과 Filed.internal_name을 자동대입할 수 있다.
class Meta(type):
    def __new__(meta, name, bases, class_dict):
        for key, value in class_dict.items():
            if isinstance(value, Field):
                value.name = key
                value.internal_name = '_' + key
        cls = type.__new__(meta, name, bases, class_dict)
        return cls

# 다음 코드는 메타클래스를 사용하는 기반 클래스 정의다. 데이터베이스 로우를 표현하는 모든 클래스는 기반 클래스를 상속해 메타클래스를 사용해야한다.
class DatabaseRow(metaclass=Meta):
    pass

# 메타클래스를 사용하기위해 Field 디스크립터에서 바꿔야 할 부분이 많지는 않다. 유일하게 달라진 부분은 생성자 인자가 없다는 점뿐이다.
# 생성자가 컬럼 이름을 받는 대신, 앞에서 본 Meta.__new__ 메서드가 애트리뷰트를 설정해준다.
class Field:
    def __init__(self):
        # 이 두 정보를 메타클래스가 채워 준다
        self.name = None
        self.internal_name = None

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, '')

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)

# 메타클래스와 새 DatabaseRow 기반클래스와 새 Field 디스크립터를 사용한 결과 이전과 달리 중복이 없어졌다.
# 새 클래스의 동작은 예전 클래스와 동일하다.
class BetterCustomer(DatabaseRow):
    first_name = Field()
    last_name = Field()
    prefix = Field()
    suffix = Field()

# 다만 이 접근 방법의 문제점은 DatabaseRow를 상속하는 것을 잊어버리거나 클래스 계층 구조로 인한 제약 때문에 어쩔 수 없이 DatabaseRow를
# 상속할 수 없는 경우, 정의하는 클래스가 Field 클래스를 프로퍼티에 사용할 수 없다는 것이다. DatabaseRow를 상속하지 않으면 코드가 깨진다.
class BrokenCustomer:
    first_name = Field()
    last_name = Field()
    prefix = Field()
    suffix = Field()

# 오류가 나는 부분. 오류를 보고 싶으면 커멘트를 해제할것
# cust = BrokenCustomer()
# cust.first_name = '메르센'

# 이 문제를 해결하는 방법은 디스크립터에 __set_name__ 특별 메서드를 사용하는 것이다.
# 클래스가 정의될 때마다 파이썬은 해당 클래스 안에 들어 있는 디스크립터 인스턴스의 __set_name__을 호출한다.
# __set_name__은 디스크립터 인스턴스를 소유 중인 클래스와 디스크립터 인스턴스가 대입될 애트리뷰트 이름을 인자로 받는다.
# 다음 코드는 앞의 예제에서 Meta.__new__가 하던 일을 디스크립터의 __set_name__에서 처리한다.
class Field:
    def __init__(self):
        self.name = None
        self.internal_name = None

    def __set_name__(self, owner, name):
        # 클래스가 생성될 때 모든 스크립터에 대해 이 메서드가 호출된다
        self.name = name
        self.internal_name = '_' + name

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, '')

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)

# 이제는 특정 기반 클래스를 상속하거나 메타클래스를 사용하지 않아도 Filed 디스크립터가 제공하는 기능을 모두 활용할 수 있다.
class FixedCustomer:
    first_name = Field()
    last_name = Field()
    prefix = Field()
    suffix = Field()

def use_set_name_better():
    cust = FixedCustomer()
    print(f'이전: {cust.first_name!r} {cust.__dict__}')
    cust.first_name = '메르센'
    print(f'이후: {cust.first_name!r} {cust.__dict__}')



# ======================================================================================================================
# __init_subclass__를 사용해 클래스 확장을 등록하라

# 메타클래스의 다른 용례로 프로그램이 자동으로 타입을 등록하는 것이 있다.
# 간단한 식별자를 이용해 그에 해당하는 클래스를 찾는 역검색을 하고 싶을 때 이런 등록 기능이 유용하다.
# 예를 들어 파이썬 object를 JSON으로 직렬화하는 방식을 구현한다고 하자.

import json

class Serializable:
    def __init__(self, *args):
        self.args = args

    def serialize(self):
        return json.dumps({'args': self.args})

# 위 클래스를 통해 간단한 불변 데이터 구조를 쉽게 직렬화할 수 있다.
class Point2D(Serializable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Point2D({self.x}, {self.y})'

# 이제 JSON 문자열을 역직렬화해서 문자열이 표현하는 Point2D 객체를 구성해야한다.
# 다음 코드는 Serializable을 부모 클래스로 하며, 이 부모 클래스를 활용해 데이터를 역직렬화하는 다른 클래스를 보여준다.
class Deserializable(Serializable):
    @classmethod
    def deserialize(cls, json_data):
        params = json.loads(json_data)
        return cls(*params['args'])

class BetterPoint2D(Deserializable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y

    def __repr__(self):
        return f'BetterPoint2D({self.x}, {self.y})'


def use_subclass_more():
    # 직렬화
    point = Point2D(5, 3)
    print('객체:', point)
    print('직렬화한 값:', point.serialize())

    # 역직렬화
    before = BetterPoint2D(5, 3)
    print('이전: ', before)
    data = before.serialize()
    print('직렬화한 값:', data)
    after = BetterPoint2D.deserialize(data)
    print('이후: ', after)


# 위 접근방식은 직렬화할 데이터의 타입(Point2D, BetterPoint2D 등)을 미리 알고있는 경우에만 사용할 수 있다는 문제가 있다.
# JSON으로 직렬화할 클래스가 아주 많더라도 JSON 문자열을 적당한 object로 역직렬화하는 함수는 하나만 있는 게 이상적이다.
# 이런 공통함수를 만들고자 객체 클래스의 이름을 직렬화해 JSON 데이터에 포함시킬 수 있다.
class BetterSerializable:
    def __init__(self, *args):
        self.args = args

    def serialize(self):
        return json.dumps({
            'class': self.__class__.__name__,
            'args': self.args,
        })

    def __repr__(self):
        name = self.__class__.__name__
        args_str = ', '.join(str(x) for x in self.args)
        return f'{name}({args_str})'


# 그러면 클래스 이름을 객체 생성자로 다시 연결해주는 매핑을 유지할 수 있다.
# 매핑을 사용해 구현한 일반적인 deserialize 함수는 register_class를 통해 등록된 모든 클래스에 대해 잘 작동한다.
registry = {}

def register_class(target_class):
    registry[target_class.__name__] = target_class

def deserialize(data):
    params = json.loads(data)
    name = params['class']
    target_class = registry[name]
    return target_class(*params['args'])


# deserialize가 항상 제대로 작동하려면 나중에 역직렬화할 모든 클래스에서 register_class를 호출해야한다.
class EvenBetterPoint2D(BetterSerializable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y

def use_subclass_better():
    register_class(EvenBetterPoint2D)

    # 이제 임의의 JSON 문자열이 표현하는 클래스를 알지 못하더라도 해당 문자열을 역직렬화할 수 있다.
    # 다만 이 방식의 문제점은 register_class 호출을 잊어버릴 수 있다는 것이다. 나중에 등록을 잊어버린 클래스의 인스턴스를 역직렬화
    # 하려고 시도하면 프로그램이 깨진다.
    before = EvenBetterPoint2D(5, 3)
    print('이전: ', before)
    data = before.serialize()
    print('직렬화한 값:', data)
    after = deserialize(data)
    print('이후: ', after)


class Point3D(BetterSerializable):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.x = x
        self.y = y
        self.z = z

# 오류 발생
# point = Point3D(5, 9, -4)
# data = point.serialize()
# deserialize(data)

# BetterSerializable의 하위클래스를 정의했음에도, 클래스 정의 다음에 register_class를 호출하는 걸 잊어버리면 BetterSerializable의
# 기능을 제대로 활용할 수 잇다. 이런 접근방식은 실수하기 쉬운데 데코레이터도 마찬가지로 호출을 잊어버리는 실수를 저지를 수 있다.

# 프로그래머가 BetterSerializable을 사용한다는 의도를 감지하고 적절한 동작을 수해항상 register_class를 호출해줄 수 있다면 어떨까?
# Better_way 48에 이런 기능을 살펴봤다.
class Meta(type):
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        register_class(cls)
        return cls

# 이제 RegisteredSerializable의 하위클래스를 정의할 떄 register_class가 호출되고 deserializer가 항상 제대로 작동한다고 확신할 수 있다.
class RegisteredSerializable(BetterSerializable, metaclass=Meta):
    pass

class Vector3D(RegisteredSerializable):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.x, self.y, self.z = x, y, z

# 더 좋은 방법은 __init_subclass__를 사용하는 거다.
class BetterRegisteredSerializable(BetterSerializable):
    def __init_subclass__(cls):
        super().__init_subclass__()
        register_class(cls)


class Vector1D(BetterRegisteredSerializable):
    def __init__(self, magnitude):
        super().__init__(magnitude)
        self.magnitude = magnitude

def use_best_way():
    before = Vector1D(6)
    print('이전: ', before)
    data = before.serialize()
    print('직렬화한 값:', data)
    print('이후: ', deserialize(data))



# ======================================================================================================================
# __init_subclass__를 사용해 하위 클래스를 검증하라

# 메타클래스의 가장 간단한 활용법 중 하나는 어떤 클래스가 제대로 구현됐는지 검증하는 것이다.
# 복잡한 클래스 계층을 설계할 때 어떤 스타일을 강제로 지키도록 만들거나, 메서드를 오버라이드하도록 요청하거나 클래스 애트리뷰트 사이에
# 엄격한 관계를 가지도록 요구할 수 있다.
# 메타클래스는 이런 목적을 달성할 수 있다. 새로운 하위 클래스가 정의될 때마다 검증 코드를 수행하는 방법을 제공하기 때문이다.

# 어떤 클래스 타입의 객체가 생성될 떄 검증 코드를 __init__안에서 실행하는 경우도 종종있다. (Better way 참조)
# 검증에 메타클래스를 사용하면, 프로그램 시작 시 클래스가 정의된 모듈을 처음 임포트할 때와 같은 시점에 검증이 이뤄지기에 예외발생을 훨신 빠르게 할 수 있다.

# 하위 클래스를 검증하는 메타클래스를 정의나느 방법을 살펴보기 전에, 일반적인 객체에 대해 메타클래스가 어떻게 작동하지 이해해보자.
# 메타클래스는 type을 상속해 정의된다. 기본적인 경우 메타클래스는 __new__를 통해 연관된 클래스의 내용을 받는다.
# 다음 코드는 어떤 타입이 실제로 구성되기 전에 클래스 정보를 살펴보고 변경하는 모습을 보여준다.
class Meta(type):
    # 메타클래스는 클래스 이름, 클래스가 상속하는 부모 클래스들(bases), class 본문에 정의된 모든 클래스 애트리뷰트에 접근할 수 있다.
    # 모든 클래스는 object를 상속하기 때문에 메타클래스가 받는 부모 클래스의 튜플 안에는 object가 명시적으로 들어 있지 않다.
    def __new__(meta, name, bases, class_dict):
        print(f'* 실행: {name}의 메타 {meta}.__new__')
        print('기반클래스들:', bases)
        print(class_dict)
        return type.__new__(meta, name, bases, class_dict)

class MyClass(metaclass=Meta):
    stuff = 123

    def foo(self):
        pass

class MySubclass(MyClass):
    other = 567

    def bar(self):
        pass

# 연관된 클래스가 정의되기 전에 이 클래스의 모든 파라미터를 검증하려면 Meta.__new__에 기능을 추가해야 한다.

# 예를 들어 다각형을 표현하는 타입을 만든다고 하자.
# 이때 검증을 수행하는 특별한 메타클래스를 정의하고, 이 메타클래스를 모든 다각형 클래스 계층 구조의 기반 클래스로 사용할 수 있다.
# 기반 클래스 자체는 같은 검증을 수행하지 않는다는 점을 유의하자.
class ValidatePolygon(type):
    def __new__(meta, name, bases, class_dict):
        # Polygon 클래스의 하위 클래스만 검증한다
        if bases:
            if class_dict['sides'] < 3:
                raise ValueError('다각형 변은 3개 이상이어야 함')
        return type.__new__(meta, name, bases, class_dict)

class Polygon(metaclass=ValidatePolygon):
    sides = None # 하위 클래스는 이 애트리뷰트에 값을 지정해야 한다
    @classmethod
    def interior_angles(cls):
        return (cls.sides - 2) * 180

class Triangle(Polygon):
    sides = 3

class Rectangle(Polygon):
    sides = 4

class Nonagon(Polygon):
    sides = 9

def use_subclass():
    # 만약 metaclass의 검증을 통과하지 못하면 프로그램이 시작되지도 않는다.
    assert Triangle.interior_angles() == 180
    assert Rectangle.interior_angles() == 360
    assert Nonagon.interior_angles() == 1260

# 에러 발생
# class Line(Polygon):
#    print('sides 이전')
#    sides = 2
#    print('sides 이후')


# 3.6버전 이후에는 위 기능과 똑같은 검증을 훨씬 간단히 제공한다.
class BetterPolygon:
    sides = None  # 하위클래스에서 이 애트리뷰트의 값을 지정해야 함

    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls.sides < 3:
            raise ValueError('다각형 변은 3개 이상이어야 함')

    @classmethod
    def interior_angles(cls):
        return (cls.sides - 2) * 180

class Hexagon(BetterPolygon):
    sides = 6

assert Hexagon.interior_angles() == 720

# 코드가 훨씬 짧아지고 ValidatePolygon 메타클래스가 완전히 사라졌다.
# 그리고 class_dict['sides']를 통해 클래스 딕셔너리에서 sides를 가져올 필요가 없다.
# __init_subclass__ 안에서는 cls 인스턴스에서 sides 애트리뷰트를 직접 가져올 수 있다.

# 다만 표준 파이썬 메타클래스 방식의 문제점은 클래스 정의마다 메타클래스를 단 하나만 지정할 수 있다는 것이다.

# 다음 코드는 어떤 영역에 칠할 색을 검증하기 위한 메타클래스다.
class ValidateFilled(type):
    def __new__(meta, name, bases, class_dict):
        # Filled 클래스의 하위 클래스만 검증한다
        if bases:
            if class_dict['color'] not in ('red', 'green'):
                raise ValueError('지원하지 않는 color 값')
        return type.__new__(meta, name, bases, class_dict)

class Filled(metaclass=ValidateFilled):
    color = None  # 모든 하위 클래스에서 이 애트리뷰트의 값을 지정해야 한다

# Polygon 메타클래스와 Filled 메타클래스를 함께 사용하려고 시도하면 오류가 뜨는 걸 볼 수 있다.
#class RedPentagon(Filled, Polygon):
#    color = 'red'
#    sides = 5

# 위 문제 역시 __init_subclass__ 특별 클래스 메서드로 해결할 수 있다.
# super() 내장함수를 사용해 부모나 형제자매 클래스의 __init_subclass__를 호출해주는 한, 여러 단계로 이뤄진 __init_subclass__를
# 활용하는 클래스 계층구조를 쉽게 정의할 수 있다. (비슷한 예제를 Better way 40에서 볼 수 있다.)
# 이 방식은 다중 상속과도 잘 어울러진다.

# 다음 코드는 영역을 칠할 색을 표현하는 클래스를 정의한다. 이 클래스는 앞에서 정의한 BetterPolygon 클래스와 함께 합성할 수 있다.
class Filled:
    color = None  # 하위 클래스에서 이 애트리뷰트 값을 지정해야 한다

    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls.color not in ('red', 'green', 'blue'):
            raise ValueError('지원하지 않는 color 값')

# 새로운 클래스에서 BetterPolygon과 Filled 클래스를 모두 상속할 수 있다.
# 두 클래스는 모두 super().__init_subclass__()를 호출하기 때문에 하위 클래스가 생성될 떄 각각의 검증 로직이 실행된다.
class RedTriangle(Filled, Polygon):
    color = 'red'
    sides = 3


def use_init_subclass():
    ruddy = RedTriangle()
    assert isinstance(ruddy, Filled)
    assert isinstance(ruddy, Polygon)

    print('class 이전')

    # 오류가 나는 부분. 오류를 보고 싶으면 커멘트를 해제할것
    #class BlueLine(Filled, Polygon):
    #    color = 'blue'
    #    sides = 2

    print('class 이후')

# 심지어 __init_subclass__를 다이아몬드 상속 같은 복잡한 경우에도 사용할 수 있다.
class Top:
    def __init_subclass__(cls):
        super().__init_subclass__()
        print(f'{cls}의 Top')

class Left(Top):
    def __init_subclass__(cls):
        super().__init_subclass__()
        print(f'{cls}의 Left')


class Right(Top):
    def __init_subclass__(cls):
        super().__init_subclass__()
        print(f'{cls}의 Right')


class Bottom(Left, Right):
    def __init_subclass__(cls):
        super().__init_subclass__()
        print(f'{cls}의 Bottom')

# Bottom에서 Top에 이르는 상속 경로가 두 가지 있지만, 각 클래스마다 Top.__init_subclass__는 단 한번만 호출된다.
# ======================================================================================================================
# 지연 계산 애트리뷰트가 필요하면 __getattr__, __getattribute__, __setattr__을 사용해라.
# 파이썬 object 훅을 사용하면 시스템을 서로 접합하는 제너릭 코드를 쉽게 작성할 수 있다.

# 예를 들어 데이터베이스 레코드를 파이썬 객체로 표현하고 싶다고 하자.
# 데이터베이스에는 이미 스키마 집합이있다. 우리가 만들 레코드에 대응하는 코드도 스키마가 어떤 모습인지 알아야한다.
# 하지만 파이썬에서 데이터베이스와 파이썬 객체를 연결해주는 코드가 특정 스키마만 표현할 필요는 없다. 스키마를 표현하는 클래스는 더 일반적으로 만들 수 있다.
# 어떻게 가능할까? @property나 디스크립터등은 미리 정의해야만 사용할 수 있으므로 적합하지 않다. 대신 파이썬은 __getattr__이라는
# 특별 메서드를 사용해 이런 동적 기능을 활용할 수 있다.
# 어떤 클래스 안에 __getattr__메서드 정의가 있다면, 이 객체의 인스턴스 딕셔너리에서 찾을 수 없는 애트리뷰트에 접근할 떄 마다 __getattr__이 호출된다.
class LazyRecord:
    def __init__(self):
        self.exists = 5

    def __getattr__(self, name):
        value = f'{name}의 값'
        setattr(self, name, value)
        return value


class LoggingLazyRecord(LazyRecord):
    def __getattr__(self, name):
        print(f'* 호출: __getattr__({name!r}), '
              f'인스턴스 딕셔너리 채워 넣음')
        result = super().__getattr__(name)
        print(f'* 반환: {result!r}')
        return result


def use_getattr():
    # foo라는 존재하지 않는 애트리뷰트를 사용해 __getattr__메서드를 호출하고 이를 통해 인스턴스 딕셔너리를 변경한다.
    data = LazyRecord()
    print('이전:', data.__dict__)
    print('foo:', data.foo)
    print('이후:', data.__dict__)

    # 자세한 호출순서를 보면 첫 번째 foo에선 __getattr__이 호출되나 setattr을 통해 foo가 추가된 이후에는 호출되지 않는 걸 볼 수 있다.
    data = LoggingLazyRecord()
    print('exists: ', data.exists)
    print('첫 번째 foo: ', data.foo)
    print('두 번째 foo: ', data.foo)

    # 이러한 기능은 스키마가 없는 데이터에 지연 게산으로 접근하는 등의 활용이 필요할 때 아주 유용하다.
    # 스키마가 없는 데이터에 접근하면 __getattr__이 한 번 실행되면서 프로퍼티를 적재하는 힘든 작업을 모두 처리한다.

    # 다만 이 데이터베이스 시스템 안에서 트랜잭션이 필요하다고 할 때, 레코드가 유효한지 그리고 트랜잭션이 여전히 열려있는지 판단해야한다.
    # 이와 같은 고급 사용법은 __getattr__ 훅으로 이런 기능을 안정적으로 만들 수 없다.
    # 대신 __getattribute__라는 다른 object 훅을 사용하면 가능하다.
    # 심지어 애트리뷰트 디렉터리에 존재하는 애트리뷰트에 접근할 때도 이 훅이 호출된다. 이를 사용하면 프로퍼티에 접근할 때마다 항상 전역
    # 트랜잭션 상태를 검사하는 등의 작업을 수행할 수 있다.

# 다음 코드는 __getattribute__가 호출될 때마다 로그를 남기는 ValidatingRecord를 정의한다.
class ValidatingRecord:
    def __init__(self):
        self.exists = 5
    def __getattribute__(self, name):
        print(f'* 호출: __getattr__({name!r})')
        try:
            value = super().__getattribute__(name)
            print(f'* {name!r} 찾음, {value!r} 반환')
            return value
        except AttributeError:
            value = f'{name}을 위한 값'
            print(f'* {name!r}를 {value!r}로 설정')
            setattr(self, name, value)
            return value

def use_getattribute():
    data = ValidatingRecord()
    print('exists: ', data.exists)
    print('첫 번째 foo: ', data.foo)
    print('두 번째 foo: ', data.foo)

    # 존재하지 않는 프로퍼티에 동적으로 접근하는 경우에는 AttributeError 예외가 발생한다. __getattr__과 __getattribute__에서 존재하지
    # 않는 프로퍼티를 사용할 때 발생하는 표준적인 예외가 AttributeError다.

    # hasattr를 통해 프러퍼티가 존재하는지 검사하는 기능과 getattr를 통해 프로퍼티 값을 꺼내오는 기능에 의존할 때도 있다.
    # 이 두 함수도 __getattr__을 호출하기 전에 어트리뷰트 이름을 인스턴스 딕셔너리에서 검사한다.
    data = LoggingLazyRecord()  # __getattr__을 구현
    print('이전: ', data.__dict__)
    print('최초에 foo가 있나: ', hasattr(data, 'foo'))
    print('이후: ', data.__dict__)
    print('다음에 foo가 있나: ', hasattr(data, 'foo'))

    data = ValidatingRecord()  # __getattribute__를 구현
    print('최초에 foo가 있나: ', hasattr(data, 'foo'))
    print('다음에 foo가 있나: ', hasattr(data, 'foo'))

    # __getattr__은 어트리뷰트가 없을 시 한번만 __getattribute__는 hasattr이나 getattr이 쓰일 때마다 호출되는 걸 볼 수 있다.

# 이제 내 파이썬 객체에 값이 대입된 경우, 나중에 이 값을 데이터베이스에 다시 저장하고 싶다고 하자.
# 임의의 애트리뷰트에 값을 설정할 때마다 호출되는 object 훅인 __setattr__을 사용하면 이런 기능을 비슷하게 구현할 수 있다.
# __getattr__이나 __getattribute__로 값을 읽을 때와 달리 메서드가 두 개 있을 필요가 없다.
# __setattr__은 인스턴스의 애트리뷰트에 대입이 이뤄질때마다(직접 대입이든 setattr을 통해서든) 항상 호출된다.
class SavingRecord:
    def __setattr__(self, name, value):
        # 데이터를 데이터베이스 레코드에 저장한다
        super().__setattr__(name, value)

class LoggingSavingRecord(SavingRecord):
    def __setattr__(self, name, value):
        print(f'* 호출: __setattr__({name!r}, {value!r})')
        super().__setattr__(name, value)

def use_setattr():
    data = LoggingSavingRecord()
    print('이전: ', data.__dict__)
    data.foo = 5
    print('이후: ', data.__dict__)
    data.foo = 7
    print('최후:', data.__dict__)

# __getattribute__와 setattr__의 문제점은 원하든 원지 않든 어떤 객체의 모든 애트리뷰트에 접근할 때마다 함수가 호출된다든 것이다.
# 예를 들어 어떤 객체와 관련된 딕셔너리에 키가 있을 때만 이 객체의 애트리뷰트에 접근하고 싶다고 하자.
class BrokenDictionaryRecord:
    def __init__(self, data):
        self._data = {}
    def __getattribute__(self, name):
        print(f'* 호출: __getattribute__({name!r})')
        return self._data[name]

data = Brokedata = BrokenDictionaryRecord({'foo': 3})
# 이 클래스의 정의는 self._data에 대한 접근을 __getattribute__를 통해 수생하도록 요구한다.
# 하지만 실제로 실행해보면 스택을 다 소모할 때까지 재귀를 수행하다 죽어버린다.
# 이유는 __getattribute__가 self_.data에 접근해서 __getattribute__가 다시 호출되기 때문이다.
#data.foo

# 해결방법은 super().__getattribute__를 호출해 인스턴스 애트리뷰트 딕셔너리에서 값을 가져오는 것이다. 이렇게 하면 재귀를 피할 수 있다.
class DictionaryRecord:
    def __init__(self, data):
        self._data = data

    def __getattribute__(self, name):
        print(f'* 호출: __getattribute__({name!r})')
        data_dict = super().__getattribute__('_data')
        return data_dict[name]

data = DictionaryRecord({'foo': 3})
#print('foo: ', data.foo)

# 반대로 __setattr__ 메서드 안에서 애트리뷰트를 변경하는 경우도 super().__setattr__을 적절히 호출해야 한다.
# ======================================================================================================================
if __name__ == "__main__":
    for mtd in [
        use_getattr,
        use_getattribute,
        use_subclass,
        use_init_subclass,
        use_subclass_more,
        use_best_way,
        use_set_name,
        use_set_name_better,
        use_decorater,
        use_decorater_2,
        use_decorater_better
    ]:
        mtd()
        print('==================================================================')
