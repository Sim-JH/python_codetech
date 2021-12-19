from collections import defaultdict

# dict를 상속해 __missing__ 특별 메서드를 구현
class Pictures(dict):
    # 해당하는 키가 없을 경우 __missing__ 메서드가 자동으로 호출된다.
    def __missing__(self, key):
        value = open_picture(key)
        self[key] = value
        return value

def open_picture(profile_path):
    try:
        return open(profile_path, 'a+b')
    except OSError:
        print(f'경로를 열 수 없습니다: {profile_path}')
        raise


def use_missing():
    # defaultdict은 딕셔너리에 키가 없는 경우를 처리해주는 좋은 메서드지만 사용하기 적당하지 않은 경우도 있다.
    # 예를 들어 파일 시스템에 있는 SNS 프로필 사진을 관리하는 프로그램을 작성한다고 가정하자.
    # 필요할 때 파일을 읽고 쓰기 위해 프로필 사진의 경로와 열린 파일 핸들을 연관시켜주는 딕셔너리가 필요하다.

    # 아래 코드는 일반 dict 인스턴스를 사용하고 get 메서드와 대입을 통해 키가 딕셔너리에 있는 지 검사한다.
    pictures = {}
    path = 'sample_data/profile_1234.png'

    if (handle := pictures.get(path)) is None:
        try:
            handle = open(path, 'a+b') # a: append모드(없으면 생성), +: 읽고 쓰기용(updating), b: binary 모드
        except OSError:
            print(f'경로를 열 수 없습니다: {path}')
            raise
        else:
            pictures[path] = handle
    # read로 편지 내용을 읽을 때, seek으로 원하는 위치에서 부터 읽을 수 있다,..
    # ro.seek(offset, 기준점) (ro는 파일 객체) offest은 앞뒤 바이트 수. 거의 안씀.
    # 기준점은 0일 시 맨 앞, 1은 현재 2는 맨 끝(쓰기에서 이어쓸 때 사용)이다.
    handle.seek(0)
    image_data = handle.read()

    # 위의 과정을 setdefault로 구현한다면 open이 딕셔너리에 있는지 없는지 관계 없이 항상 호출되기에,
    # 같은 프로그램상에 존재하던 열린 파일과 혼동될 수 있는 새로운 파일 핸들이 생길 수 있다.
    # 이러면 open이 예외를 던지니 처리해야되는데, 문제는 except로 처리한 예외에 때문에 혼동이 생길 수 있다.
    try:
        handle = pictures.setdefault(path, open(path, 'a+b'))
    except OSError:
        print(f'경로를 열 수 없습니다: {path}')
        raise
    else:
        handle.seek(0)
        image_data = handle.read()

    # defaultdict의 경우에는 defaultdict의 생성자에 전달한 함수는 인자를 받을 수 없다는 문제가 있다.
    # 아래처럼 인자가 함수일 경우에는 defaultdict 객체를 생성시 인자를 넘겨줄 수 없다.
    # pictures = defaultdict(open_picture)
    # handle = pictures[path]
    # handle.seek(0)
    # image_data = handle.read()

    # 이런 상황은 생각보다 흔히 발생하기 때문에 파이썬은 다른 해법을 내장하여 제공한다.
    # dict 타입의 하위 클래스를 만들고 __missing__ 특별 메서드를 구현하면 키가 없는 경우를 처리하는 로직을 커스텀화할 수 있다.
    # 아래 코드는 앞의 예제와 똑같은 open_picture 도우미 함수를 활요하는 새로운 클래스를 정의해 키가없는 경우 파일을 여는 딕셔너리를 만든다.
    pictures = Pictures()
    handle = pictures[path]
    handle.seek(0)
    image_data = handle.read()
    # pictures[path]라는 딕셔너리 접근에서 path가 없다면 __missing__ 메서드가 호출된다.
    # 이 메서드는 키에 해당하는 디폴트 값을 생성해 딕셔너리에 넣어준 다음에 호출한 쪽에 그 값을 반환한다.
    # 그 이후에 딕셔너리에서 같은 경로에 접근하면 이미 해당 원소가 딕셔너리에 들어있으므로 호출되지 않는다.
    # __getattr__의 동작과 비슷하다.


class Visits_2:
    def __init__(self):
        self.data = defaultdict(set)

    def add(self, country, city):
        self.data[country].add(city)


class Visits:
    def __init__(self):
        self.data = {}

    def add(self, country, city):
        city_set = self.data.setdefault(country, set())
        city_set.add(city)


