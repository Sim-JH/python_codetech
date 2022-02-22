# ======================================================================================================================
# bytes를 복사하지 않고 다루려면 memoryview와 bytearray를 사용하라.
# 파이썬이 CPU 위주의 계산 작업을 추가적인 노력없이 병렬화해줄 수 없지만, 스루풋이 높은 병렬 I/O를 다양한 방식으로 지원할 수는 ㅇ있다.
# 그럼에도 불구하고 이런 I/O 도구를 잘못 사용해서 파이썬 언어가 I/O 위주의 부하에 대해서도 너무 느리다는 결론으로 이어지기 쉽다.

# 예를 들어 TV나 영화를 모두 내려받지 않고도 시청할 수 있게 네트워크를 통해 스트리밍하는 미디어 서버를 만든다고 하자.
# 이런 시스템의 핵심 기능으로 플레이 중인 비디오를 플레이 시간상 앞이나 뒤로 이동해서 일부를 건너뛰거나 반복하는 기능이 있다.
# 클라이언트 프로그램에서 사용자가 선택한 시간에 대응하는 데이터 덩어리를 서버에 요청에 이 기능을 구현할 수 있다.
def timecode_to_index(video_id, timecode):
    return 1243
    # 비디오 데이터의 바이트 오프셋을 반환한다


def request_chunk(video_id, byte_offset, size):
    pass
    # video_id에 대한 비디오 데이터 중에 바이트 오프셋부터 size만큼을 반환한다


video_id = ...
timecode = '01:09:14:28'
byte_offset = timecode_to_index(video_id, timecode)
size = 20 * 1024 * 1024
video_data = request_chunk(video_id, byte_offset, size)

# request_chunk 요청을 받아서 요청에 해당하는 20MB의 데이터를 돌려주는 서버 측 핸들러를 어떻게 구현할 수 있을까?
# 이 예제의 경우 서버의 명령과 제어 부분은 이미 만들어져 있다고 자정하자.
# 여기서는 요청받은 데이터 덩어리를 메모리 캐시에 들어있는 수 기가바이트 크기의 비디오 정보에서 꺼낸 후 소켓을 통해 클라이언트에게 돌려주는
# 과정에 집중한다. 다음은 서버 핸들러를 구현한 코드를 보여준다.

# 책에는 없지만 실행을 시키기 위해 추가한 코드
# 소켓을 에뮬레이션
import os

class NullSocket:
    def __init__(self):
        self.handle = open(os.devnull, 'wb')

    def send(self, data):
        self.handle.write(data)

socket = NullSocket()
video_data = 100 * os.urandom(1024 * 1024)
byte_offset = 1234
size = 20 * 1024 * 1024 # 요정받은 데이터 크기
# 책에는 없지만 실행을 시키기 위해 추가한 코드 끝

# 이 코드의 지연 시간과 쓰루풋은 video_data에서 20MB의 비디오 덩어리를 가져오는 데 걸리는 시간과 이 데이터를 클라이언트에게 송신하는 데
# 걸리는 시간이라는 두 가지 요인에 의해 결정된다. 소켓이 무한히 빠르다고 가정하면, 이 코드의 지연시간과 스루풋은 데이터 덩어리를 가져와
# 만드는 데 걸리는 시간에 따라 결정된다. 따라서 최대 성능을 알아보려면 소켓 송신 부분은 무시하고 데이터 덩어리를 만들기 위해 bytes 인스턴스를
# 슬라이싱하는 방법에 걸리는 시간을 측정하면 된다.
chunk = video_data[byte_offset:byte_offset + size]
socket.send(chunk)

import timeit

video_data = 100 * os.urandom(1024 * 1024)
byte_offset = 1234

def run_test():
    chunk = video_data[byte_offset:byte_offset + size]
    # socket.send(chunk)를 호출해야 하지만 벤치마크를 위해 무시한다

result = timeit.timeit(
    stmt='run_test()',
    globals=globals(),
    number=100) / 100

print(f'{result:0.9f} 초')

# 클라이언트에게 보낼 20MB의 슬라이스를 꺼내는 데 대략 5밀리초가 걸린다. 이는 서버의 최대 전체 스루풋이 이론적으로 20MB/5밀리초 = 7.3GB/초
# 라는 뜻이다. 이보다 더 빨리 메모리에서 비디오 데이터를 꺼내올 순 없다. 이 서버에서 병렬로 새 데이터 덩어리를 요청할 수 있는 클라이언트의
# 최대 개수는 1 CPU-초 / 5밀리초 = 200이다. 이 개수는 asyncio 내장 모듈같은 도구가 지원할 수 있는 수만 건의 동시 접속에 비하면 아주 작다.
# 문제는 기반 데이터를 bytes 인스턴스로 슬라이싱하려면 메모리를 복사해야 하는데, 이 과정에 CPU 시간을 점유한다는 점이다.

