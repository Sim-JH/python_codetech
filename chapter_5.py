from collections import defaultdict

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

        def __call__(self):
            self.added += 1
            return 0

    counter = BetterCountMissing()
    assert counter() == 0
    assert callable(counter) # 호출가능한 객체인 걸 볼 숭 ㅣㅆ다.

    # 아주 깔끔하고 사용하기 쉬운 best_way다.
    counter = BetterCountMissing()
    result = defaultdict(counter, current)  # __call__에 의존함
    for key, amount in increments:
        result[key] += amount
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
        func_hook
    ]:
        mtd()
        print('==================================================================')
