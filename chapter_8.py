# ======================================================================================================================
# 정확도가 매우 중요한 경우에는 decimal을 사용하라
# ======================================================================================================================
# copyreg를 사용해 pickle을 더 신뢰성 있게 만들어라
# pickle 내장 모듈을 사용하면 파이썬 객체를 바이트 스트림으로 직렬화하거나 바이트 스트림을 파이썬 객체로 역 직렬화할 수 있다.
# pickle의 목적은 제어하는 프로그램들이 이진 채널을 통해 서로 파이썬 객체를 넘기는데 있다.

# 예를 들어 파이썬 객체를 사용해 게임 중인 플레이어의 진행 상태를 표현하고 싶다고 하자. 진행 상태에는 플레이어의 레벨과 남은 생명 개수가 들어있다.
class GameState:
    def __init__(self):
        self.level = 0
        self.lives = 4

# 프로그램은 게임이 실행됨에 따라 이 객체를 변경한다.
state = GameState()
state.level += 1
state.lives -= 1
print(state.__dict__)

# 사용자가 게임을 그만두면 나중에 이어서 진행할 수 있도록 프로그램이 게임 상태를 파일에 저장하며, pickle 모듈을 사용하면 상태를 쉽게 저장할 수 있다.
# 다음 코드는 dump 함수를 사용해 GameState 객체를 파일에 기록한다.
import pickle
state_path = 'game.state.bin'
with open(f'sample_data/{state_path}', 'wb') as f:
    pickle.dump(state, f)

# 나중에 이 파일에 대해 load 함수를 호출하면 직렬화한적이 전혀 없었던 것처럼 다시 GameState 객체를 돌려받을 수 있다.
with open(f'sample_data/{state_path}', 'rb') as f:
    state_after = pickle.load(f)
print(state_after.__dict__)

# 이런 접근 방법을 사용하면 시간이 지나면서 게임 기능이 확장될 때 문제가 발생한다. 플레이어가 최고점을 목표로 점수를 얻을 수 있게 게임을
# 변경한다고 생각해보자. 사용자의 점수를 추적하기 위해 GameState 클래스에 새로운 필드를 추가해야한다.
class GameState:
    def __init__(self):
        self.level = 0
        self.lives = 4
        self.points = 0

# 이 경우 저장은 이전과 똑같이 되더라도 예전 버전에서 저장한 GameState 객체를 사용해 게임을이어서 진행하고자 하면 어떻게 될까?
# 새로 추가한 points필드가 사라진 것을 확인할 수 있다.
state = GameState()
serialized = pickle.dumps(state)
state_after = pickle.loads(serialized)
print(state_after.__dict__)

with open(f'sample_data/{state_path}', 'rb') as f:
    state_after = pickle.load(f)

print(state_after.__dict__)

# assert isinstance(state_after, GameState)

# 이는 pickle이 객체 직렬화를 쉽게 하는 용도로만 만들어져있기 때문이다. 만약 pickle을 사용하는 방식이 아주 간단한 수준을 벗어나면
# pickle은 망가지기 시잔한다.
# copyreg 내장 모듈을 사용하면 이런 문제를 쉽게 해결할 수 있다. 파이썬 객체를 직렬화하고 역직렬화할 때 사용할 함수를 등록할 수 있으므로,
# pickle의 동작을 제어할 수 있고, 그에따라 pickle 동작의 신뢰성을 높일 수 있다.

# 디폴트 애트리뷰트 값
# 가장 간단한 경우, 디폴트 인자가 있는 생성자를 사용하면 GameState 객체를 언피클했을 떄도 항상 필요한 모든 애트리뷰트를 포함시킬 수 있다.
class GameState:
    def __init__(self, level=0, lives=4, points=0):
        self.level = level
        self.lives = lives
        self.points = points

# 이 생성자를 피클링에 사용하려면 GameState 객체를 받아서 copyreg 모듈이 사용할 수 있는 튜플 파라미터로 변환해주는 도우미 함수가 필요하다.
# 이 함수가 반환한 튜플 객체에는 언피클 시 사용할 함수와 언피클 시 이 함수에 전달해야 하는 파라미터 정보가 들어간다.
def pickle_game_state(game_state):
    kwargs = game_state.__dict__
    return unpickle_game_state, (kwargs,)

