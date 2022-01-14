# ======================================================================================================================
# 재사용 가능한 @property 메서드를 만들려면 디스크립터를 사용해라
# @property의 가장 큰 문제점은 재사용성이다. @property가 데코레이션 하는 메서드를 같은 클래스에 속하는 여러 애트리뷰트로 사용할 수 없다.
# 그리고 서로 무관한 클래스 사이에서 @property 데코레이터를 적용한 메서드를 재사용할 수도 없다.

# 예를들어 학생의 숙제 점수가 백분율 값인지 검증하고 싶다고 하자.
class Homework:
    def __init__(self):
        self._grade = 0

    @property
    def grade(self):
        return self._grade

    @grade.setter
    def grade(self, value):
        if not (0 <= value <= 100):
            raise ValueError(
                '점수는 0과 100 사이입니다')
        self._grade = value


def use_discripter():
    # property로 쉽게 사용할 수 있다.
    galileo = Homework()
    galileo.grade = 95

# 이제 이 학생에게 시험 점수를 부여하고 싶다고 하자. 시험 과목은 여러 개고, 각 과목마다 별도의 점수가 부여된다.
class Exam:
    def __init__(self):
        self._writing_grade = 0
        self._math_grade = 0

    # 정적 메소드(인스턴스를 만들지 않아도 class의 메서드를 바로 실행할 수 있다. classmethod도 마찬가지)
    @staticmethod
    def _check_grade(value):
        if not (0 <= value <= 100):
            raise ValueError(
                '점수는 0과 100 사이입니다')

    @property
    def writing_grade(self):
        return self._writing_grade

    @writing_grade.setter
    def writing_grade(self, value):
        self._check_grade(value)
        self._writing_grade = value

    @property
    def math_grade(self):
        return self._math_grade

    @math_grade.setter
    def math_grade(self, value):
        self._check_grade(value)
        self._math_grade = value

# 위처럼 계속확장다보면 각 부분마다 새로운 property를 지정하고 관련 검증 메서드를 작성해야하므로 굉장히 번거롭다.
# 이런 경우 디스크립터를 사용하는 것이 일반적이다. 디스크립터 프로토콜은 파이썬 언어에서 애트리뷰트 접근을 해석하는 방법을 정의한다.
# 디스크립터 클래스는 __get__, __set__ 메서드를 제공하고 이 두 메서드를 사용하면 별다른 분비코드없이 동작을 재사용할 수 있다.
# 이런 경우 같은 로직을 한 클래스 안에 속한 여러 다른 애트리뷰트에 적용할 수 있으므로 디스크립터가 믹스인 보다 낫다.

# 다음 코드는 Grade의 인스턴스인 클래스 애트리뷰트가 들어있는 Exam 클래스를 정의한다.
# Grade 클래스는 다음과 같은 디스크립터 프로토콜을 구현한다.
class Grade:
    def __init__(self):
        self._value = 0
    def __get__(self, instance, instance_type):
        return self._value
    def __set__(self, instance, value):
        if not (0 <= value <= 100):
            raise ValueError(
                '점수는 0과 100 사이입니다')
        self._value = value

# 위 클래스를 대입하면
# exam = Exam()
# exam.writing_grade = 40
# 다음과 같이 해석된다.
# Exam.__dict__['writing_grade'].__set__(exam, 40)
# 마찬가지로 다음과 같이 프로퍼티를 읽으면
# exam.writing_grade
# 다음과 같이 해석된다.
# Exam.__dict__['writing_grade'].__get__(exam, Exam)

# 위와 같은 동작을 이끌어내는 것은 object 클래스의 __getattribute__ 매서드다. 간단히 말해 Exam 인스턴스의 writing_grade라는 이름의
# 애트리뷰트가 없으면 파이썬은 Exam 클래스의 애트리뷰트를 대신 사용한다. 이 클래스의 애트리뷰트가 __get__과 __set__ 메서드가 정의된
# 객체라면 파이썬은 디스크립터 프로토콜을 따라야 한다고 결정한다.