# 이 코드를 더 잘 작성하는 방법은 파이썬이 제공하는 memoryview 내장 타입을 사용하는 것이다. memoryview는 CPython의 고성능 버퍼
# 프로토콜을 프로그램에 노출시켜준다. 버퍼 프로토콜은 파이썬 런타입과 C 확장이 bytes와 같은 객체를 통하지 않고 하부 데이터 버퍼에 접근할 수
# 있게 해주는 저수준 C API다. memoryview 인스턴스의 가장 좋은 점은 슬라이싱을 하면 데이터를 복사하지 않고 새로운 memoryview 인스턴스를 만들어준다는 것이다.
# 다음 코드는 bytes 인스턴스를 둘러싸는 memoryview를 만들고, 이 memoryview의 슬라이스를 사려ㅍ본다.

data = '동해물과 abc 백두산이 마르고 닳도록'.encode("utf8")
view = memoryview(data)
chunk = view[12:19]
print(chunk)
print('크기      :', chunk.nbytes)
print('뷰의 데이터:', chunk.tobytes())
print('내부 데이터:', chunk.obj)

# 복사가 없는 연산을 활성화함으로써 memoryview는 Numpy 같은 수치 계산 C 확장이나 이 예제 같은 I/O 위주 프로그램이 커다란 메모리를
# 바르게 처리해야하는 경우에 성능을 엄청나게 향상시킬 수 있다.
# 다음 코드는 앞의 예제에서 사용한 간단한 bytes 슬라이스를 memoryview로 바꿔서 마이크로 벤치마크를 수행한 결과다.
video_view = memoryview(video_data)

def run_test():
    chunk = video_view[byte_offset:byte_offset + size]
    # socket.send(chunk)를 호출해야 하지만 벤치마크를 위해 무시한다

result = timeit.timeit(
    stmt='run_test()',
    globals=globals(),
    number=100) / 100

print(f'{result:0.9f} 초')

# 결과는 250나노초다. 이는 164TB/초에 해당하는 수치다. 병렬 클라이언트의 경우 이론적으로 400만개까지 지원할 수 있다.


# 이제 데이터가 반대방향으로 흘러야 한다고 생각해보자. 일부 클라이언트가 여러 사용자에게 방송을 하기 위해 서버로 라이브 비디오 스트림을 보내야 한다.
# 그렇게 하려면 사용자가 가장 최근에 보낸 비디오 데이터를 캐시에 넣고 다른 클라이언트가 캐시에 있는 비디오 데이터를 읽게해야한다.
# 다음은 클라이언트가 서버로 1MB 데이터를 새로 보낸 경우를 구현한 코드다,

# 책에는 없지만 실행을 시키기 위해 추가한 코드
# 소켓을 에뮬레이션
class FakeSocket:

    def recv(self, size):
        return video_view[byte_offset:byte_offset+size]

    def recv_into(self, buffer):
        source_data = video_view[byte_offset:byte_offset+size]
        buffer[:] = source_data

socket = FakeSocket()
video_cache = video_data[:]
byte_offset = 1234
size = 1024 * 1024 # 데이터 덩어리 크기
# 책에는 없지만 실행을 시키기 위해 추가한 코드 끝

# socket.recv 메서드는 bytes 인스턴스를 반환한다. 간단한 슬라이스 연산과 bytes.join 메서드를 사용하면 현재 byte_offset에 있는
# 기존 캐시 데이터를 새로운 데이터로 스플라이스할 수 있다. 이런 연산의 성은을 확인하기 위해 또 다른 마이크로 벤치마크를 실행할 수 있다.
# 여기서는 가짜 소켓을 사용하기 때문에 이 성능 테스트는 I/O 상호작용을 테스트하지 않고 메모리 연산의 성능만 테스트한다,
chunk = socket.recv(size)
video_view = memoryview(video_cache)
before = video_view[:byte_offset]
after = video_view[byte_offset + size:]
new_cache = b''.join([before, chunk, after])

def run_test():
    chunk = socket.recv(size)
    before = video_view[:byte_offset]
    after = video_view[byte_offset + size:]
    new_cache = b''.join([before, chunk, after])

