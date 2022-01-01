# ======================================================================================================================
# 긴 리스트 컴프리헨션보다는 제너레이터 식을 사용하라
# 리스트 컴프리헨션 (리스트 내포)의 문제점은 한번에 입력 시퀀스와 같은 수의 리스트를 만들기에 입력이 커지면 메모리가 상당히 많이 사용된다는 거다.
# 이 문제를 해결하기 위해 제너레이터식을 제공한다.
def use_gerater_func():
    value = [len(x) for x in open('sample_data/my_numbers.txt')]
    print(value) # bad way

    value = (len(x) for x in open('sample_data/my_numbers.txt'))
    print(value) # better way

    print(next(value))
    print(next(value))

    # 또한 제너레이터는 두 제너레이터를 합성할 수 있는 특징이 있다. 메모리 또한 효율적으로 사용된다,
    roots = ((x * x**0.5) for x in value)
    print(next(roots))

# ======================================================================================================================
# 인자에 대해 이터레이션할 때는 방어적이 돼라.
def defence_generator():
    # 만약 도시의 여행자 비율을 계산하는 함수가 있다고 하자.
    # 이 함수의 확장성을 높히기 위해 파일로부터 데이터를 받는다고 가정한다.
    def normalize(numbers):
        total = sum(numbers)
        result = []
        for value in numbers:
            percent = 100 * value / total
            result.append(percent)
        return result

    def read_visits(data_path):
        with open(data_path) as f:
            for line in f:
                yield int(line)

    # 이터레이터를 사용할 경우 read_visits에 파일의 값을 전달해도 아무런 결과가 나오지 않는다.
    # 이런 현상이 일어난 이유는 이터레이터가 결과를 단 한번만 만들어내기 때문이다.
    # 이미 StopIteration 예외가 발생한 이터레이터나 제너레이터를 다시 이터레이션해도 아무 결과도 얻을 수 없다.
    it = read_visits('sample_data/my_numbers.txt')
    percentages = normalize(it)
    print(percentages)

    # 또한 이미 소진된 이터레이터에 이터레이션을 수행해도 아무런 오류를 발생하지 않는다. 이는 for, list 등과같은 표준 라이브러리에 있는
    # 함수들이 일반적인 연산 도중에서 StopIteration 예외가 발생할 걸 가정하기 때문이다.
    # 이런 함수들은 출력이 없는 이터레이터와 이미 소진돼버린 이터레이터를 구분할 수 없다.
    it = read_visits('sample_data/my_numbers.txt')
    print(list(it))
    print(list(it))  # 이미 모든 원소를 다 소진했다

    # 이 문제를 해결하기 위해 입력 이터레이터를 명시적으로 소진시키고 이터레이터의 전체 내용을 리스트에 넣을 수 있다.
    # 그 후 데이터를 담아 둔 리스트에 대해 원하는 만큼 이터레이션을 수행할 수 있다.
    # 아래는 이전과 똑같은 함수를 바꿔서 방어적으로 복사하도록 만든 코드다.

    def normalize_copy(numbers):
        numbers_copy = list(numbers)  # 이터레이터 복사 (do not use)
        total = sum(numbers_copy)
        result = []
        for value in numbers_copy:
            percent = 100 * value / total
            result.append(percent)
        return result

    it = read_visits('sample_data/my_numbers.txt')
    percentages = normalize_copy(it)
    print(percentages)
    assert sum(percentages) == 100.0

    # 다만 이런 접근 방식은 입력 이터레이터의 내용을 복사하면 메모리가 과도하게 사용될 수 있다. 이 문제를 해결하는 다른 방법은
    # 호출될 때마다 새로 이터레이터를 반환하는 함수를 받는 것이다.

    # 람다식을 통해 read_visits 함수를 인자로 받아 호출될때마다 새로 이터레이터를 만들어낸다.
    def normalize_func(get_iter):
        total = sum(get_iter())  # 새 이터레이터 (better way)
        result = []
        for value in get_iter():  # 새 이터레이터
            print(value)
            percent = 100 * value / total
            result.append(percent)
        return result

    path = 'sample_data/my_numbers.txt'
    percentages = normalize_func(lambda: read_visits(path))
    print(percentages)
    assert sum(percentages) == 100.0

    # 다만 이런식으로 람다 함수를 넘기는 것은 보기에 좋지 않다. 같은 결과를 더 나은 방법으로 달성하는 건,
    # 이터레이터 프로토콜을 구현한 새로운 컨테이너 클래스 (__contain__메서드가 구현된 객체 [str, list, dict, set 등 in이나 len을
    # 사용가능한 객체. 모든 container는 iterable함])를 제공하는 것이다.
    # 파이썬의 for 루프나 연관식들은 for x in foo 같이 사용시 실제로는 iter(foo)를 호출한다.
    # 그러면 iter() 함수는 foo.__iter__라는 특별 매서드를 호출한다. (__iter__메서드는 반드시 이터레이터 객채(__next__)를 반환해야한다.
    # for 루프를 데이터가 소진 (StopIteration 예외발생)할 때까지 반복적으로 next 함수를 호출한다.

    # BEST WAY
    class ReadVisits:
        def __init__(self, data_path):
            self.data_path = data_path

        # 새로운 이터레이터 객체를 할당
        def __iter__(self):
            with open(self.data_path) as f:
                for line in f:
                    yield int(line)

    visits = ReadVisits(path)
    percentages = normalize(visits)
    print(percentages)
    assert sum(percentages) == 100.0

    # 이터레이터가 iter 내장 함수에 적달되는 경우는 받은 그대로 반환되고, 반대로 컨테이너 타입이 전달되면 새로운 이터레이터가 반환된다.
    # 이 습성을 이용해 반복적으로 이터레이션 할 수 없는 인자의 경우에는 TypeError를 발생시켜보자.
    def normalize_defensive_f(numbers):
        if iter(numbers) is numbers:  # 이터레이터가 iter 내장 함수에 전달되면 전달받은 이터레이터가 그대로 반환된다.
            raise TypeError('컨테이너를 제공해야 합니다')
        total = sum(numbers)
        result = []
        for value in numbers:
            percent = 100 * value / total
            result.append(percent)
        return result

    #아니면 더 간단히 내장 모듈을 사용할 수 있다.
    from collections.abc import Iterator

    def normalize_defensive(numbers):
        print(numbers)
        if isinstance(numbers, Iterator):  # 반복 가능한 이터레이터인지 검사하는 다른 방법
            raise TypeError('컨테이너를 제공해야 합니다')
        total = sum(numbers)
        result = []
        for value in numbers:
            percent = 100 * value / total
            result.append(percent)
        return result

    # 위 함수는 리스트와 ReadVisits에 대해 모두 제대로 작동한다. 둘 모두 이터레이터 프로토콜을 따르는 이터러블 컨테이너이기 때문이다.
    visits = [15, 35, 80]
    percentages = normalize_defensive(visits)
    assert sum(percentages) == 100.0

    visits = ReadVisits(path)
    percentages = normalize_defensive(visits)
    assert sum(percentages) == 100.0

    # 만약 컨테이너가 아닌 이터레이터면 예외를 발생한다.
    visits = [15, 35, 80]
    it = iter(visits) # 이터레이터가 iter 내장 함수에 전달되면 전달받은 이터레이터가 그대로 반환된다.
    # normalize_defensive(it) # 더는 반복할 수 없는 이터레이션이기때문에 에러발생