# 이제 unpickle_game_state 도우미 함수를 정의해야 한다. 이 함수는 직렬화한 데이터와 pickle_game_state가 돌려주는 튜플에 있는 파라미터
# 정보를 인자로 받아서 그에 대응하는 GameState 객체를 돌려준다.
def unpickle_game_state(kwargs):
    return GameState(**kwargs)

import copyreg

# 이제 pickle_game_state함수를 copyreg 내장 모듈에 등록한다.
copyreg.pickle(GameState, pickle_game_state)

# 함수를 등록한 다음에는 직렬화와 역직렬화가 예전처럼 잘 작동한다.
state = GameState()
state.points += 1000
serialized = pickle.dumps(state)
state_after = pickle.loads(serialized)
print(state_after.__dict__)

# 변경함수를 등록한 다음, 다시 GameState의 정의를 바꿔서 사용자가 마법 주문을 얼마나 사용했는지 알 수 있게한다. 이 변경은 GameState에
# points 필드를 추가하는 변경과 비슷하다.
class GameState:
    def __init__(self, level=0, lives=4, points=0, magic=5):
        self.level = level
        self.lives = lives
        self.points = points
        self.magic = magic   # 추가한 필드


# 하지만 앞에서 points를 추가했던 경우와 달리, 예전 버전의 GameState를 역직렬화해도 애트리뷰트가 없다는 오류가 발생하지 않고 데이터가 제대로 만들어진다.
# pickle 모듈의 디폴트 동작은 object에 속한 애트리뷰트만 저장한 후 역직렬화할 떄 복구하지만, unpickle_game_state는 GameState의 생서자를
# 직접 호출하므로 이런 경우에도 객체가 제대로 생성된다. GameState의 생성자 키워드 인자에는 파라미터가 들어오지 않을 경우 설정할 디폴트 값이 지정돼 있다.
# 따라서 예전 게임 상태 파일을 역직렬화하면 새로 추가한 magic 필드의 값은 디폴트 값으로 설정된다.
print('이전:', state.__dict__)
state_after = pickle.loads(serialized)
print('이후:', state_after.__dict__)

# 클래스 버전 지정
# 가끔은 파이썬 객체의 필드를 제거해 예전 버전 객체와의 하위 호환성이 없어지는 경우도 발생한다. 이런 식의 변경이 일어나면 디폴트 인자를
# 사용하는 접근방법을 사용할 수 있다.
# 예를들어 lives 인자를 없애보자.
class GameState:
    def __init__(self, level=0, points=0, magic=5):
        self.level = level
        self.points = points
        self.magic = magic

# 문제는 이렇게 변경한 뒤에는 예전 게임 데이터를 역직렬화할 수 없다는 점이다. unpickle_game_state 함수에 의해 이전 데이터의 모든 필드가
# GameState 생성자에게 전달되므로, 클래스에 제거된 필드도 생성자에게 전달된다.
#pickle.loads(serialized)


# copyrreg 함수에게 전달하는 함수에 버전 파라미터를 추가하면 문제를 해결할 수 있다. 새로운 GameState 객체를 피클링할 때는 직렬화한 데이터의 버전이 2로 설정된다ㅣ,
def pickle_game_state(game_state):
    kwargs = game_state.__dict__
    kwargs['version'] = 2
    return unpickle_game_state, (kwargs,)

# 이전 버전 데이터에는 version 인자가 들어있지 않다. 따라서 이에 맞춰 GamState 생성자에 전달할 인자를 적절히 변경할 수 있다.
def unpickle_game_state(kwargs):
    version = kwargs.pop('version', 1)
    if version == 1:
        del kwargs['lives']
    return GameState(**kwargs)

# 이제는 이전에 직렬화했던 객체도 제대로 역직렬화된다.
copyreg.pickle(GameState, pickle_game_state)
print('이전:', state.__dict__)
state_after = pickle.loads(serialized)
print('이후:', state_after.__dict__)


