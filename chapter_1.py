def pick_fruit():
    import random
    if random.randint(1,10) > 2:   # 80% 확률로 새 과일 보충
        return {
            '사과': random.randint(0,10),
            '바나나': random.randint(0,10),
            '레몬': random.randint(0,10),
        }
    else:
        return None # return None과 Fasle는 조건문 상 같은 취급

def make_juice(fruit, count):
    if fruit == '사과':
        return [('사과주스', count/4)]
    elif fruit == '바나나':
        return [('바나나스무디',count/2)]
    elif fruit == '레몬':
        return [('레모네이드',count/1)]
    else:
        return []

def use_assignment():
    # 대입식을 사용해 반복을 피해라.
    fresh_fruit = {
        '사과': 10,
        '바나나': 8,
        '레몬': 5,
    }

    # 키값을 하나 가져와서 그 같이 0이 아닌지 확이하려면 조건문을 사용시 잡음이 많이 발생한다.
    # 하지만 대입식을 쓰면 이런 유형의 코드를 콕집어서 처리할 수 있다.

    # 우선 count 변수에 값을 삽입하고 대입된 값을 바탕으로 if문이 작동한다.
    # dict.get()는 key에 해당하는 calu를 돌려준다. 이 때, 2번째 인자는 해당 key가 없을 경우 받아올 default이다.
    # 즉 레몬 키가 있는 지금은 5를 받아서 count에 대입하고 없다면 0을 받아와서 else 문을 탄다.
    if count := fresh_fruit.get('레몬', 0):
        print('레모네이드를 만든다', count)
    else:
        print('재고가 없다.', count)

    # 비슷한 로직을 풀어서 보자
    count = fresh_fruit.get('사과', 0) # 사과 key가 있다면 해당 value 없다면 0
    if count >= 4: # count가 4보다 크면 if 조건 아니면 else 조건
        print('사과 주스를 만든다.', count)
    else:
        print('재고가 없다.', count)

    # 대입문을 사용하면 아래처럼 줄일 수 있다.
    if (count := fresh_fruit.get('사과', 0)) >= 4:
        print('사과 주스를 만든다.', count)
    else:
        print('재고가 없다.', count)

    # 응용하면 switch/case와 같이 쓸 수 있다. (파이썬에는 switch/case가 없음)
    if (count := fresh_fruit.get('바나나', 0)) >= 2:
        print('바나나: ', count)
    elif (count := fresh_fruit.get('사과', 0)) >= 4:
        print('사과: ', count)
    elif count := fresh_fruit.get('레몬', 0):
        print('레몬: ', count)
    else:
        print('아무것도 없음', count)

    # do while이 없어서 생기는 불편함도 개선할 수 있다.

    # 보통 do while을 쓸 때.
    bottles = []
    while True:  # 무한루프
        fresh_fruit = pick_fruit()

        if not fresh_fruit:  # 중간에서 끝내기
            break

        for fruit, count in fresh_fruit.items():
            batch = make_juice(fruit, count)
            # extend는 [1, 2, 3]에 extend[4, 5]로 [1, 2, 3, 4, 5] 같은 식으로 추가가 가능
            bottles.extend(batch)

    print(bottles)

    bottles = []

    while fresh_fruit := pick_fruit():
        for fruit, count in fresh_fruit.items():
            batch = make_juice(fruit, count)
            bottles.extend(batch)

    print(bottles)


def use_zip():
    # 여러 이터레이터에 대해 나란히 루프를 수행하려면 zip을 사한다
    names = ['Cecilia', '남궁민수', '毛泽东']
    counts = [len(n) for n in names]
    max_count = 0
    longest_name=''

    # names와 counts를 나란히 언패킹하며 이터레이터의 원소를 하나씩 소비한다
    # 만약 두 이터레이터의 길이가 다르다면 한 쪽의 이터레이터가 끝날 시 동작이 동료된다.
    for name, count in zip(names, counts):
        if count > max_count:
            longest_name = name
            max_count = count
    print(longest_name, max_count)

    # zip_longest를 사용하면 한쪽의 이터레이터가 끝나도 계속 반복을 진행한다.
    # 이때 먼저 끝난 쪽의 이터레이터에는 fillvalue(default=None)값이 들어간다.
    import itertools

    names.append('Rosalind')
    for name, count in itertools.zip_longest(names, counts):
        print(f'{name}: {count}')

def use_enumerate():
    # range로 인덱스의 시퀀스를 가져오기보다는 enumerate를 사용하라
    flavor_list = ['바닐라', '초콜릿', '피칸', '딸기']

    # 두 번째 인자 1은 1부터 인덱스를 시작한다는 의미
    for i, flavor in enumerate(flavor_list, 1):
        print(f'{i}: {flavor}')

def use_unpacking():
    # 파이썬은 한 문장 안에서 여러 값을 대입할 수 있는 언패킹 분법이 있다. ex. a, b = c
    # 언패킹은 모든 이터러블에 적용할 수 있고 이터러블이 여러 계층으로 내포된 경우도 적용할 수있다
    snacks = [('베이컨', 350), ('도넛', 240), ('머핀', 190)]

    for rank, (name, calories) in enumerate(snacks, 1):
        print(f'#{rank}: {name}은 {calories} 칼로리입니다.')

def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode('utf-8')
    else:
        value = bytes_or_str
    return value  # str 인스턴스

def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode('utf-8')
    else:
        value = bytes_or_str
    return value  # bytes 인스턴스

def str_and_bytes():
    # str과 bytes의 차이점

    # str 인스턴스에는 유니코드 코드포인트가 들어간다
    # str 인스턴스에는 직접 대응하는 이진 인코딩이 없다
    # 유니코드 데이터를 이진 데이터로 변환하려면 str의 encode 메서드를 호출해야한다.
    str_ = 'a\u0300 propos'
    print('str_: ', list(str_))
    print(str_)

    # bytes 인스턴스에는 부호가 없는 8바이트 데이터가 그대로 들어간다
    # bytes 인스턴스에는 직접 대응하는 텍스트 인코딩이 없다
    # 이진 데이터를 유니코드 데이터로 변환하려면 bytes의 decode 메서드를 호출해야한다.
    bytes_ = b'h\x65llo'
    print('bytes_: ', list(bytes_))
    print(bytes_)

    # encode와 decode 모두 원하는 방식을 명시적으로 지정할 수도 있고 시스템의 기본 설정을 받아들일 수 있다
    # encode는 다양한 텍스트 인코딩으로 입력 데이터를 받아들일 수 있고 출력텍스트 인코딩을 제한할 수 있도록 코딩해야한다.

    # bytes나 str 인스턴스를 받아서 항상 str을 반환 (repr()는 str()과 비슷)
    # str() 은 입력 받은 객체의 문자열 버전을 반환
    # repr() 는 어떤 객체의 ‘출력될 수 있는 표현’(printable representation)을 문자열의 형태로 반환한다.
    print(repr(to_str(b'foo')))
    print(repr(to_str('bar')))
    print(repr(to_str(b'\xed\x95\x9c')))  # UTF-8에서 한글은 3바이트임

    # bytes나 str 인스턴스를 받아서 항상 bytes나 반환
    print(repr(to_bytes(b'foo')))
    print(repr(to_bytes('bar')))
    print(repr(to_bytes('한글')))


if __name__ == "__main__":
    for mtd in [
        str_and_bytes,
        use_unpacking,
        use_enumerate,
        use_zip,
        use_assignment,
    ]:
        print('==================================================================')
        mtd()


