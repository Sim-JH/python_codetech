# ======================================================================================================================
# 커스텀 컨테이너 타입은 collections.abc를 상속하라.
# 파이썬 프로그램의 상당 부분은 데이터를 포함하는 클래스를 정의하고 이런 클래스에 속하는 객체들이 상호작용하는 방법을 기술하는 것으로 이뤄진다.
# (기능 구현은 class로 이를 연결해 사용하는 건 func로) 모든 파이썬 클래스는 함수와 애트리뷰트를 함께 캡슐화하는 일조의 컨테이너라 할 수 있다.
# 파이썬은 데이터를 관리할 떄 사용할 수 있도록 리스트, 튜플, 셋, 딕셔너리 등의 내장 컨테이너 타입을 제공한다.

# 시퀀스처럼 사용법이 간단한 클래스를 정의할 때는 리스트 타입의 하위 클래스를 만들고 싶은 것이 당연하다.
# 예를 들어 맴버들의 빈도를 계산하는 메서드가 포함된 커스텀 리스트 타입이 필요하다고 가정하자.
class FrequencyList(list):
    def __init__(self, member):
        # list 클래스의 init()를 호출
        super().__init__(member)

    # 리스트를 key=문자, value=갯수인 dict로 만들어주는 기능 추가
    def frequency(self):
        counts = {}
        for item in self:
            counts[item] = counts.get(item, 0) + 1
        return counts

# FrequencyList를 list의 하위 클래스로 만듦으로서 리스트가 제공하는 모든 표준함수를 FrequencyList에서도 사용할 수 있다.
# 또한 필요한 기능을 제공하는 메서드도 얼마든지 추가할 수 있다.
def Inheritance_list():
    foo = FrequencyList(['a', 'b', 'a', 'c', 'b', 'a', 'd'])
    print('길이: ', len(foo))

    foo.pop()
    print('pop한 다음:', repr(foo))
    print('빈도:', foo.frequency(), type(foo.frequency()))

# 이제 리스트처럼 느껴지면서 인덱싱이 가능한 객체를 제공하는데, 리스트의 하위 클래스로 만들고 싶지는 않다고 가정해보자.
class BinaryNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


class IndexableNode(BinaryNode):
    def _traverse(self):
        if self.left is not None:
            yield from self.left._traverse()
        yield self
        if self.right is not None:
            yield from self.right._traverse()

    # 만약 bar[0]같은 인덱싱이 있다면 이는 bar.__getitem__(0)으로 해석된다.
    # 인덱싱 기능을 구현하려면 __getitem__아래 트리 노드를 깊이 우선순회(depth first traverse)하는 메서드를 구현하면 된다.
    def __getitem__(self, index):
        for i, item in enumerate(self._traverse()):
            if i == index:
                return item.value
        raise IndexError(f'인덱스 범위 초과: {index}')

# 위 클래스는 left나 right 애트리뷰트를 통해 순회할 수도 있지만, 추가로 리스트처럼 접근할 수도 있다.
def custom_index():
    tree = IndexableNode(
        10,
        left=IndexableNode(
            5,
            left=IndexableNode(2),
            right=IndexableNode(
                6,
                right=IndexableNode(7))),
        right=IndexableNode(
            15,
            left=IndexableNode(11)))

    print('LRR:', tree.left.right.right.value)
    print('인덱스 0:', tree[0])
    print('인덱스 1:', tree[1])
    print('11이 트리 안에 있나?', 11 in tree)
    print('17이 트리 안에 있나?', 17 in tree)
    print('트리:', list(tree))

# __len__을 구현하면 len()도 사용할 수 있다.
class SequenceNode(IndexableNode):
    def __len__(self):
        for count, _ in enumerate(self._traverse(), 1):
            pass
        return count

# 다만 문제는 __getitem__나 __len__을 구현하는 것만으로 올바른 시퀀스를 구현할 수 없다는 거다.
# count, index 등 시퀀스에 있을 것으로 예상하는 메서도도 들어있지 않다. 자신만의 컨테이너 타입을 직접 정의하는 건 어려운 일이다.
# 이런 어려움을 덜어주기 위해 collection.abc 내장 모듈안에 컨테이너 타입에 정의해야하는 정형적인 메서드를 제공하는 추상 기반 클래스가 여러가지 들어있다.
# 이런 추상 기반 클래스의 하위 클래스를 만들고 필요한 메서드 구현을 빼먹으면 해당 모듈이 실수한 부분을 알려준다.
from collections.abc import Sequence

# class BadType(Sequence):
#     pass
#
# foo = BadType()

# 또한 collections.abc에서 가져온 추상 기반 클래스가 요구하는 모든 메서드를 구현하면 index나 count와 같은 추가 구현 메서드를 거저 얻을 수 있다.
class BetterNode(SequenceNode, Sequence):
    pass