result = timeit.timeit(
    stmt='run_test()',
    globals=globals(),
    number=100) / 100

print(f'{result:0.9f} 초')

# 1MB 데이터를 받아서 비디오 캐시를 갱신하는데 33밀리초가 걸린다. 이는 수신 시 최대 스루풋이 1MB / 33밀리초 = 31MB 포이고, 비디오를
# 이런 식으로 스트리밍해 방송하는 클라이언트는 최대 31MB/1MB = 31 갤로 제한된다는 뜻이다.

# 이런 코드를 작성하는 더 나은 방법은 파이썬 내장 bytearray 타입과 memoryview를 같이 사용하는 것이다. bytes 인스턴스의 한 가지 단점은
# 읽기 전용이라 인덱스를 사용해 값을 변경할 수 없다는 것이다.
my_bytes = b'hello'
# 오류가 나는 부분. 오류를 보고 싶으면 커멘트를 해제할것
#my_bytes[0] = b'\x79'

# bytearray 타입은 bytes에서 원하는 위치에 있는 값을 바꿀 수 있는 가변버전과 같다.
# 인덱스를 사용해 bytearray의 내용을 바꿀 떄는 바이트 문자열이 아니라 정수를 대입한다.
my_array = bytearray('hello 안녕'.encode("utf8"))
my_array[0] = 0x79
print(my_array)

# bytearray도 memoryview를 사용해 감쌀 수 있다. memoryview를 슬라이싱해서 객체를 만들고, 이 객체에 데이터를 대입하면 하부의 bytearray
# 버퍼에 데이터가 대입된다. 이런 방법을 사용하면, 앞에서 bytes 인스턴스를 스플라이스해 클라이언트로부터 받은 데이터를 덧붙였던 것과 달리 데이터 복사에 드는 비용이 사라진다.
my_array = bytearray('row, row, row your 보트'.encode("utf8"))
my_view = memoryview(my_array)
write_view = my_view[3:13]
write_view[:] = b'-10 bytes-'
print(my_array)

# socket.recv_into나 RawIOBase.readinto와 같은 파이썬 라이브러리 메서드가 버퍼 프로토콜을 사용해 데이터를 빠르게 받아들이거나 읽을 수 있다.
# 이런 메서드를 사용하면 새로 메모리를 할당하고 데이터를 복사할 필요가 없어진다. 다음 코드는 스플라이스를 하지 않고 socket.recv_into와
# memoryview 슬라이스를 사용해 하부 bytearray에 데이터를 수신한다.
video_array = bytearray(video_cache)
write_view = memoryview(video_array)
chunk = write_view[byte_offset:byte_offset + size]
socket.recv_into(chunk)

def run_test():
    chunk = write_view[byte_offset:byte_offset + size]
    socket.recv_into(chunk)

result = timeit.timeit(
    stmt='run_test()',
    globals=globals(),
    number=100) / 100

print(f'{result:0.9f} seconds')

# 31GB/초, 최대 31000개의 클라이언트를 병렬로 처리할 수 있다.
# ======================================================================================================================
# 우선순위 큐로 heapq를 사용하는 방법을 알아두라.
# 파이썬이 제공하는 다른 큐 수현들의 제약 중에는 이들이 선입선출(FIFO)큐라는 점이 있다.
# 즉 이들은 원소를 받은 순서대로 정렬한다. 하지만 떄로는 프로그램에서 원소를 받은 순서가 아니라,
# 원소간의 상대적인 중요도에 따라 원소를 정렬해야하는 경우가 있다. 이런 목적에서는 우선순위 큐가 적합하다.
# 리스트 연산을 사용해 우선순위를 구현하면 큐 크기가 커짐에 따라 프로그램의 성능이 선형보다 더 빠르게 나빠진다.
# heapq 내장 모듈은 효율적으로 규모 확장이 가능한 우선수위 큐를 구현하는 데 필요한 모든 기능을 제공한다.
# heapq를 사용하려면 우선순위를 부여하려는 원소들이 자연스러운 순서를 가져야한다. 이는 원소를 표현하는 클래스에 __lt__와 같은 특별 메서드가 있어야한다는 뜻이다.
# functolls 내장 모듈이 제공하는 total_ordering 클래스 데코레이터를 사용하고, __lt__ 메서드를 구현하면 간단하게 정렬순서를 제공할 수 있다.
# ======================================================================================================================
