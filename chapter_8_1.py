# ======================================================================================================================
# 최적화하기 전에 프로파일링 하라
# 파이썬의 동적인 특성으로 인해 실행 시간 성능이 예상과 다를 수 있다.
# 느릴거라 생각한 연산이 실제로는 아주 빠르거나 (문자열 조작, 제너레이터)
# 빠를거라 생각한 기능이 실제로는 아주 느린 (애트리뷰트 접근, 함수 호출) 경우가 있다,
# 파이썬은 프로그램의 각 부분이 실행 시간을 얼마나 차지하는지 결정할 수 있게 해주는 프로파일러를 제공한다.
# 예를 들어 프로그램에서 알고리즘이 느린 이유를 알아보고 싶다고 하자. 다음은 삽입정렬을 이용해 데이터 리스트를 정렬하는 함수를 정의한다.
def insertion_sort(data):
    result = []
    for value in data:
        insert_value(result, value)
    return result

# 아래는 입력 배열을 선형 검색하는 아주 비효율적인 함수다,
def insert_value(array, value):
    for i, existing in enumerate(array):
        if existing > value:
            array.insert(i, value)
            return
    array.append(value)

from random import randint
max_size = 10**4
data = [randint(0, max_size) for _ in range(max_size)]
test = lambda: insertion_sort(data)

# 파이썬에는 두 가지 내장 프로파일러가 있다. 하나는 순수 파이썬으로 작성됐고(profile) 다른 하나는 C확장 모듈로 되어있다.
# 이중 후자가 프로그램 성능에 더 적은 영향을 끼친다.
from cProfile import Profile

# Profile의 runcall로 테스트 함수를 실행한다.
profiler = Profile()
profiler.runcall(test)

# 테스트 함수가 실행되고 나면 pstats 내장 모듈의 Stats 클래스를 사용해 성능 통계를 추출할 수 있다.
from pstats import Stats

stats = Stats(profiler)
stats.strip_dirs()
stats.sort_stats('cumulative')   # 누적 통계
stats.print_stats()

# 출력은 함수별로 정보가 정리된 표가 있다. 이때 표에 정리된 데이터는 runcall 메서드가 실행되면서 프로파일러가 활성화돼 있는 동안만 샘플링된다.
# 각 열은 다음 의미를 가진다.
# ncalls: 함수가 호출된 횟수
# tottime: 함수를 실행하는 데 걸린 시간의 합계. 대상 함수가 다른 함수를 호출한 경우, 이 다른 함수를 실행하는데 걸린 시간은 제외된다.
# percall: 함수가 호출될 때마다 걸린 시간의 평균. 이 값은 tottime을 ncalls로 나눈 값과 같다.
# cumtime: 함수를 실행할 떄 걸린 누적 시간. 이 시간에는 대상 함수가 호출한 다른 함수를 실행하는데 걸린 시간을 포함한다.
# percall: cumtime을 ncalls로 나눈 값과 같다.

# 해당 프로파일러 통계를 보면 누적 시간으로 CPU를 가장 많이 사용한 함수는 insert_value 함수라는 걸 알 수 있다.
# 이 함수를 bisect 내장모듈을 사용해 다시 구현해보자.
from bisect import bisect_left

def insert_value(array, value):
    i = bisect_left(array, value)
    array.insert(i, value)

test = lambda: insertion_sort(data)

profiler = Profile()
profiler.runcall(test)

stats = Stats(profiler)
stats.strip_dirs()
stats.sort_stats('cumulative')   # 누적 통계
stats.print_stats()

# 누적시간이 100배 가까이 줄어들었음을 알 수 있다.
# 전체 프로그램을 프로파일링 했는데, 공통 유틸리티 함수가 대부분의 실행 시간을 차지한다는 사실을 발견할 때도 있다.
# 프로그램의 여러 부분에서 이런 유틸리티 함수를 호출하기 때문에 프로파일러의 디폴트 출력을 사용하면 이런 상황을 제대로 이해하기 어려울 수 있다.
# 다음 프로그램에서는 두 함수가 반복적으로 my_utility 함수를 호출한다.
def my_utility(a, b):
    c = 1
    for i in range(100):
        c += a * b

def first_func():
    for _ in range(1000):
        my_utility(4, 5)

def second_func():
    for _ in range(10):
        my_utility(1, 3)

def my_program():
    for _ in range(20):
        first_func()
        second_func()

# 이 코드를 프로파일링하고 print_stats의 디폴트 옵션으로 통계를 출력하면 통계를 해석하기 어렵다.
test = lambda: my_program()

profiler = Profile()
profiler.runcall(test)

stats = Stats(profiler)
stats.strip_dirs()
stats.sort_stats('cumulative')   # 누적 통계
stats.print_stats()

# my_utility 함수가 실행 시간의 대부분을 차지하는 것은 분명하다. 하지만 이 함수가 왜 이렇게 많이 호출됐는지 즉시 알아보기는 어렵다.
# 프로그램 코드를 살펴보면 my_utility를 호출하는 부분이 여러 곳이라는 사실을 알 수 있지만, 여전히 혼란스러울 뿐이다.
# 이런 상황을 처리하고자 파이썬 프로파일러는 각 함수를 프로파일링한 정보에 대해 그 함수를 호출한 함수들이 얼마나 기여했는지를 보여주는
# print_callers 메서드를 제공한다.
stats.print_callers()

# 이 프로파일러 정보 표는 왼쪽에 호출된 함수를, 오른쪽에 그 함수를 호출한 함수를 보여준다.
# 다음 표를 보면 first_func가 my_utility 함수를 가장 많이 썼다는 점을 분명히 알 수 있다.

# ======================================================================================================================
