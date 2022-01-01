# ======================================================================================================================
# 이터레이터나 제너레이터를 다룰 때는 itertools를 사용하라.
# itertools 내장 모듈에는 이터레이터를 조직화하거나 사용할 때 쓸모 있는 여러 함수가 들어있다.
# 복잡한 이터레이터 코드를 작성하고 있다고 깨달을 때마다 혹시 쓸만한 기능이 없는지 찾아보자.
import itertools

# itertools를 3가지 범주로 나눠서 알아둬야하는 중요 함수를 설명한다.

# 첫 번째, 여러 이터레이터 연결.
def itertools_chain():
    # chain (연결)
    it = itertools.chain([1, 2, 3], [4, 5, 6])
    print(list(it))

    # repeat (한 값을 반복)
    it = itertools.repeat('안녕', 3)
    print(list(it))

    # cycle (내놓는 원소들을 반복)
    it = itertools.cycle([1, 2])
    result = [next(it) for _ in range(10)]
    print(result)

    # tee (이터레이터를 병럴적으로 만들 시)
    # 이때 만들어진 이터레이터 간의 소비속도가 같지 않으면 큐에 담아둬야 하므로 메모리가 낭비된다.
    it1, it2, it3 = itertools.tee(['하나', '둘'], 3)
    print(list(it1))
    print(list(it2))
    print(list(it3))

    # zip_longest
    # zip 내장 함수의 변종으로 여러 이터레이터 중 짧은 쪽 이터레이터의 원소를 다 사용했을 시, fillvalue로 지정한 겂을 채워준다.
    keys = ['하나', '둘', '셋']
    values = [1, 2]

    # 그냥 zip
    normal = list(zip(keys, values))
    print('zip:', normal)

    # zip_longest
    it = itertools.zip_longest(keys, values, fillvalue='없음')
    longest = list(it)
    print('zip_longest:', longest)

# # 두 번째 이터레이터에서 원소 거르기.
def itertools_filtering():
    # islice
    # 이터레이터를 복사하지 않으며 슬라이싱 하고 싶을 때 사용. 슬라이싱과 스트라이딩과 비슷하다.
    values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    first_five = itertools.islice(values, 5)
    print('앞에서 다섯 개:', list(first_five))

    middle_odds = itertools.islice(values, 2, 8, 2)
    print('중간의 홀수들:', list(middle_odds))

    # takewhile (술어(predicate)가 True를 반환할동안 원소를 돌려줌)
    values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    less_than_seven = lambda x: x < 7
    it = itertools.takewhile(less_than_seven, values)
    print(list(it))

    # dropwhile (False를 반환할동안 원소를 돌려줌)
    values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    less_than_seven = lambda x: x < 7
    it = itertools.dropwhile(less_than_seven, values)
    print(list(it))

    # filterfalse (filter의 반대. 즉 False를 반환하는 모든 원소를 돌려줌)
    values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    evens = lambda x: x % 2 == 0

    filter_result = filter(evens, values)
    print('Filter:', list(filter_result))

    filter_false_result = itertools.filterfalse(evens, values)
    print('Filter false:', list(filter_false_result))

# 세번째 , 원소의 조합 만들어내기
def itertools_combine():
    # accumulate (누적합)
    # 파라미터를 두 개 받는 함수를 반복적용하며 이터레이터 원소를 값 하나로 줄여준다. (fold 연산)
    # 이 함수가 돌려주는 이터레이터는 원본 이터레이터의 각 원소에 대해 누적된 결과를 내놓는다.
    values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    sum_reduce = itertools.accumulate(values)
    print('합계:', list(sum_reduce))

    def sum_modulo_20(first, second):
        output = first + second
        return output % 20

    modulo_reduce = itertools.accumulate(values, sum_modulo_20)
    print('20으로 나눈 나머지의 합계:', list(modulo_reduce))

    # product
    # 데카르트 곱을 반환한다.
    single = itertools.product([1, 2], repeat=2)
    print('리스트 한 개:', list(single)) # [(1, 1), (1, 2), (2, 1), (2, 2)]

    multiple = itertools.product([1, 2], ['a', 'b'])
    print('리스트 두 개:', list(multiple)) # [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')]

    # permutations (길이가 두 번째 원소인 순열)
    it = itertools.permutations([1, 2, 3, 4], 2)
    print(list(it))

    # combinations (길이가 두 번째 원소인 조합)
    it = itertools.combinations([1, 2, 3, 4], 2)
    print(list(it))

    # #combinations_with_replacement (길이가 두 번째 원소인 중복조합)
    it = itertools.combinations_with_replacement([1, 2, 3, 4], 2)
    print(list(it))


# ======================================================================================================================
# 제너레이터 안에서 throw로 상태를 변화시키지 말라.

