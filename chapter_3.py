# 아래 함수가 작동되는 이유는 세 가지가 있다.
# 1. 파이썬이 closure를 지원한다. closure 란 자신이 정의된 영역 밖의 변수를 참조하는 함수다.
#    그로인해 helper 함수가 sort_priority 함수의 group인자에 접근할 수 있다.
# 2. 파이썬에서 함수가 일급 시민 객체이다. 일급 시민 객체란 직접 가르킬 수 있고, 변수에 대입하거나 인자로 전달할 수 있으며,
#    식이나 if문에서 함수를 비교하거나 반환하는 것등이 가능하다는 것을 의미한다. 이 성질로 인해 sort 메서드는 클로저 함수를 key로 받을 수 있다.
# 3. 파이썬에는 시퀀스(튜플 포함)를 비교하는 구체적인 규칙이 있다. 파이썬은 시퀀스를 비교할 때 0번 인덱스에 있는 값을 비교한 다음, 같다면
#    다음 1번 인덱스 값을 비교하는 동작을 끝까지 반복한다. 이로인해 helper 클로저가 반환하는 튜플이 서로들 두 그룹을 정렬하는 기준 역할을 한다.
def sort_priority(values, group):
    def helper(x):
        # 튜플 구조를 이용해 x가 group 안에 있다면 (0, value) 없다면 (1, value) 식으로 정하여 일단 0과 1순으로 정렬 후,
        # 두 번째 인자인 value로 정렬하도록 하는 식
        if x in group:
            return (0, x)
        return (1, x)
    # 기준이 여러개인 sort를 할 시에는 튜플을 이용한다. https://ooyoung.tistory.com/59
    values.sort(key=helper)


def variable_and_closure():
    # 변수 영역과 클로저의 상호작용 방식을 이해하기

    # list를 정렬하되, 정렬한 리스트의 앞쪽에는 우선순위를 부여한 몇몇 숫자를 위치시켜야 한다고 가정하자.
    # 복잡한 기준을 사용해 정렬할 때는 key 파라미터를 사용하는 게 좋다.
    numbers = [8, 3, 1, 2, 5, 4, 7, 6]
    group = {2, 3, 5, 7}
    sort_priority(numbers, group)
    print(numbers)


def careful_divide(a: float, b: float) -> float:
    """a를 b로 나눈다.

    Raises:
        ValueError: b가 0이어서 나눗셈을 할 수 없을 때
    """
    try:
        return a / b
    except ZeroDivisionError as e:
        raise ValueError('잘못된 입력')


def raise_error():
    # None을 반환하기보다는 예외를 발생시켜라

    # None 반환은 조건문에서 False와 동등한 취급이기에 잘못해석되는 에러가 발생하기 쉽다.
    # 이런 에러를 줄이는 좋은 방법은 특별한 경우에 결코 None을 반환하지 않는 것이다.
    # 대신 Exception을 호출한 쪽으로 발생시켜 호출자가 이를 처리하게 한다.
    # 또한 함수의 인터페이스에 어떤 예외를 발생시킬지 명시한다.
    x, y = 5, 2

    try:
        result = careful_divide(x, y)
    except ValueError:
        print('잘못된 입력')
    else:
        print('결과는 %.1f 입니다.' % result)


def get_avg_ratio(numbers):
    average = sum(numbers) / len(numbers)
    scaled = [x / average for x in numbers]
    scaled.sort(reverse=True)
    return scaled

def return_unpacking():
    # 함수가 여러 값을 반환하는 경우 절대로 네 값 이상을 언패킹하지 말라.

    # 함수에서 return 시 언패킹을 사용할 수 있다.
    lengths = [63, 73, 72, 60, 67, 66, 71, 61, 72, 70]

    longest, *middle, shortest = get_avg_ratio(lengths)
    print(f'최대 길이: {longest:>4.0%}')
    print(f'최소 길이: {shortest:>4.0%}')
    # [print(f'중간 길이: {mid:>4.0%}') for mid in middle]

    # 다만 이런 식으로 언패킹을 할 때는 변수를 네 개 이상 사용해선 안된다. 햇갈리기 쉽고 이상이 생겼을 때 찾기도 힘들기 때문.
    # 만약 필요할땐 경량 클래스나 namedtuple을 반환하도록 해라.


if __name__ == "__main__":
    for mtd in [
        return_unpacking,
        raise_error,
        variable_and_closure
    ]:
        print('==================================================================')
        mtd()