# 이제 위 구현을 사용해보자. 정상적으로 작동할까?
class Exam:
    # 클래스 애트리뷰트
    math_grade = Grade()
    writing_grade = Grade()
    science_grade = Grade()

def use_discripter_2():
    # 한 Exam 인스턴스에 정의된 여러 애트리뷰트에 접근할 경우에는 예상대로 작동한다.
    first_exam = Exam()
    first_exam.writing_grade = 82
    first_exam.science_grade = 99
    print('쓰기', first_exam.writing_grade)
    print('과학', first_exam.science_grade)

    # 하지만 여러 Exam 인스턴스 객체에 대해 애트리뷰트 접근을 시도하면 예기치 못한 동작을 볼 수 있다.
    second_exam = Exam()
    second_exam.writing_grade = 75
    print(f'두 번째 쓰기 점수 {second_exam.writing_grade} 맞음')
    print(f'첫 번째 쓰기 점수 {first_exam.writing_grade} 틀림; '
          f'82점이어야 함')

    # 문제는 writing_grade 클래스 애트리뷰트로 한 Grade 인스턴스를 모든 Exam 인스턴스가 공유한다는 점이다.
    # Exam 클래스가 처음 정의될 때, 이 애트리뷰트에 대한 Grade 인스턴스가 단 한번만 생성된다. Exam 인스턴스가 생성될 때마다
    # 매번 Grade 인스턴스가 생성되지는 않는다.

# 이를 해결하려면 Grade 클래스가 각각의 유일한 Exam 인스턴스에 대해 따로 값을 추적해야한다.
# 인스턴스별 상태를 딕셔너리에 저장하면 이런 구현이 가능하다.
class Grade:
    def __init__(self):
        self._values = {}

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return self._values.get(instance, 0)

    def __set__(self, instance, value):
        if not (0 <= value <= 100):
            raise ValueError(
                '점수는 0과 100 사이입니다')
        self._values[instance] = value

class Exam:
    # 클래스 애트리뷰트
    math_grade = Grade()
    writing_grade = Grade()
    science_grade = Grade()

def use_discripter_3():
    first_exam = Exam()
    first_exam.writing_grade = 82
    first_exam.science_grade = 99
    print('쓰기', first_exam.writing_grade)
    print('과학', first_exam.science_grade)

    second_exam = Exam()
    second_exam.writing_grade = 75
    print(f'두번째 쓰기 점수 {second_exam.writing_grade} 맞음')
    print(f'첫번째 쓰기 점수 {first_exam.writing_grade} 맞음')

# 위 구현은 잘 작동하지만 메모리 누수가 심하다. _values 딕셔너리는 프로그램이 실행되는 동안 __set__호출에 전달된 모든 Exam 인스턴스 참조를 저장한다.
# 이로인해 인스턴스에 대한 참조가 절대 0이 될 수 없고 가비지 컬렉터가 인스턴스 메모리를 재활용하지 못한다.
# 이 문제를 해결하기 위해 weakref 내장 모듈을 사용할 수 있다.
# 이 모듈은 WeakKeyDictionary라는 클래스를 제공하며 _values 대신 이 클래스를 쓸 수있다.
# 해당 클래스는 객체를 저장할 때 일반적인 강한 참조 대신에 약한 참조를 실행한다. 가비지 컬렉터는 약한 참조로만 참조되는 객체의 메모리를 얼마든지 재활용할 수 있다.
# 따라서 WeakKeyDictionary를 사용해 저장된 Exam 인스턴스가 더 이상 쓰이지 않는다면 해당 메모리를 재활용한다.
from weakref import WeakKeyDictionary
from weakref import WeakKeyDictionary

class Grade:
    def __init__(self):
        self._values = WeakKeyDictionary()

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return self._values.get(instance, 0)

    def __set__(self, instance, value):
        if not (0 <= value <= 100):
            raise ValueError(
                '점수는 0과 100 사이입니다')
        self._values[instance] = value