# 안정적인 임포트 경로
# pickle을 할 때 마주칠 수 있는 다른 문제점으로, 클래스 이름이 바뀌어 코드가 깨지는 경우를 들 수 있다. 이런 변경이 일어난 경우 pickle 모듈이 제대로 작동하지 않는다.
# 만약 위의 GameState 라는 이름을 아래와 같이 바꾸자고 가정해보자.
class BetterGameState:
    def __init__(self, level=0, points=0, magic=5):
        self.level = level
        self.points = points
        self.magic = magic

# 그렇다면 GameState 클래스를 찾을 수 없으므로 오류가 발생한다. 해당 오류가 발생하는 이유는 피클된 데이터 안에 직렬화한 클래스의 임포트
# 경로가 들어 있기 때문이다.
# pickle.loads(serialized)
#
print(serialized)

# copyreg를 쓰면 객체를 언피클할 때 사용할 함수에 대해 안정적인 식별자를 지정할 수 있다. 이로 인해 여러 다른 클래스에서 다른 이름으로
# 피클된 데이터를 역질렬화 할 때 서로 전환할 수 있다,
copyreg.pickle(BetterGameState, pickle_game_state)

# 확인해보면 BetterGameState 대신 unpickle_game_state에 대한 임포트 경로가 인코딩된다는 사실을 알 수 있다.
state = BetterGameState()
serialized = pickle.dumps(state)
print(serialized)
# ======================================================================================================================
# datetime 관련
# https://spoqa.github.io/2019/02/15/python-timezone.html 참조
# ======================================================================================================================
# 강건성과 성능
# try/except/else/finally의 각 블록을 잘 활용하라.
# 파일을 열 때 발생하는 오류는 finally 블록을 거치지말고 호출한 쪽에 전달되어야함으로 try 블록 앞에서 open을 호출하는 것이 옳다.

# 재사용 가능한 try/finally 동작을 원한다면 contextlib와 with문을 사용하라.
# 파이썬의 with 문은 코드가 특별한 컨텍스트 안에서 실행되는 경우를 표현한다. 예를 들어 상호 배제 락(뮤텍스)을 with 문 안에서 사용하면
# 락을 소유했을 때만 코드 블록이 실행된다는 것을 의미한다.
from threading import Lock
lock = Lock()
with lock:
    # 어떤 불변 조건을 유지하면서 작업을 수행한다.
    pass

# 위 with 문은 아래와 같은 효과가 있다.
lock.acquire()
try:
    # 어떤 불변 조건을 유지하면서 작업을 수행한다.
    pass
finally:
    lock.release()

# contextlib 내장 모듈을 사용하면 객체나 함수를 with 문에서 쉽게 쓸 수 있다.
# contextlib 모듈은 with 문에 쓸 수 있는 함수를 간단히 만들 수 있는 contextmanager 데코레이터를 제공한다.
# 이 데코레이터를 사용하는 방법이 __enter__와 __exit__ 특별 메서드를 사용해 새로 클래스를 정의하는 방법보다 훨씬 쉽다.
# 예를 들어 어떤 코드 영역에서 디버깅 관련 로그를 더 많이 남기고 싶다고 하자.
import logging


def s_log():
    logging.debug('디버깅 데이터')
    logging.error('이 부분은 오류 로그')
    logging.debug('추가 디버깅 데이터')

# 로그 수준의 디폴트 값은 WARNING이므로 실행시 error 메세지만 화면에 출력된다.
s_log()
# 컨텍스트 매니저를 정의하면 이 함수의 로그 수준을 일시적으로 높일 수 있다. 이 도우미 함수는 with 블록을 실행하기 직전에 로그 심각성
# 수준을 높이고, 블록을 실행한 직후에 심각성 수준을 이전 수준으로 회복시켜준다.
from contextlib import contextmanager