def use_defaultdict():
    # setdefault는 딕셔너리에 키값이 들어있는지 상과없이 value를 추가할 때 편리한 기능을 제공한다.
    visits = {
        '미국': {'뉴욕', '로스엔젤레스'},
        '일본': {'하코네'},
    }
    # setdefault 를 사용하는 경우
    visits.setdefault('프랑스', set()).add('칸')  # 짧다

    # 대입식을 사용하는 경우
    if (japan := visits.get('일본')) is None:  # 길다
        visits['일본'] = japan = set()

    japan.add('교토')

    print(visits)

    # 클래스를 이용하면 더 간단히 처리 가능하다.
    visits = Visits()
    visits.add('러시아', '예카테린부르크')
    visits.add('탄자니아', '잔지바르')
    print(visits.data)

    # 하지만 setdefault의 경우 주어진 나라가 data 딕셔너리에 있든 없든 호출할 때마다 새로운 set인스턴스를 만들기에 비효율적이다.
    # 그러므로 setdefault보다는 collectionse내장 모듈의 defaultdict 클래스를 쓰는 것이 훨씬 낫다.
    # defaultdict 클래스는 키가 없을 때 자동으로 디폴트 값을 저장해서 이런 용법을 간단히 처리해준다.
    visits = Visits()
    visits.add('영국', '바스')
    visits.add('영국', '런던')
    print(visits.data)
    # defaultdict을 사용하면 setdefault와 같이 불필요한 set이 만들어지는 경우가 없다.


def use_get_dict():
    # in을 사용하고 get으로 키를 받아라.
    # 딕셔너리의 내용은 동적이므로 어떤 키에 접근하거나 키를 삭제할 때 그 키가 딕셔너리에 없을 수도 있다.
    counters = {
        '품퍼니켈': 2,
        '사워도우': 1,
    }

    # 딕셔너리에는 키가 존재하면 값을 가져오고 존재하지 않으면 디폴트를 반환하는 흐름이 꽤 자주 반환한다.
    key = '밀'
    if key in counters:
        count = counters[key]
    else:
        count = 0

    counters[key] = count + 1
    print(counters)

    # 위의 경우를 KeyError 처리로 구현할 수도 있다.
    try:
        count = counters[key]
    except KeyError:
        count = 0

    key = '호밀'
    # 하지만 이 경우 가장 좋은 건 dict 내장의 get 메서드를 사용하는 것이다.
    # get의 두번째 인자는 키가 없을 경우 반환할 디폴트 값을 정할 수 있다.
    count = counters.get(key, 0)
    print(count)
    counters[key] = count + 1
    print(counters)

    # 만약 딕셔너리에 저장된 값이 리스트처럼 더 복잡한 경우라면 어떨 까
    # 위처럼 득표수만 세는 것이 아니라 어떤 사람이 어떤 유형의 빵에 투표했는지도 알고 싶은 경우에는 각 키마다 이름이 들어있는 리스트를 연관시킬 수 있다.
    # 그리고 해당하는 빵이 votes에 없다면 해당 key를 추가한다.
    # 만약 in을 사용해 해결한다면 키를 두번 읽어야하고, 키가 없는 경우에는 값을 대입해야한다.
    votes = {
        '바게트': ['철수', '순이'],
        '치아바타': ['하니', '유리'],
    }
    key = '브리오슈'
    who = '단이'

    if key in votes:
        names = votes[key]
    else:
        # key(브리오슈)가 없다면 해당하는 키로 빈 리스트를 만들고 그걸 다시 votes에 추가한다.
        votes[key] = names = []

    names.append(who)
    print(votes)

    # get을 사용해 리스트 값을 가져오려면 if 문안에 대입식을 사용하면 가독성이 훨씬 좋아진다.
    if (name := votes.get(key)) is None:
        votes[key] = names = []
    names.append(who)

    # dict 타입은 이 패턴을 더 간단히 사용할 수 있게 해주는 setdefault 메서드를 제동한다.
    # setdefault는 딕셔너리에서 키를 사용해 값을 가져오려고 시도하고 없다면 제공받은 디폴트를 대입 후, 키값을 반환한다.
    names = votes.setdefault(key, [])
    names.append(who)
    # 다만 setdefault는 사용을 권장하지 않는다. 바로의 위 함수 defaultdict를 참조하자.

class Tool:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

    def __repr__(self):
        return f'Tool({self.name!r}, {self.weight})'