class Exam:
    # 클래스 애트리뷰트
    math_grade = Grade()
    writing_grade = Grade()
    science_grade = Grade()


def use_discripter_4():
    first_exam = Exam()
    first_exam.writing_grade = 82
    second_exam = Exam()
    second_exam.writing_grade = 75
    print(f'첫 번째 쓰기 점수 {first_exam.writing_grade} 맞음')
    print(f'두 번째 쓰기 점수 {second_exam.writing_grade} 맞음')
# ======================================================================================================================
# 애트리뷰트를 리팩터링 하는 대신 @property를 사용해라

# @property 데코레이터를 사용하면, 겉으로는 단순한 애트리뷰트처럼 보이지만 실제로는 지능적인 로직을 수행하는 애트리뷰트를 정의할 수 있다.
# 흔히 사용하는 기법으로는 간단한 수치 애트리뷰르를 그때그때 요청에 따라 계산해 제공하도록 바꾸는 것을 들 수 있다.
# 이 기법은 기존 클래스를 호출하는 코드를 전혀 바꾸지 않고도 클래스 애트리뷰트의 기존 동작을 변경할 수 있개 때문에 아주 유용하다.

# 예를 들어 일반 파이썬 객체를 사용해 리키 버킷 흐름 제어 알고리즘을 구현한다고 하자.
# 다음 코드의 Buket 클래스는 남은 가용 용량과 이 가용 용량의 잔존 시간을 표현한다.
from datetime import datetime, timedelta

class Bucket:
    def __init__(self, period):
        self.period_delta = timedelta(seconds=period)
        self.reset_time = datetime.now()
        self.quota = 0

    def __repr__(self):
        return f'Buket(quota={self.quota})'

# 리키 버킷 알고리즘은 시간을 일정한 간격(주기)으로 구분하고 가용 용량을 소비할 때마다 시간을 검사해서 주기가 달라질 경우에는 이전 주기에
# 미사용한 가용 용량이 새로운 주기로 넘어오지 못하게 막는다.
def fill(bucket, amount):
    now = datetime.now()
    if (now - bucket.reset_time) > bucket.period_delta:
        bucket.quota = 0
        bucket.reset_time = now
    bucket.quota += amount

# 가용 용량을 소비하는 쪽(예를 들어, 네트워크라면 데이터를 전송하는 클래스가 될 수 있다)에서는 어떤 작업을 하고 싶을 때마다
# 먼저 리키 버킷으로부터 자신의 작업에 필요한 용량을 할당받아야한다.
def deduct(bucket, amount):
    now = datetime.now()
    if (now - bucket.reset_time) > bucket.period_delta:
        return False # 새 주기가 시작됐는데 아직 버킷 할당량이 재설정되지 않았다
    if bucket.quota - amount < 0:
        return False # 버킷의 가용 용량이 충분하지 못하다
    else:
        bucket.quota -= amount
        return True  # 버킷의 가용 용량이 충분하므로 필요한 분량을 사용한다


def rikey_bucket():
    # 먼저 버킷에 가용 용량을 미리 정해진 할당량만큼 채운다.
    bucket = Bucket(60)
    fill(bucket, 100)
    print(bucket)

    # 그 후 사용할때마다 필요햔 용량을 버킷에서 빼야한다.
    if deduct(bucket, 99):
        print('99 용량 사용')
    else:
        print('가용 용량이 작아서 99 용량을 처리할 수 없음')
    print(bucket)

    if deduct(bucket, 3):
        print('3 용량 사용')
    else:
        print('가용 용량이 작아서 3 용량을 처리할 수 없음')
    print(bucket)