def use_abc():
    tree = BetterNode(
        10,
        left=BetterNode(
            5,
            left=BetterNode(2),
            right=BetterNode(
                6,
                right=BetterNode(7))),
        right=BetterNode(
            15,
            left=BetterNode(11))
    )

    print('7의 인덱스:', tree.index(7))
    print('10의 개수:', tree.count(10))
# ======================================================================================================================
# 비공개 애트리뷰트, 공개 애트리뷰트
# 파이썬에서 클래스의 애트리뷰트에 대한 가시성은 공개와 비공개 두 가지밖에 없다.
class MyObject:
    def __init__(self):
        # 공개 애트리뷰트
        self.public_field = 5
        # 비공개 애트리뷰트
        self.__private_field = 10

    def get_private_field(self):
        return self.__private_field


def dont_use_private():
    foo = MyObject()
    print(foo.public_field)
    # print(foo.__private_field)
    print(foo.get_private_field())

    # 파이썬 컴파일러는 비공개 애트리뷰트를 자식 클래스나 클래스 외부에서 사용하지 못하도록 엄격히 금지하지 않는다.
    # 비공개 애트리뷰트로 접근을 막으려고 시도하기보다는 보호된 필드(_private)를 사용하면서 문서에 적절한 가이드를 남겨라.
    # 코드 작성을 제어할 수 없는 하위 클래스에서 네이밍 충돌이 일어나는 걸 막고 싶을때만 비공개 애트리뷰트를 사용할 것을 권한다.

# ======================================================================================================================
# 기능을 합성할때는 믹스인 클래스를 사용하라.
# 파이썬은 다중상속을 처리할 수 있지만 피하는 편이 좋다.
# 대신 mix-in 사용을 고려해라. 믹스인은 자식 클래스가 사용할 메서드 맻 개만 정의하는 클래스다.
# 믹스인 클래스에는 자체 애트리뷰트 정의가 없으므로 __init__ 메서드를 호출할 필요도 없다,

# 믹스인을 사용해 메모리 내에 들어있는 파이썬 객체를 딕셔너리로 바꿔보자.
class ToDictMixin:
    def to_dict(self):
        # _traverse_dict 메서드를 hasattr을 통한 동적접근과 isinstance를 통한 타입검사, __dict__를 통한 딕셔너리 접근을 활요해 구현할 수 있다.
        return self._traverse_dict(self.__dict__)

    def _traverse_dict(self, instance_dict):
        output = {}
        for key, value in instance_dict.items():
            output[key] = self._traverse(key, value)
        return output

    def _traverse(self, key, value):
        if isinstance(value, ToDictMixin):
            return value.to_dict()
        elif isinstance(value, dict):
            return self._traverse_dict(value)
        elif isinstance(value, list):
            return [self._traverse(key, i) for i in value]
        elif hasattr(value, '__dict__'):
            return self._traverse_dict(value.__dict__)
        else:
            return value


# 위 믹스인을 사용해 이진 트리를 딕셔너리로 표현
class BinaryTree(ToDictMixin):
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


def use_mixin():
    tree = BinaryTree(10,
                      left=BinaryTree(7, right=BinaryTree(9)),
                      right=BinaryTree(13, left=BinaryTree(11)))
    print(tree.to_dict())

# 믹스인의 가장 큰 장점은 제너릭 기능을 쉽게 연결할 수 있고 필요할 떄 기존 기능을 다른 기능으로 오버라이드해 변경할 수 있다는 거다.
# 아래 코드는 BinaryTree에 대한 참조를 저장하는 BinaryTree의 하위 클래스를 정의한다.
# 원래라면 이 구현은 무한 로프를 돌지만 BinaryTreeWithParent._traverse 메서드를 오버라이드해 문제가 되는 값만 처리하게 한다.
# 오버라이드한 메서는 부모를 가리키는 참조는 부모 값을 아닌경우에는 super를 통해 디폴드 믹스인 구현을 호출한다.
class BinaryTreeWithParent(BinaryTree):
    def __init__(self, value, left=None,
                 right=None, parent=None):
        super().__init__(value, left=left, right=right)
        self.parent = parent

    def _traverse(self, key, value):
        if (isinstance(value, BinaryTreeWithParent) and
                key == 'parent'):
            return value.value  # 순환참조 방지
        else:
            return super()._traverse(key, value)

def use_overide():
    root = BinaryTreeWithParent(10)
    root.left = BinaryTreeWithParent(7, parent=root)
    root.left.right = BinaryTreeWithParent(9, parent=root.left)
    print(root.to_dict())


# 믹스인을 서로 합성할 수도 있다.
# 예를 들어 임의의 클래스를 JSON으로 직렬화하는 제너럴 믹스인을 만들고 싶다고 하자. 모든 클래스가 to_dict 메서드를 제공한다고 가정하면,
# 아래와 같은 제너럴 믹스인을 만들 수 있다.
import json

