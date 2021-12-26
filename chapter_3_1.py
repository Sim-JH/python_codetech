# functools.wrap을 사용해 함수 데코레이터를 정의하라.
def trace(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f'{func.__name__}({args!r}, {kwargs!r}) '
              f'-> {result!r}')
        return result
    return wrapper

@trace
def fibonacci(n):
    """Return n 번째 피보나치 수"""
    if n in (0, 1):
        return n
    return (fibonacci(n - 2) + fibonacci(n - 1))

fibonacci(4)

# 다만 이때 fibonacci 함수의 이름이 fibonacci가 아니게 된다.
# tarace 함수는 자신의 본문에 정의된 wrapper 함수를 반환하고 데코레이터로 인해 이 wrapper 함수가 모듈에 fibonacci라는 이름으로 등록된다.
# 이런 동작은 디버거와 같이 인스트로펙션(실행 시점에 프로그램이 어떻게 실행되는지 관찰하는 것)을 하는 도구에서 문제가 된다.
# 예를들어 help 함수(함수의 독스트링 호출)를 통해 호출해보면 "Return n 번째 피보나치 수"가 호출되지 않는다.
print(fibonacci)

# 데코레이터가 감싸고 있는 원래 함수의 위치를 찾을 수 없기 때문에 객체 직렬화도 깨진다.
#import pickle
#pickle.dumps(fibonacci)

# 문제를 해결하는 법은 wraps 도우미 함수를 사용하는 것이다. 이 함수는 데코레이터 작성을 돕는 데코레이터다.
from functools import wraps

def trace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f'{func.__name__}({args!r}, {kwargs!r}) '
              f'-> {result!r}')
        return result
    return wrapper


@trace
def fibonacci(n):
    """Return n 번째 피보나치 수"""
    if n in (0, 1):
        return n
    return (fibonacci(n - 2) + fibonacci(n - 1))

# @wraps 도우미 함수 덕에 데코레이터로 감싸진 함수에 대해서도 원하는 결과를 볼 수 있다.
help(fibonacci)

# 객체 직렬화도 제대로 작동한다.
import pickle
print(pickle.dumps(fibonacci))
# 이 외에도 더 많은 표준 애트리뷰트가(__name__, __module__ 등등)가 존재하는 데 wraps를 통해 이 모든 애트리뷰트를 복사해서 함수가 제대로 작동하도록 해준다.

#=======================================================================================================================

# 위치로만 인자를 지정하거나 키워드로만 지정하거나 함수 호출을 명확하게 하자.
# 인자목록의 '/' 기호는 위치로만 지정하는 인자의 끝을 표현한다.
def safe_division_e(numerator, denominator, /,
                    ndigits=10, *,
                    ignore_overflow=False,
                    ignore_zero_division=False):
    print(f'numerator: {numerator}, denominator: {denominator}, ndigits: {ndigits}')
    try:
        fraction = numerator / denominator
        return round(fraction, ndigits)
    except OverflowError:
        if ignore_overflow:
            return 0
        else:
            raise
    except ZeroDivisionError:
        if ignore_zero_division:
            return float('inf')
        else:
            raise

# 위 함수에서 ndigits는 위치나 키워드를 사용해 전달할 수 있는 선택적 파라미터이므로 어떤 방식으로든 함수 호출에 사용할 수 있다.
result = safe_division_e(22, 7)
print(result)

result = safe_division_e(22, 7, 5)
print(result)

result = safe_division_e(22, 7, ndigits=2)
print(result)

#=======================================================================================================================

def decode(data, default=None):
    import json
    # None과 독스트링을 사용해 동적인 디폴트 인자를 지정해라
    """ 문자열로부터 JSON 데이터를 읽어온다
    
    :param data: 디코딩할 JSON 데이터
    :param default: 디코딩 실패 시 반환할 값
    :return: default 
    """
    try:
        return json.loads(data)
    except ValueError:
        if default is None:
            default = {}
        return default

# 위 접근 방법은 타입 애너테이션을 사용해도 잘 작동한다.
from typing import Optional
from datetime import datetime

def log_typed(message: str,
              when: Optional[datetime]=None) -> None:
    """메시지와 타임스탬프를 로그에 남긴다.

    Args:
        message: 출력할 메시지.
        when: 메시지가 발생한 시각(datetime).
            디폴트 값은 현재 시간이다.
    """
    if when is None:
        when = datetime.now()
    print(f'{when}: {message}')


if __name__ == "__main__":
    pass