def sort_with_key():
    # 리스트 내장 타입에는 리스트를 여러 기준에 따라 정렬 가능한 sort가 있다.
    # sort는 대부분의 내장 타입에 대해 잘 작동한다.
    # 다만 아래와 같이 순서가 정해져 있지 않은 경우는 정렬할 수 없다.
    # 클래스에 정수와 마찬가지로 자연스러운 순서가 존재하는 특별 메서드를 정의하면 별도의 인자없이 sort를 쓸 수 있다.
    # 그러나 보통 객체는 여러 가지 순서를 지원해야하는 경우가 더 많으므로 특별 메서드를 정의하는 건 큰 의미가 없다.
    # 정렬에 사용하고 싶은 애트리뷰트가 객체안에 내포된 경우는 그냥 key함수를 사용하면 된다.
    tools = [
        Tool('수준계', 3.5),
        Tool('해머', 1.25),
        Tool('스크류드라이버', 0.5),
        Tool('끌', 0.25),
    ]

    # key는 함수여야되기에 lambda로 정렬하고자하는 원소를 전달한다.
    print('미정렬:', repr(tools))
    tools.sort(key=lambda x: x.name)
    print('알파벳순 정렬: ', tools)

    tools.sort(key=lambda x: x.weight)
    print('무게순 정렬:', tools)

    # 문자열 같은 경우에는 정렬전 key함수를 사용해 원소값을 변형할 수 있다,
    places = ['home', 'work', 'New York', 'Paris']
    places.sort()
    print('대소문자 구분:', places)
    places.sort(key=lambda x: x.lower())
    print('대소문자 무시:', places)

    # 때로는 여러 기준을 사용해 정렬해야할 수 있는데, 아래의 같은 리스트를 weight로 정렬 후 name으로 정렬하고자 한다.
    power_tools = [
        Tool('드릴', 4),
        Tool('원형 톱', 5),
        Tool('착암기', 40),
        Tool('연마기', 4),
    ]

    # 가장 쉬운 건 tuple 타입을 쓰는 건데, 튜플은 기본적으로 비교가능하며 자연스러운 순서가 정해져있다.
    # 이는 sort에 필요한 __lt__ 정의가 들어있다는 뜻이다.
    saw = (5, '원형 톱')
    jackhammer = (40, '착암기')
    assert not (jackhammer < saw)  # 예상한 대로 결과가 나온다

    # 아래의 경우 첫번째 위치의 값이 서로 같으면 두번째 그리고 세번째 값을 비교한다.
    drill = (4, '드릴')
    sander = (4, '연마기')
    assert drill[0] == sander[0]  # 무게가 같다
    assert drill[1] < sander[1]  # 알파벳순으로 볼 때 더 작다
    assert drill < sander  # 그러므로 드릴이 더 먼저다

    # 이런 튜플의 동작 방식과 sort()를 응용하면 쉽게 weight로 정렬 후 name으로 정렬할 수 있다.
    power_tools.sort(key=lambda x: (x.weight, x.name))
    print('차례로 정렬', power_tools)

    # 이때 제약사항은 모든 정렬기준(오름차순, 내림차순)이 같아야된다는 거다.
    # 만약 sort 매서드에 reverse 파라미터를 넘기면 튜플에 들어있는 두 기준의 정렬 순서가 똑같이 영향을 받는다.
    # 다만 숫자값의 경우에는 -를 이용하여 정렬방향을 혼합할 수 있다.
    power_tools.sort(key=lambda x: (-x.weight, x.name))
    print('숫자 역순 문자 순정렬', power_tools)

    # sort는 key 함수 반환 값이 서로 같은 경우 원래 순서를 그대로 유지해준다.
    # 그러므로 서로 다른 기준이라면 sort를 여러번 호출해도 된다.
    # 위의 과정을 아래와 같이 동일하게 수행 가능하다.
    power_tools.sort(key=lambda x: x.name)  # name 기준 오름차순
    power_tools.sort(key=lambda x: x.weight,  # weight 기준 내림차순
                     reverse=True)
    print(power_tools)

    # 이를 응용하면 기존에 제한사항에 걸려 불가능했던 문자 역순 숫자 순정렬이 가능하디.
    power_tools.sort(key=lambda x: x.name, reverse=True)  # name 기준 내림차순
    power_tools.sort(key=lambda x: x.weight),  # weight 기준  오름차순
    print('문자 역순 숫자 순정렬', power_tools)