# 여기서 인스턴스 메서도와 클래스 메서드가 함꼐 정의됐다는 점을 유의하자. 믹스인을 사용하면 인스턴스/클래스 동작 모두 하위클래스에 추가할 수 있다.
# JsonMixin의 하위 클래스 요구사항은 to_dict 메서드를 제공해야한다는 점과 __init__메서드가 키워드 인자(**kwargs)를 받아야한다는 점 뿐이다.
class JsonMixin:
    @classmethod
    def from_json(cls, data):
        kwargs = json.loads(data)
        return cls(**kwargs)

    def to_json(self):
        return json.dumps(self.to_dict())


class DatacenterRack(ToDictMixin, JsonMixin):
    def __init__(self, switch=None, machines=None):
        self.switch = Switch(**switch)
        self.machines = [
            Machine(**kwargs) for kwargs in machines]


class Switch(ToDictMixin, JsonMixin):
    def __init__(self, ports=None, speed=None):
        self.ports = ports
        self.speed = speed


class Machine(ToDictMixin, JsonMixin):
    def __init__(self, cores=None, ram=None, disk=None):
        self.cores = cores
        self.ram = ram
        self.disk = disk


def compound_mixin():
    serialized = """{
        "switch": {"ports": 5, "speed": 1e9},
        "machines": [
            {"cores": 8, "ram": 32e9, "disk": 5e12},
            {"cores": 4, "ram": 16e9, "disk": 1e12},
            {"cores": 2, "ram": 4e9, "disk": 500e9}
        ]
    }"""
    deserialized = DatacenterRack.from_json(serialized)
    roundtrip = deserialized.to_json()
    print(json.loads(serialized), json.loads(roundtrip))
    assert json.loads(serialized) == json.loads(roundtrip)

# ======================================================================================================================
# super로 부모클래스를 초기화하라
class MyBaseClass:
    def __init__(self, value):
        self.value = value


class TimesSevenCorrect(MyBaseClass):
    def __init__(self, value):
        # 자식 클래스에서 부모 클래스의 __init__()를 호출해서 초기화
        super().__init__(value)
        self.value *= 7


class PlusNineCorrect(MyBaseClass):
    def __init__(self, value):
        super().__init__(value)
        self.value += 9

# super()를 통해 부모클래스를 초기화해야 실제로 class문의 순서대로 호출된다.
# 이때 호출 순서는 MRO의 정의를 따른다.
class GoodWay(TimesSevenCorrect, PlusNineCorrect):
    def __init__(self, value):
        super().__init__(value)


def use_super():
    foo = GoodWay(5)
    print('7 * (5 + 9) = 98이 나와야 하고 실제로도', foo.value)

    # 얼핏보면 TimesSevenCorrect, PlusNineCorrect 순서로 호출되어 (5 * 7) + 9 = 44가 되야하는 것 처럼 보이지만 실제로는 아니다.
    # 이 함수는 GoodWay.__init__(이후 생략)을 호출하고, TimesSevenCorrect와 PlusNineCorrect를 차례로 호출하고 그 후,
    # MyBaseClass를 호출한다.
    # 상속 다이아몬드의 정점(MyBaseClass) 도달 시, 각 초기화 메서드는 클래스의 __init__가 호출된 역순으로 작업하게 된다.
    # MyBaseClass에 5를 대입하고 PlusNineCorrect로 9를 더하고 TimesSevenCorrect와를 곱한다.
    mro_str = '\n'.join(repr(cls) for cls in GoodWay.mro())
    print(mro_str)

# super 함수에는 두 가지 파라미터를 넘길 수 있다. 첫 번째는 접근하려는 MRO뷰를 제공할 부모타입이고, 두 번째는 접근할 때 사용할 인스턴스다.
class ExplicitTrisect(MyBaseClass):
    def __init__(self, value):
        super(ExplicitTrisect, self).__init__(value)
        self.value /= 3

# 하지만 object 인스턴스를 초기화할 떄는 두 파라미터를 지정할 필요가 없다. 만약 클래스 정의 안에서 아무 인자도 지정하지 않고
# super를 호출하면, 컴파일러가 자동으로 올바른 파라미터(__class__와 self)를 넣어준다.
# 따라서 ExplicitTrisect 와 아래 두 가지 방법은 모두 동일하다.
class AutomaticTrisect(MyBaseClass):
    def __init__(self, value):
        super(__class__, self).__init__(value)
        self.value /= 3

class ImplicitTrisect(MyBaseClass):
    def __init__(self, value):
        super().__init__(value)
        self.value /= 3

# super에 파라미터를 제공해야하는 유일한 경우는 자식 클래스에서 상위 클래스의 특정 기능에 접근해야 하는 경우뿐이다.
assert ExplicitTrisect(9).value == 3
assert AutomaticTrisect(9).value == 3
assert ImplicitTrisect(9).value == 3
# ======================================================================================================================
if __name__ == "__main__":
    for mtd in [
        use_super,
        use_mixin,
        use_overide,
        compound_mixin,
        dont_use_private,
        Inheritance_list,
        custom_index,
        use_abc
    ]:
        mtd()
        print('==================================================================')