# 이 구현의 문제점은 버킷이 시작할 때 가용 용량이 얼마인지 알 수 없다는 것이다.
# 가용용량이 0이 되면 버킷에 새로운 가용 용량을 할당하기 전까지 deduct는 항상 False를 반환한다.
# 하지만 그 이유가 가용 용량을 다 소진해서인지 아니면 아직 버킷에 매 주기마다 재설정하도록 정해진 가용 용량을 받지 못해서인지 이유를 알기 어렵다.
# 이러한 문제를 해결하기 위해 이번 주기에 재설정된 가용 용량인 max_quota와 이번 주기에 수비한 용량의 합계인 quota_consumed를 추적하도록 클래스를 변경할 수 있다.
class NewBucket:
    def __init__(self, period):
        self.period_delta = timedelta(seconds=period)
        self.reset_time = datetime.now()
        self.max_quota = 0
        self.quota_consumed = 0

    def __repr__(self):
        return (f'NewBucket(max_quota={self.max_quota}, '
                f'quota_consumed={self.quota_consumed})')

    # 원래의 Bucket 클래스와 인터페이스를 동일하게 제공하기 위해 @property 데코레이터가 붙은 메서드를 사용해 클래스의 두 애트리뷰트
    # (max_quota, quota_consumed)에서 현재 가용 용량을 그때그때 계산한다.
    @property
    def quota(self):
        return self.max_quota - self.quota_consumed

    # full과 deduct 함수가 quota 애트리뷰트에 값을 할당할 때는 현재 사용방식에 맞춰 특별한 동작을 수행해야한다.
    @quota.setter
    def quota(self, amount):
        delta = self.max_quota - amount
        if amount == 0:
            # 새로운 주기가 되고 가용 용량을 재설정하는 경우
            self.quota_consumed = 0
            self.max_quota = 0
        elif delta < 0:
            # 새로운 주기가 되고 가용 용량을 추가하는 경우
            assert self.quota_consumed == 0
            self.max_quota = amount
        else:
            # 어떤 주기 안에서 가용 용량을 소비하는 경우
            assert self.max_quota >= self.quota_consumed
            self.quota_consumed += delta

def new_buckey():
    bucket = NewBucket(60)
    print('최초', bucket)
    fill(bucket, 100)
    print('보충 후', bucket)

    if deduct(bucket, 99):
        print('99 용량 사용')
    else:
        print('가용 용량이 작아서 99 용량을 처리할 수 없음')
    print('사용 후', bucket)

    if deduct(bucket, 3):
        print('3 용량 사용')
    else:
        print('가용 용량이 작아서 3 용량을 처리할 수 없음')

    print('여전히', bucket)

# 위 구현의 가장 좋은 점은 Bucket.quota를 사용하는 코드를 변경할 필요가 없고 이 클래스의 구현이 변경됐음을 알필요도 없다는 것이다.
# 새로운 방법은 제대로 작동하고, 추가로 max_quota와 quota_consumed에도 접근 할 수있다.
# @property를 사용하면 데이터 모델을 점진적으로 개선할 수 있다.
# ======================================================================================================================
# 메타클래스와 애트리뷰트

# 메타클래스를 사용하면 class 문을 가로채서 클래스가 정의될 떄마다 특별한 동작을 할 수 있다.
# 또한 동적으로 애트리뷰트 접근을 커스텀화해주는 내장 기능과 합쳐지면 간단한 클래스를 복잡한 클래스로 쉽게 변활할 수 있다.

# 세터와 게터 메서드 대신 평볌한 애트리뷰트를 사용하라.

# 다른 언어에서는 클래스에 게터나 세터 머서드를 명시적으로 정의하곤 한다.
class OldResistor:
    def __init__(self, ohms):
        self._ohms = ohms

    def get_ohms(self):
        return self._ohms

    def set_ohms(self, ohms):
        self._ohms = ohms

# 하지만 파이썬에선 세터와 게터를 구현할 필요가 전혀 없다.
# 대신 다음 코드와 같이 항상 단순한 공개 애트리뷰트로부터 구현을 시작하라.
class Resistor:
    def __init__(self, ohms):
        self.ohms = ohms
        self.voltage = 0
        self.current = 0

