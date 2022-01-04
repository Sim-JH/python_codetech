import os

from collections import defaultdict
from threading import Thread
# ======================================================================================================================
# 객체를 제너릭하게 구성하려면 @classmethod를 통한 다형성을 활용하라

# 파이썬에서는 객체뿐 아니라 클래스도 다형성을 지원한다.
# 이는 같은 인터페이스를 만족하거나 같은 추상 클래스를 공유하는 많은 클래스가 서로 다른 기능을 제공할 수 있다는 뜻이다.
# 추상 클래스는 미구현 메서드를 하나 이상 가지며, 자식클래스에서 해당 클래스를 반드시 구현하도록 강제하는 걸 뜬한다.

# 추상 클래스
class InputData:
    # 추상 매서드. 상속받은 자식 클래스는 반드시 해당 메서드를 구현해야함
    def read(self):
        # 해당 메소드가 구현되지 않으면 강제적으로 에러 발생
        raise NotImplementedError

# 경로의 파일을 읽음
class PathInputData(InputData):
    def __init__(self, path):
        super().__init__()
        self.path = path

    def read(self):
        with open(self.path) as f:
            return f.read()

# 추상 클래스
class Worker:
    def __init__(self, input_data):
        self.input_data = input_data
        self.result = None

    def map(self):
        raise NotImplementedError

    def reduce(self, other):
        raise NotImplementedError

# 새줄 문자의 개수를 샘
class LineCountWorker(Worker):
    def map(self):
        data = self.input_data.read()
        self.result = data.count('\n')

    def reduce(self, other):
        self.result += other.result


# 위 클래스들을 도우미 함수들을 통해 객체로 만들어 연결한다.
# 클래스 기반 맵 리듀스 구현
def generate_inputs(data_dir):
    for name in os.listdir(data_dir):
        yield PathInputData(os.path.join(data_dir, name))


def create_workers(input_list):
    workers = []
    for input_data in input_list:
        workers.append(LineCountWorker(input_data))
    return workers


def execute(workers):
    threads = [Thread(target=w.map) for w in workers]
    for thread in threads: thread.start()
    for thread in threads: thread.join()

    first, *rest = workers
    for worker in rest:
        first.reduce(worker)
    return first.result


def mapreduce(data_dir):
    inputs = generate_inputs(data_dir)
    print(inputs)
    workers = create_workers(inputs)
    print(workers)
    return execute(workers)


def not_use_classmethod():
    import random

    # 이 코드는 잘 작동하나 함수가 전혀 제너릭하지 않다는 문제가 있다.
    # 다른 InputData나 Worker 하위 클래스를 사용하고 싶다면 각 하위 클래스에 맞게 generate_inputs, create_workers, mapreduce를 재작성해야한다.
    # 이 문제의 핵심은 객체를 구성할 수 있는 제너릭한 방법이 필요하다는 점이다.
    # 다른 언어에서는 다형성을 활용해 이 문제를 해결할 수 있다. 파이썬에서는 생성자 매서드가 __init__밖에 없다.
    # InputData의 모든 하위클래스가 똑같은 생서자만 제공해야한다는 것은 불합리하다.
    def write_test_files(tmpdir):
        os.makedirs(tmpdir)
        for i in range(100):
            with open(os.path.join(tmpdir, str(i)), 'w') as f:
                f.write('\n' * random.randint(0, 100))

    tmpdir = './sample_data/test_inputs'
    write_test_files(tmpdir)

    result = mapreduce(tmpdir)
    print(f'총 {result} 줄이 있습니다.')

    # 위 문제를 해결하는 가장 좋은 방법은 클래스 메서드 다형성을 사용하는 것이다.
    # 이 방식은 InputData.read에서 사용했던 인스턴스 메서드의 다형성과 같은데, 클래스로 만들어낸 개별 객체에 적용되지 않고 클래스 전체에 적용된다.
    # 기존 클래스를 수정해보자.

class GenericInputData:
    def read(self):
        raise NotImplementedError

    # generate_inputs는 GenericInputData의 하위클래스가 객체를 생성하는 방법을 알려주는 설정 정보 딕셔너리를 인자로 받는다.
    @classmethod
    def generate_inputs(cls, config):
        raise NotImplementedError


# 입력 파일이 들어 있는 디렉토리를 찾기위해 generate_inputs의 config를 사용한다.
class GenericPathInputData(GenericInputData):
    def __init__(self, path):
        super().__init__()
        self.path = path

    def read(self):
        with open(self.path) as f:
            return f.read()

    @classmethod
    def generate_inputs(cls, config):
        data_dir = config['data_dir']
        for name in os.listdir(data_dir):
            yield cls(os.path.join(data_dir, name))

