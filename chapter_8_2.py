# ======================================================================================================================
# 정렬된 시퀀스를 검색할 떄는 bisect를 사용하라
from bisect import bisect_left
data = list(range(10**5))
index = bisect_left(data, 91234)  # 정확히 일치
print(index)
index = bisect_left(data, 91234.56)  # 근접한 값과 일치
print(index)
# bisect 모듈이 사용하는 이진 검색 알고리즘의 복잡도는 로그 복잡도다. bisect는 모든 파이썬 객체에 대해 사용가능하다.
# ======================================================================================================================
# 생산자-소비자 큐로 deque를 사용해라
# 프로그램을 작성할 때 자주 쓰는 기능으로 선입선출(FIFO) 큐가 있다. 선입선출 큐를 생산자-소비자 큐라고 부르기도 한다.
# 종종 파이썬 프로그래머들은 리스트를 생산자 소비자 큐로 사용하곤 한다.
# 하지만 리스트 안의 원소 개수가 늘어나면 리스트 타입의 성능은 선형보다 더 나빠진다.
import collections
import timeit
import random
def print_results(count, tests):
    avg_iteration = sum(tests) / len(tests)
    print(f'\n원소 수: {count:>5,} 걸린시간: {avg_iteration:.6f}초')
    return count, avg_iteration


def list_overdue_benchmark(count):
    def prepare():
        to_add = list(range(count))
        random.shuffle(to_add)
        return [], to_add

    def run(queue, to_add):
        for i in to_add:
            queue.append(i)
            queue.sort(reverse=True)

        while queue:
            queue.pop()

    tests = timeit.repeat(
        setup='queue, to_add = prepare()',
        stmt=f'run(queue, to_add)',
        globals=locals(),
        repeat=100,
        number=1)

    return print_results(count, tests)

def print_delta(before, after):
    before_count, before_time = before
    after_count, after_time = after
    growth = 1 + (after_count - before_count) / before_count
    slowdown = 1 + (after_time - before_time) / before_time
    print(f'데이터 크기 {growth:>4.1f}배, 걸린 시간 {slowdown:>4.1f}배')

baseline = list_overdue_benchmark(500)
for count in (1_000, 1_500, 2_000):
    comparison = list_overdue_benchmark(count)
    print_delta(baseline, comparison)

# 이결과를 보면 리스트 타입에 있는 메서드가 거의 상수 시간 복잡도가 걸린다는 걸 볼 수 있다.
# 따라서 데이터 크기가 커짐에 따라 큐에 데이터를 넣는데 걸리는 전체 시간이 선형적으로 늘어난다.

# 다음 코드는 리스트를 queue 처럼 pop(0)을 통해 원소를 제거하는 방식이다.
print('=============================================================================================')
def list_return_benchmark(count):
    def prepare():
        queue = list(range(count))
        random.shuffle(queue)
        to_return = list(range(count))
        random.shuffle(to_return)
        return queue, to_return

    def run(queue, to_return):
        for i in to_return:
            queue.remove(i)

    tests = timeit.repeat(
        setup='queue, to_return = prepare()',
        stmt=f'run(queue, to_return)',
        globals=locals(),
        repeat=100,
        number=1)

    return print_results(count, tests)

baseline = list_return_benchmark(500)
for count in (1_000, 1_500, 2_000):
    comparison = list_return_benchmark(count)
    print_delta(baseline, comparison)

# 놀랍게도 리스트에서 pop(0)을 사용해 원소에서 큐를 빼내는 데 걸리는 시간이 큐 길이가 늘어남에 따라 제곱에 비례해 늘어나는 걸 볼 수 있다.
# 그 이유는 pop(0)을 하면 리스트의 모든 남은 원소를 제 위치로 옮겨야해서, 결과적으로 전체 리스트 내용을 다시 재대입하기 때문이다.

# 파이썬 collections 내장 모듈에는 deque 클래스가 들어있다. deque(데크)는 양방향 큐이며 양방향 데이터 출입모두 상수 시간이 걸린다.
# 따라서 데크는 FIFO 큐를 구현하는데 이상적이다.
print('=============================================================================================')
def dequeue_popleft_benchmark(count):
    def prepare():
        return collections.deque(range(count))

    def run(queue):
        while queue:
            queue.popleft()

    tests = timeit.repeat(
        setup='queue = prepare()',
        stmt='run(queue)',
        globals=locals(),
        repeat=1000,
        number=1
    )

    return print_results(count, tests)

baseline = dequeue_popleft_benchmark(500)
for count in (1_000, 1_500, 2_000):
    comparison = dequeue_popleft_benchmark(count)
    print_delta(baseline, comparison)

# ======================================================================================================================