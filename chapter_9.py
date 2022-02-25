# ======================================================================================================================
# 프로그램이 메모리를 사용하는 방식과 메모리 누수를 이해하기 위해 tracemalloc을 사용하라
# 파이썬 기본 구현인 CPython은 메모리 관리를 위해 참조 카운팅을 사용한다. 이로 인해 어떤 객체를 가리키는 참조가 모두 없어지면 참조된
# 객체도 메모리에서 삭제되고 메모리 공간을 다른 데이터에 내어줄 수 있다. CPython에는 순환 탐지기가 들어 있으므로 자기 자신을 참조하는 객체의
# 메모리도 언젠가는 수집된다.
# 이는 이론적으로 대부분의 파이썬 개발자가 프로그램에서 메모리를 할당하거나 해제하는 것을 신경쓰지 않아도 된다는 뜻이다.
# 하지만 실전에서는 더 이상 사용하지 않는 쓸모없는 참조를 유지하기 때문에 언젠가는 결국 메모리를 소진하게 되는 경우가 있다.
# 파이썬 프로그램이 사용하거나 누수시키는 메모리를 알아내기란 매우 어려운 일이다.
# tracemalloc은 객체를 자신이 할당된 장소와 연결시켜준다. 이 정보를 사용해 메모리 사용의 이전과 이후의 스냅샵을 만들어 서로 비교하면
# 어떤 부분이 변경됐는지 알 수 있다.
# ======================================================================================================================
# TestCase 하위 클래스를 사용해 프로그램에서 연관된 행동 방식을 검증하라
# 목을 사용해 의존 관계가 복잡한 코드를 테스트하라
# 도서 참조
# ======================================================================================================================
# 테스트와 디버깅
# 파이썬은 컴파일 시점에 정적 타입 검사를 수행하지 않는다. 또한, 파이썬 인터프리터가 컴파일 시점에 프로그램이 제대로 작동할 것이라고
# 확일할 수 있는 요소가 전혀 없다. 파이썬은 선택적인 타입 애너테이션을 지원하며, 이를 활용해 정적(컴파일 시점, 동적:프로그램 실행시점)분석을
# 시행함으로써 여러 가지오류를 감지할 수 있다. 하지만 여전히 파이썬은 근본적으로 동적인 언어이며, 프로그램을실행하는 도중에 어떤 일이든 벌어질 수 있다.


# 디버깅 출력에는 repr 문자열을 사용하라,
# 파이썬 프로그램을 디버깅할 떄 print 함수와 형식화 문자열을 사용하거나 logging 내장 모듈을 사용해 출력을 만들면 아주 긴 출력이 생긴다.
# 파이썬의 내부 정보도 일반 애트리뷰트만큼 접근하기 쉽다.
# 실질적으로 필요한 작업은 프로그램이 실행되는 동안 print를 호출해 상태가 어떻게 바뀌었는지 알아내는 것이다.

# print는 만약 문자열을 출력시 "", ''을 포함하지 않고 출력한다.
# 반면 repr는 객체의 출력 가능한 표현을 반환하는데, 출력 가능한 표현은 반드시 객체를 가장 명확하게 이해할 수 있는 문자열 표현이어야한다.
a = "\x07"
print(repr(a))
# repr이 돌려준 값을 eval 내장 함수에 넘기면 repr에 넘겼던 객체와 같은 객체가 생겨야한다.
b = eval(repr(a))
assert a == b
# print를 사용해 디버깅할 때는 값을 출력하기 전에 repr을 호출해서 타입이 다른 경우에도 명확히 차이를 볼 수 있게 만들어야한다.
print(repr(5))
print(repr('5'))
# repr을 호출하는 것은 % 연산자에 %r 형식화 문자열을 사용하는 것이 f스트링에 !r 타입 변환을 사용하는 것과 같다.
print('%r' % 5)
print('%r' % '5')

int_value = 5
str_value = '5'
print(f'{int_value!r} != {str_value!r}')
# 예를 들어 파이썬 클래스의 경우 사람이 읽을 수 있는 문자열 값은 repr 값과 같다. 이는 인스턴스를 print에 넘기면 원하는 출력이 나오므로
# 굳이 인스턴스에 대해 repr을 호출할 필요가 없다는 뜻이다. 안타깞지만 object를 상속한 하위 클래스의 repr 기본구현은 그다지 쓸모가 없다.
class OpaqueClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y

obj = OpaqueClass(1, 'foo')
print(obj)
# 이 출력은 eval 함수에 넘길 수 없고, 객체의 인스턴스 필드에 대한 정보도 전혀 들어있지 않다.

# 이를 해결하는 두 가지 방법이 있다. 클래스 정의를 바꿀 수 있는 경우에는 __repr__을 직접 정의할 수 있다,
class BetterClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'BetterClass({self.x!r}, {self.y!r})'

obj = BetterClass(2, '뭐시기')
print(obj)
# 클래스 정의를 바꿀 수 없다면 __ditct__ 애트리뷰트를 통해 객체의 인스턴스 딕셔너리에 접근할 수 있다.
obj = OpaqueClass(4, 'baz')
print(obj.__dict__)




# ======================================================================================================================