# 비슷한 방식으로 GenericWorker 클래스안에 create_workers 도우미 메서드를 추가한다.
class GenericWorker:
    def __init__(self, input_data):
        self.input_data = input_data
        self.result = None

    def map(self):
        raise NotImplementedError

    def reduce(self, other):
        raise NotImplementedError

    # 이 도우미 매서드는 GenericInputData의 하위 타입이어야하는 input_class를 인자로 받는다.
    # input_class는 필요한 입력을 생성해준다.
    # GenericWorker의 구체적인 하위 타입의 인스턴스를 만들때는 create_workers가 받은 cls()를 제너릭 생성자로 사용한다.
    @classmethod
    def create_workers(cls, input_class, config):
        workers = []
        # input_class.generate_inputs 호출이 여기서 보여주려는 클래스 다형성의 예다.
        # create_workers가 __init__메서드를 직접 호출하지 않고 cls()를 호출함으로서 다른 방법으로 GenericWorker 객체를 만들 수 있다.
        for input_data in input_class.generate_inputs(config):
            workers.append(cls(input_data))
        return workers

# 이런 변경이 GenericWorker 하위 클래스에 미치는 영향은 부모클래스를 바꾸는 것 뿐이다.
class GenericLineCountWorker(GenericWorker):
    def map(self):
        data = self.input_data.read()
        self.result = data.count('\n')

    def reduce(self, other):
        self.result += other.result

def use_classmethod():
    #mapredyce 함수가 create_workers를 호출하게 변경해서 mapreduce를 완전한 재너릭 함수로 만들 수 있다.
    def mapreduce(worker_class, input_class, config):
        workers = worker_class.create_workers(input_class, config)
        return execute(workers)
    tmpdir = './sample_data/test_inputs'
    config = {'data_dir': tmpdir}
    result = mapreduce(GenericLineCountWorker, PathInputData, config)
    print(f'총 {result} 줄이 있습니다.')


# ======================================================================================================================
# 간단한 인터페이스의 경우 클래스 대신 함수를 받아라

# 파이썬 내장 API 중 상당수는 함수를 전달해서 동작을 원하는 대로 바꿀 수 있게 해준다.
# 만약 API가 실행되는 관정에서 전달받은 함수를 실행하는 경우, 이런 함수를 훅(hook)이라고 부른다.
def func_hook():
    # 예를 들어 sort 메서드의 경우 key인자로 함수를 받을 수 있다.
    def key_hook():
        names = ['소크라테스', '아르키메데스', '플라톤', '아리스토텔레스']
        names.sort(key=len) # key 훅으로 len 내장 함수를 받음.
        print(names)

    key_hook()

    # 훅을 추상 클래스를 통해 정의해야하는 언어도 있지만, 파이썬은 단순히 인자와 반환 값이 정의된 상태가 없는 훅으로 사용하는 경우가 많다.
    # 함수는 정의하거나 기술하기가 클래스보다 쉬우므로 훅으로 사용하기에 이상적이다. 또한 파이썬은 함수를 일급 시민 객체로 취급하기에 함수를 훅으로 사용할 수 있다.
    # 에를 들어 defaultdict 클래스의 동작을 사용자정의 하고 싶다고 하자.
    # defaultdict에는 딕셔너리 안에 없는 키에 접근할 경우 인자가 없는 함수를 전달 가능하다.
    def log_missing():
        print('키 추가됨')
        return 0

    current = {'초록': 12, '파랑': 3}
    increments = [
        ('빨강', 5),
        ('파랑', 17),
        ('주황', 9),
    ]
    # log_missing는 접근시 해당 키가 없을때 실행되는 기본값(default_factory)
    result = defaultdict(log_missing, current)
    print('이전:', dict(result))
    # 키가 없다면 키와 값 추가 있다면 값 +
    for key, amount in increments:
        result[key] += amount
    print('이후:', dict(result))

    # log_missing 같은 함수를 사용할 수 있다면 정해진 동작과 부수 효과(side effect)를 분리할 수 있다.
    # 예를 들어 defaultdick에 전달되는 키가 존재하지 않는 총 횟수를 세고 싶다고 하자.
    # 여러가지 방법이 있는데, 아래는 클로저를 사용한방법이다.

    def increment_with_report(current, increments):
        added_count = 0

        def missing():
            nonlocal added_count  # 상태가 있는 클로저
            added_count += 1
            return 0

        result = defaultdict(missing, current)
        for key, amount in increments:
            result[key] += amount

        return result, added_count

    result, count = increment_with_report(current, increments)
    print('closer: ', result, count)
    assert count == 2

    # 더 나은 방법은 상태를 추적하는 작은 클래스를 정의하는 거다.
    # 다른 언어에서는 불가능하지만 파이썬에선 CountMissing.missing 메서드를 직접 defaultdict의 디폴트 값으로 전달할 수 있다.
    class CountMissing:
        def __init__(self):
            self.added = 0

        def missing(self):
            self.added += 1
            return 0

    counter = CountMissing()
    result = defaultdict(counter.missing, current)  # 클래스안의 메서드를 직접 전달.
    for key, amount in increments:
        result[key] += amount
    print('class: ', result, counter.added)
    assert counter.added == 2

    # 하지만 위의 경우 CountMissing.missing의 목적이 무엇인지 사용하는 부분을 보기 전에는 이해하기 어렵다.
    # 이런 경우를 더 명확히 표현하기위해 클래스에 __call__ 특별 메서드를 정의할 수있다. __call__을 사용하면 객체를 함수처럼 호출할 수 있다.
    class BetterCountMissing:
        def __init__(self):
            self.added = 0

        # 호출 시마다 added 가 1씩 증가한다.
        def __call__(self):
            self.added += 1
            return 0

    counter = BetterCountMissing()
    assert counter() == 0
    assert callable(counter) # 호출가능한 객체인 걸 볼 수 있다.

    # 아주 깔끔하고 사용하기 쉬운 best_way다.
    counter = BetterCountMissing()
    result = defaultdict(counter, current)  # __call__에 의존함
    print(result)
    for key, amount in increments:
        result[key] += amount
        print(result)
    assert counter.added == 2