def asterisk_unpacking():
    # 만약 나머지 모든 값을 담으려면 슬라이스말고 언패킹을 사용해라.
    car_ages = [0, 9, 4, 8, 7, 20, 19, 1, 6, 15]
    car_ages_descending = sorted(car_ages, reverse=True)

    # 슬라이스를 사용한 할당. 시각적 잡음이 많고 1차이 인덱스로 인한 오류(off-by-one-error)가 발생하기 쉽다.
    oldest = car_ages_descending[0]
    second_oldest = car_ages_descending[1]
    others = car_ages_descending[2:]
    print(oldest, second_oldest, others)

    # 언패킹을 사용한 할당. *식으로 나머지를 할당한다.
    oldest, second_oldest, *others = car_ages_descending
    print(oldest, second_oldest, others)

    # 중간이나 첫번째 위치 등, 원하는 대로 언패킹이 가능하다.
    oldest, *others, youngest = car_ages_descending
    print(oldest, youngest, others)

    *others, second_youngest, youngest = car_ages_descending
    print(youngest, second_youngest, others)

    # 다만 별표 식이 포함된 언패킹을 사용하려면 필수인 부분이 최소 하나는 있어야 한다.
    # *others = car_ages_descending 이런 식은 에러가 발생한다.

    # 또한, 한 수준의 언패킹 패턴에 별표 식을 두개 이상 쓸 수도 없다.
    # first, *middle, *second_middle, last = [1, 2, 3, 4]

    # 별표 식은 항상 list 인스턴스가 되며 남는 원소가 없다면 빈 리스트가 된다.
    short_list = [1, 2]
    first, second, *rest = short_list
    print(first, second, rest)


def list_stride():
    # 스트라이드는 리스트[시작:끝:증가값]으로 일정한 간격으로 슬라이스 하는 것을 뜻함.
    x = [1, 2, 3, 4, 5, 6]
    odds = x[::2]
    evens = x[1::2]
    print(odds)
    print(evens)

    # 역수로 스트라이드 시 역으로 뒤집을 수 있다. 2개씩도 가능하다.
    y = x[::-1]
    print(y)
    y = x[::-2]
    print(y)

    # 문자열의 경우에도 작동한다.
    x = b'mongoose'
    y = x[::-1]
    print(y)

    x = '寿司'
    y = x[::-1]
    print(y)

    # 하지만 유니코드 데이터를 UTF-8로 인코딩한 문자열에선 작동하지 않는다.
    # 왜냐하면 UTF-8의 바이트 순서를 뒤집으면 2바이트 이상으로 이뤄졌던 문자들은 코드가 깨지기 때문에 이를 유니코드 문자로 디코딩 할 수 없다.
    # 단 모든 문자가 아스키 문자라면 문제가 없을 수 있다. UTF-8인코딩에서 아스키코드는 1바이트 값으로 인코딩되기 떄문이다.
    w = '寿司'
    x = w.encode('utf-8')
    y = x[::-1]
    # 오류가 나는 부분. 오류를 보고 싶으면 커멘트를 해제할것
    # z = y.decode('utf-8')

    # 다만 스트라이딩을 슬라이싱과 같이 사용하지는 말 것. 읽기에 혼란스럽다.
    # 필요한 경우에는 나누어서 사용하는 게 좋다.
    x = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    print(x[2::2])  # ['c', 'e', 'g']
    print(x[-2::-2])  # ['g', 'e', 'c', 'a']

    # 위 방법보단 이 방법이 더 낫다.
    y = x[::2]  # ['a', 'c', 'e', 'g']
    z = y[1:-1]  # ['c', 'e']

def list_slice():
    # 리스트를 슬라이싱 한 결과는 완전히 새로운 리스트이다. 참조는 유지되나 변경해도 원래 리스트가 변하진 않는다.
    # 리스트 대입 시에는 길이가 같을 필요가 없다.
    a = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

    # 주어진 슬라이스보다 작은 값이 대입되어서 총 길이가 줄어듬
    print('이전:', a)
    a[2:7] = [99, 22, 14]
    print('이후:', a)

    # 주어진 슬라이스보다 작은 값이 대입되어서 총 길이가 늘어남
    print('이전:', a)
    a[2:3] = [47, 11]
    print('이후:', a)

    # 슬라이싱에서 시작과 끝 인덱스를 모두 생략하면 원래 리스트를 복사한 새 리스트를 얻음
    b = a[:]
    assert b == a and b is not a

    # 단순히 대입해버리면 b를 a가 덮어써버림
    b = a
    print('이전 a:', a)
    print('이전 b:', b)
    a[:] = [101, 102, 103]
    assert a is b  # 여전히 같은 리스트 객체임
    print('이후 a:', a)  # 새로운 내용이 들어 있음
    print('이후 b:', b)  # 같은 리스트 객체이기 때문에 a와 내용이 같음


if __name__ == "__main__":
    for mtd in [
        list_slice,
        list_stride,
        asterisk_unpacking,
        sort_with_key,
        use_get_dict,
        use_defaultdict,
        use_missing
    ]:
        print('==================================================================')
        mtd()