# ======================================================================================================================
# 리스트를 반환하기보다는 제너레이터를 사용하라
def use_generator():
    # ' '의 인덱스를 찾는 함수를 리스트로 만든다고 할 때
    def index_words(text):
        result = []
        if text:
            result.append(0)
        for index, letter in enumerate(text):
            # 이 부분이 핵심이지만 잡음이 많고 알아보기 힘들다.
            if letter == ' ':
                result.append(index + 1)
        return result

    address = '컴퓨터(영어: Computer, 문화어: 콤퓨터, 순화어:전산기)는 진공관'
    result = index_words(address)
    print(result)

    # yield를 사용한다고 하면
    def index_words_iter(text):
        if text:
            yield 0
        for index, letter in enumerate(text):
            if letter == ' ':
                yield index + 1

    # 위 함수가 호출되면 제너레이터 함수가 실제로 실행되지 않고 즉시 이터레이터를 반환한다.
    # 이터레이터가 next 내장함수를 호출할때마나 제너레이터는 다음 yield식까지 진행시킨다.
    # 제너레이터가 yield에 전달하는 값은 이터레이터에 의해 호출하는 쪽에 반환된다. (결과가 yield식에 의해 반환된다)
    # 다만 제너레이터는 호출하는 쪽에서 재사용이 불가능하다.

    it = index_words_iter(address)
    print(next(it))
    print(next(it))