# ======================================================================================================================
# 내장 타입을 여러 단계로 내포시키보다는 클래스를 합성해라

# 아래와 같이 클래스의 복잡도가 늘어나면 더 이상 딕셔너리, 리스트 등의 내장 타입을 사용하지 말고 계층구조를 사용해야한다.
# 코드에서 값을 관리하는 부분이 점점 복잡해지는 걸 깨달으면 즉시 해당 기능을 클래스로 분리해야한다.
class WeightedGradebook:
    def __init__(self):
        self._grades = {}

    def add_student(self, name):
        self._grades[name] = defaultdict(list)

    def report_grade(self, name, subject, score, weight):
        by_subject = self._grades[name]
        grade_list = by_subject[subject]
        grade_list.append((score, weight))

    def average_grade(self, name):
        by_subject = self._grades[name]
        score_sum, score_count = 0, 0

        for subject, scores in by_subject.items():
            subject_avg, total_weight = 0, 0

            for score, weight in scores:
                subject_avg += score * weight
                total_weight += weight

            score_sum += subject_avg / total_weight
            score_count += 1

        return score_sum / score_count


def bad_way_class():
    book = WeightedGradebook()
    book.add_student('알버트 아인슈타인')
    book.report_grade('알버트 아인슈타인', '수학', 75, 0.05)
    book.report_grade('알버트 아인슈타인', '수학', 65, 0.15)
    book.report_grade('알버트 아인슈타인', '수학', 70, 0.80)
    book.report_grade('알버트 아인슈타인', '체육', 100, 0.40)
    book.report_grade('알버트 아인슈타인', '체육', 85, 0.60)
    print(book.average_grade('알버트 아인슈타인'))


    ## ex) 튜플은 key를 지정할 수 없기에 원소가 3개 이상이면 다른 접근 방법을 생각해보는 게 좋다.
    grades = []
    grades.append((95, 0.45, '참 잘했어요'))
    grades.append((85, 0.55, '조금 만 더 열심히'))
    total = sum(score * weight for score, weight, _ in grades)
    total_weight = sum(weight for _, weight, _ in grades)
    average_grade = total / total_weight
    print(average_grade)

    # namedtuple로 튜플인자에 이름을 매길 수 있다.
    from collections import namedtuple
    Grade = namedtuple('Grade', ('score', 'weight'))
    g = Grade(95, 0.45)
    print(g, g.score, g.weight)

# 위 코드를 개선해보자
# 클래스를 활용해 리팩터링하기

# 각 기능에 따라 클래스를 분리한다.
class Subject:
    def __init__(self):
        from collections import namedtuple
        self._grades = []
        self.Grade = namedtuple('Grade', ('score', 'weight'))

    def report_grade(self, score, weight):
        self._grades.append(self.Grade(score, weight))

    def average_grade(self):
        total, total_weight = 0, 0
        for grade in self._grades:
            total += grade.score * grade.weight
            total_weight += grade.weight
        return total / total_weight


class Student:
    def __init__(self):
        self._subjects = defaultdict(Subject)

    def get_subject(self, name):
        return self._subjects[name]

    def average_grade(self):
        total, count = 0, 0
        for subject in self._subjects.values():
            total += subject.average_grade()
            count += 1
        return total / count


class Gradebook:
    def __init__(self):
        self._students = defaultdict(Student)

    def get_student(self, name):
        return self._students[name]

# 기능을 훨씬 깔끔하게 사용할 수 있다.
def better_way_class():
    book = Gradebook()
    albert = book.get_student('알버트 아인슈타인')
    math = albert.get_subject('수학')
    math.report_grade(75, 0.05)
    math.report_grade(65, 0.15)
    math.report_grade(70, 0.80)
    gym = albert.get_subject('체육')
    gym.report_grade(100, 0.40)
    gym.report_grade(85, 0.60)
    print(albert.average_grade())


# ======================================================================================================================
if __name__ == "__main__":
    for mtd in [
        bad_way_class,
        better_way_class,
        func_hook,
        not_use_classmethod,
        use_classmethod
    ]:
        mtd()
        print('==================================================================')