@contextmanager
def debug_logging(level):
    logger = logging.getLogger()
    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    try:
        # yield 식은 with 블록의 내용이 실행되는 부분을 지정한다.
        # with 블록 안에서 발생한 예외는 어떤 것이든 yield 식에 의해 다시 발생되기 때문에 이 예외를 도우미 함수(debug_logging) 안에서 잡아낼 수 있다.
        yield
    finally:
        logger.setLevel(old_level)

# 이제 같은 로그 함수를 호출하되, 이번에는 debug_logging 컨텍스트 안에서 실행하자. with 블록 안에서는 화면에 모든 로그 메시지가 출력된다.
# with 블록 밖에서 같은 함수를 실행하면 디버그 수준의 메세지는 출려되지 않는다.
with debug_logging(logging.DEBUG):
    print('*내부')
    s_log()
print('*외부:')
s_log()


# with와 대상 변수 함께 사용하기
# with 문에 전달된 컨텍스트 매니저가 객체를 반환할 수도 있다. 이렇게 반환된 객체는 with 복합문의 일부로 지정된 지역 변수에 대입된다.
# 이를 통해 with 블록 안에서 실행되는 코드가 직접 컨텍스트 객체와 상호작용할 수 있다.
# 예를 들어 파일을 작성하고 이파일이 제대로 닫혔는지 확인하고 싶다고 하자. with 문에 open을 전달하면 이렇게 할 수 있다.
# open은 with문에서 as를 통해 대상으로 지정된 변수에게 파을 핸들을 전달하고, with 블록에서 나갈 때 이 핸들을 닫는다.
with open('sample_data/test_context.txt', 'w') as handle:
    handle.write('데이터')
# 위 방식을 통해 매번 파일을 닫을 필요없이 자동으로 파일을 닫게 할 수 있다.
# as 대상 변수에게 값을 제공하도록 하기 위해 필요한 일은 컨텍스트 매니저 안에서 yield에 값을 넘기는 것 뿐이다.
# 예를 들어, 다음과 같이 Logger 인스턴스를 가져와서 로그 수준을 설정하고 yield로 대상을 전달하는 컨텍스트 매니저를 만들 수 있다.
@contextmanager
def log_level(level, name):
    logger = logging.getLogger(name)
    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    try:
        yield logger
    finally:
        logger.setLevel(old_level)

# with의 as 대상 번수로 얻은 객체에 대해 debug와 같은 로그 관련 메서드를 호출하면, with 블록 내의 로그 심각성 수준이 낮게 설정돼 있으므로
# 디버깅 메세지가 출력된다. 하지만 디폴트 로그 심각성 수준이 WARNING이기 떄문에 logging 모듈을 직접 사용해 debug 로그 메서드를 호출하면
# 아무 메세지도 출력되지 않는다.
with log_level(logging.DEBUG, 'my-log') as logger:
    logger.debug(f'대상: {logger.name}!')
    logging.debug('이 메시지는 출력되지 않습니다')

# with 문이 끝날 떄 로그 심각성 수준이 원래대로 복구되므로, with 문 밖에서 my-log라는 로그에 대해 debug를 통해 메세지를 출력해도
# 아무 메세지가 표시되지 않는다. 하지만 error로 출력한 로그는 항상 출력된다.
logger = logging.getLogger('my-log')
logger.debug('디버그 메시지는 출력되지 않습니다')
logger.error('오류 메시지는 출력됩니다')

# 나중에 with문을 바꾸기만 하면 로거 이름을 바꿀 수 있다. 이렇게 로거 이름을 바꾼 경우 with의 as 대상 변수가 가리키는 Logger가 다른
# 인스턴스를 가리키게 되지만 이에 맞춰 다른 코드를 변경할 필요는 없다,
with log_level(logging.DEBUG, 'other-log') as logger:
    logger.debug(f'대상: {logger.name}!')
    logging.debug('이 메시지는 출력되지 않습니다')

# 이런 식으로 상태를 격리할 수 있고, 컨텍스트를 만드는 부분과 컨텍스트 안에서 실행되는 코드를 서로 분리할 수 있다는 것이 with문의 또 다른 장점이다.



# ======================================================================================================================