# 이렇게 애트리뷰트를 사용하면 필드를 제자리에서 증가시키는 등의 연산이 더 자연스럽고 명확해진다.
r1 = Resistor(50e3)
r1.ohms = 10e3
r1.ohms += 5e3
# print(r1.ohms)

# 나중에 애트리뷰트가 설정될 때 특별한 기능을 수행해야한다면, 애트리뷰트를 @property 데코레이터와 대응하는 setter 애튜리뷰트로 옮겨갈 수 있다.
# 다음 코드는 Registor라는 새 하위 클래스를 만든다. Registor에서 voltage 프로퍼티에 값을 대입하면 current 값이 바뀐다.
class VoltageResistance(Resistor):
    def __init__(self, ohms):
        super().__init__(ohms)
        self._voltage = 0

    # @property 데코레이터는 setter와 대응한다. voltage 호출 시 setter 메서드가 호출된다.
    @property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, voltage):
        self._voltage = voltage
        self.current = self._voltage / self.ohms

# 프로퍼티에 setter를 지정하면 타입을 검사하거나 클래스 프로퍼티에 전달된 값에 대한 검증을 수행할 수 있다.
# 다음 코드에서는 모든 저항값이 0옴보다 큰지 확인하는 클래스를 정의한다.
class BoundedResistance(Resistor):
    # BoundedResistance.__init__가 Resistor_init__를 호출하고 이 초기화 메서드는 다시 self.ohms = ohms라는 대입문을 싱행한다.
    # 이 대입으로 인핸 BoundedResistance에 있는 @ohms.setter 메서드가 호출되고, 이 세터 메서드는 객체 생성이 끝나기 전에 즉시 if문을 실행한다.
    def __init__(self, ohms):
        super().__init__(ohms)

    @property
    def ohms(self):
        return self._ohms

    @ohms.setter
    def ohms(self, ohms):
        if ohms <= 0:
            raise ValueError(f'저항 > 0이어야 합니다. 실제 값: {ohms}')
        self._ohms = ohms

# 심지어 @property를 사용해 부모 클래스에 정의된 애트리뷰트를 불변으로 만들 수도 있다.
class FixedResistance(Resistor):
    def __init__(self, ohms):
        super().__init__(ohms)

    @property
    def ohms(self):
        return self._ohms

    @ohms.setter
    def ohms(self, ohms):
        if hasattr(self, '_ohms'):
            raise AttributeError("Ohms는 불변객체입니다")
        self._ohms = ohms


def use_property():
    r2 = VoltageResistance(1e3)
    print(f'이전: {r2.current:.2f} 암페어')
    r2.voltage = 10
    print(f'이후: {r2.current:.2f} 암페어')

    r3 = BoundedResistance(1e3)

    # 잘못된 값을 대입하면 예외가 발생한다.
    # r3.ohms = 0
    # BoundedResistance(-5)

    # 프로퍼티에 값을 대입하면 예외가 발생한다.
    r4 = FixedResistance(1e3)
    # r4.ohms = 2e3

    # @property 메서드를 사용해 세터와 게터를 구현할 때는 게터와 세터 구현이 예기치 않은 동작을 수행하지 않도록 만들어야한다.
    # 예를들어 게터 프로퍼티 메서드안에서 다른 애트리뷰트를 설정하면 안 된다.
    # 객체 상태를 변경하는 것은 @property.setter 메서드 안에서만 이뤄지는 것이 좋다.
    # 또한 @property 메서드에선 느리거나 복잡한 작업(특히 I/O)에는 어울리지 않는다. 이런 경우에는 일반적인 메서드를 사용하라.

# ======================================================================================================================
if __name__ == "__main__":
    for mtd in [
        use_property,
        rikey_bucket,
        new_buckey,
        use_discripter,
        use_discripter_2,
        use_discripter_3,
        use_discripter_4
    ]:
        mtd()
        print('==================================================================')