# ======================================================================================================================
def use_substitution():
    # 대입식을 사용해 컴프리헨션 안에서 반복 잡업을 피해라

    # 아래와 같이 8개 단위로 각 부품이 몇 개씩 존재하는가 조회하는 로직이 있다고 하자. (부품이 개수가 0이 아닐 시 조회)
    stock = {
        '못': 125,
        '나사못': 35,
        '나비너트': 8,
        '와셔': 6,
    }

    order = ['나사못', '나비너트', '와셔', '클립']

    def get_batches(count, size):
        return count // size

    result = {}
    for name in order:
        count = stock.get(name, 0)
        batches = get_batches(count, 8)
        # 0은 if 문에서 거짓 취급이다
        if batches:
            result[name] = batches

    print(result)
    # >>> {'나사못': 4, '나비너트': 1}

    found = {name: batches for name in order if (batches := get_batches(stock.get(name, 0), 8))}
    print(found)

    # 다만 컴프리헨션을 사용할때는 순서를 주의해야한다.
    # result = {name: (tenth := count // 10)        # 에러식
    #          for name, count in stock.items() if tenth > 0}

    result = {name: tenth for name, count in stock.items()
              if (tenth := count // 10) > 0}

    # 더불어 루프 변수 누출의 이유 등으로 컴프리헨션에서 대입식을 사용하는 건 조건에만 사용하는 걸 권장한다.

    # 루프 변수 누출의 예
    half = [(last := count // 2) for count in stock.values()]
    print(f'{half}의 마지막 원소는 {last}')

    for count in stock.values():  # 루프 변수가 누출됨
        pass

    print(f'{list(stock.values())}의 마지막 원소는 {count}')

    # 대입식은 제너레이터의 경우에도 똑같은 방식으로 작동한다.
    found = ((name, batches) for name in order
             if (batches := get_batches(stock.get(name, 0), 8)))
    print(found)
    print(next(found))
    print(next(found))

# ======================================================================================================================
def not_over_two():
    # 컴프리헨션 내부에 제어 하위식을 사용할 수 있다.
    matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    squared = [[x**2 for x in row] for row in matrix]
    print(squared)

    # 다만 이런 제어 하위식을 세 개 이상 사용해선 안된다. 이런 경우 컴프리헨션을 사용하는 이점이 없어져 버린다.
    # 조건문 두 개, 루프 두 개, 혹은 조건문 한 개와 루프 한 개가 적당하다.
# ======================================================================================================================
# 컴프리헨션(내포)과 제너레이터

def use_comprehension():
    # map과 filter 대신 컴프리헨션을 사용해라
    a = [1, 2, 3, 4, 5]

    # 컴프리헨션
    squares = [x**2 for x in a]

    # map
    squares_alt = map(lambda x: x**2, a)

    # 컴프리헨션
    even_squares = [x**2 for x in a if x % 2 == 0]

    # map + filter
    even_squares_alt = map(lambda x: x**2, filter(lambda x: x % 2 == 0, a))

    assert squares == list(squares_alt)
    assert even_squares == list(even_squares_alt)

    # 딕셔너리나 집합도 가능
    even_squares_dict = {x: x ** 2 for x in a if x % 2 == 0}
    threes_cubed_set = {x ** 3 for x in a if x % 3 == 0}

    # 마찬가지로 map과 filter로 가면 너무 복잡해진다
    alt_dict = dict(map(lambda x: (x, x ** 2),
                        filter(lambda x: x % 2 == 0, a)))
    alt_set = set(map(lambda x: x ** 3,
                      filter(lambda x: x % 3 == 0, a)))


if __name__ == "__main__":
    for mtd in [
        use_comprehension,
        not_over_two,
        use_substitution,
        use_generator,
        defence_generator,
        use_gerater_func
    ]:
        mtd()
        print('==================================================================')
