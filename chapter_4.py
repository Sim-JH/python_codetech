# ======================================================================================================================



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
    use_comprehension(),
    not_over_two(),
    use_substitution()