# throw를 사용하면 제너레이터 안에서 Exception을 다시 던질 수 있다.
def generator_throw():
    class MyError(Exception):
        pass

    def my_generator():
        yield 1
        yield 2
        yield 3

    it = my_generator()
    # print(next(it))  # 1을 내놓음
    # print(next(it))  # 2를 내놓음
    # 오류가 나는 부분. 오류를 보고 싶으면 커멘트를 해제할것
    # print(it.throw(MyError('test error')))

    # 또한 throw를 호출해 제너레이터에 예외를 주입해도 try/except 복합문을 사용해 마지막 yield문을 둘러쌈으로서 예외를 잡아낼 수 있다.
    # 이 기능은 제너레이터와 제너레이터를 호출하는 쪽 사이에 양방향 통신수단을 제공한다.
    def my_generator():
        yield 1
        try:
            yield 2
        except MyError:
            print('MyError 발생!')
        else:
            yield 3
        yield 4

    it = my_generator()
    print(next(it))  # 1을 내놓음
    print(next(it))  # 2를 내놓음
    print(it.throw(MyError('test error')))

    # 이를 이용해 throw 메서드에 의존하는 타이머를 구현해보자.
    # 아래는 yield에서 Reset 예외가 발생할때마다 카운터가 period로 재설정되는 코드이다.

    class Reset(Exception):
        pass

    def timer(period):
        current = period
        while current:
            current -= 1
            try:
                yield current
            except Reset:
                current = period

    RESETS = [
        False, False, False, True, False, True, False,
        False, False, False, False, False, False, False]

    def check_for_reset():
        # 외부 이벤트를 폴링한다
        return RESETS.pop(0)

    def announce(remaining):
        print(f'{remaining} 틱 남음')

    def run():
        it = timer(4)
        while True:
            try:
                if check_for_reset():
                    current = it.throw(Reset())
                else:
                    current = next(it)
            except StopIteration:
                break
            else:
                announce(current)

    run()

    print('==================================================================')
    # 이 코드는 잘 작동되지만 잡음이 많다. 더 단순히 이터러블 컨테이너 객체(better way 31)을 통해 상태가 있는 클로저를 구현할 수 있다.
    class Timer:
        def __init__(self, period):
            self.current = period
            self.period = period

        def reset(self):
            self.current = self.period

        def __iter__(self):
            while self.current:
                self.current -= 1
                yield self.current

    #
    def run():
        timer = Timer(4)
        for current in timer:
            if check_for_reset():
                timer.reset()
            announce(current)

    run()


# ======================================================================================================================
# send로 제너레이터에 데이터를 주입하지 말라.
import math

# TODO 나중에 한 번 읽어보기
# better way 34
# send 메서드를 사용해 데이터를 제너레이터에 주입할 수 있다. 제너레이터는 send로 주입된 값을 yield 식이 반환하는 값을 통해 받으며,
# 이 값을 변수에 저장할 수 있다. 하지만 send와 yield from을 함께 사용하면 제너레이터 출력에 None이 불쑥불쑥 나타나는 의외의 결과를 얻을 수있다.
# 그러므로 합성할 제너레이터들의 입력으로 이터레이터를 전달하는 방식이 send보다 낫다. send는 가급적 사용하지 말라.
def transmit(output):
    if output is None:
        print(f'출력: None')
    else:
        print(f'출력: {output:>5.1f}')


def wave_cascading(amplitude_it, steps):
    step_size = 2 * math.pi / steps
    for step in range(steps):
        radians = step * step_size
        fraction = math.sin(radians)
        amplitude = next(amplitude_it) # 다음 입력 받기
        output = amplitude * fraction
        yield output

def complex_wave_cascading(amplitude_it):
    yield from wave_cascading(amplitude_it, 3)
    yield from wave_cascading(amplitude_it, 4)
    yield from wave_cascading(amplitude_it, 5)

def run_cascading():
    amplitudes = [7, 7, 7, 2, 2, 2, 2, 10, 10, 10, 10, 10]
    it = complex_wave_cascading(iter(amplitudes))
    for amplitude in amplitudes:
        output = next(it)
        transmit(output)
# ======================================================================================================================
# yield from을 사용해 여러 제너레이터를 합성하라

def use_yield_from():
    # 만약 제너레이터로 화면의 이미지를 움직이는 그래픽 프로그램이 있다고 치자.
    # 원하는 시각적 효과를 얻기 위해선 처음에는 빠르게 움직이다가 잠시 몸추고 다시 느리게 이동해야한다.
    def move(period, speed):
        for _ in range(period):
            yield speed

    def pause(delay):
        for _ in range(delay):
            yield 0

    def animate():
        for delta in move(4, 5.0):
            yield delta
        for delta in pause(3):
            yield delta
        for delta in move(2, 3.0):
            yield delta

    def render(delta):
        print(f'Delta: {delta:.1f}')
        # 화면에서 이미지를 이동시킨다

    def run(func):
        for delta in func():
            render(delta)

    run(animate)
    print('==================================================================')

    # 위코드를 yield from을 통해 간단화 하자.
    def animate_composed():
        yield from move(4, 5.0)
        yield from pause(3)
        yield from move(2, 3.0)

    run(animate_composed)

    # yield from은 단순히 잡음제거만이 아닌 실제로 성능도 좋아진다.


if __name__ == "__main__":
    for mtd in [
        use_yield_from,
        run_cascading,
        generator_throw,
        itertools_chain,
        itertools_filtering,
        itertools_combine
    ]:
        mtd()
        print('==================================================================')
