# ======================================================================================================================
# Queue를 사용해 스레드 사이의 작업을 조율하라

# 파이썬에서 동시성 작업을 처리할 때 가장 유용한 방식은 함수 파이프라인이다.
# 파이프라인에는 순차적으로 실행해야하는 여러 단계가 있고, 각 단계마다 실행할 구체적인 함수가 정해진다. 이런 접근 방법은 작업처리에
# 블로킹 I/O나 하위 프로세스가 포함되는 경우에 특히 좋다. 파이썬에서는 블로킹 I/O나 하위 프로세스를 더 쉽게 병렬화할 수 있기 때문이다.

# 예를 들어, 디지털 카메라에서 이미지 스트림을 계속 가져와 이미지 크기를 변경하고 온라인 포토 갤러리에 저장하고 싶다고 하자.
# 3단계 파이프라인으로 나눠 프로그램을 구성할 수 있다. 첫 단계에서 새 이미지를 얻고, 얻은 이미지는 두 번째 단계의 크기 변환 함수로
# 보내 처리한다. 크기가 조정된 이미지를 마지막 단계의 업로드 함수에 전달해 처리한다.
def download(item):
    return item


def resize(item):
    return item


def upload(item):
    return item


from collections import deque
from threading import Lock

# 가장 먼저 필요한 기능은 파이프라인의 단계마다 작업을 전달할 방법이다. 스레드 안전한 생산자-소비자를 이용해 이를 모델링 할 수 있다.
class MyQueue:
    def __init__(self):
        self.items = deque()
        self.lock = Lock()

    # 디지털 카메라는 deque 끝에 새로운 이미지를 추가한다
    def put(self, item):
        with self.lock:
            self.items.append(item)

    # 소비자는 duque 앞에서 이미지를 제거한다.
    def get(self):
        with self.lock:
            return self.items.popleft()

# 위와 같이 비슷한 큐에서 가져온 작업에 함수를 적용하고, 그 결과를 다른 큐에 넣는 스레드를 통해 파이프라인의 각 단계를 구현한다.
# 그리고 각 작업자가 얼마나 많이 새로운 입력을 검사(폴링)했고 얼마나 많이 작업을 완료했는지 추적한다.
class Worker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.polled_count = 0
        self.work_done = 0

    # 입력 큐가 비어있는 경우를 작업자 스레드가 제대로 처리하도록.
    # 입력 큐가 비어있다는 건 이전 단계가 아직 작업을 완료하지 못했다는 뜻이고, IndexError에서 에러를 잡아냄.
    def run(self):
        while True:
            self.polled_count += 1
            try:
                item = self.in_queue.get()
            except IndexError:
                time.sleep(0.01) # 할 일이 없음
            else:
                result = self.func(item)
                self.out_queue.put(result)
                self.work_done += 1

def use_queue():
    # 각 단계별로 큐를 생성하고 각 단계에 맞는 작업 스레드를 만들어서 서로 연결
    download_queue = MyQueue()
    resize_queue = MyQueue()
    upload_queue = MyQueue()

    done_queue = MyQueue()
    threads = [
        Worker(download, download_queue, resize_queue),
        Worker(resize, resize_queue, upload_queue),
        Worker(upload, upload_queue, done_queue),
    ]

    # 각 단게를 처리하기 위해 세 가지 스레드를 시작하고, 파이프라인의 첫 번째 단계에 원하는 만큼 작업을 넣는다.
    for thread in threads:
        thread.start()

    for _ in range(1000):
        download_queue.put(object())

    # done_queue를 지켜보며 파이프라인이 모든 원소를 처리할 때까지 대기
    while len(done_queue.items) < 1000:
        # 기다리는 동안 유용한 작업을 수행한다
        pass

    processed = len(done_queue.items)
    polled = sum(t.polled_count for t in threads)
    print(f'{processed} 개의 아이템을 처리했습니다, '
          f'이때 폴링을 {polled} 번 했습니다.')

    # 작업이 끝나도 무한대기함. 프로그램을 강제종료시킬것

    # 이 코드는 제대로 작동하지만, 스레드들이 새로운 작업을 기다리면서 큐를 폴링하기 때문에 부작용이 있다. run 메서드 안의 까다로운 부분인
    # IndexError 예외를 잡아내는 부분이 상당히 많이 실행된다. 작업자 함수의 속도가 달라지면 앞에 있는 단계가 그보다 더 뒤에 있는 단계의
    # 작업을 받지 못하는 기아 상태(starvation)가 돼서 처리할 작업이 없으므로, 루프를 빠르게 돌며 새로운 작업이 들어왔는지 자신의 입력 큐를
    # 계속 계산한다. 이로 인해 작업자가 스레드를 유용하지 않은 일(지속적으로 IndexError 예외를 잡아냄)을 하느라 CPU 시간을 잡아먹게 된다.
    # 그 외에도 3가지 문제가 있는데, 첫째 모든 작업이 다 끝났는지 검사하기 위해 추가로 done_queue에 대해 바쁜 대기를 수행해야한다.
    # 둘째 작업자 스레드에게 루푸를 중단할 시점을 알려줄 방법이 없어 Worker의 run 메서드가 무한히 반복한다.
    # 셋째 최악인 점은 파이프라인의 진행이 막히면 프로그램이 임의로 중단될 수도 있다.
    # 여기서 얻을 수 있는 교훈은 파이프라인이 나쁜다는 것이 아니라, 제대로 작동하는 생산자-소비자 큐를 직접 구현하기 어렵다는 것이다.
    # 따라서 굳이 직접 할 필요가 없다.

# 대안 Queue
# queue 내장 모듈에 있는 Queue 클래스는 위에서 말한 모든 문제를 해결할 수 있다. Queue는 새로운 데이터가 나타날 때까지 get 메서드가
# 블록되게 만들어서 작업자의 바쁜 대기 문제를 해결한다. 예를 들어 다음 코드는 큐에 입력 데이터가 들어오기를 기다리는 스레드를 하나 시작한다.
from queue import Queue
from threading import Thread

my_queue = Queue()

def consumer():
    print('소비자 대기')
    my_queue.get()  # 다음에 보여줄 put()이 실행된 다음에 시행된다
    print('소비자 완료')

def use_Queue_1():
    # 이 스레드가 먼저 실행되지만 Queue 인스턴스에 원소가 put돼서 get 메서드가 반환할 원소가 생기기 전까지 이 스레드는 끝나지 않는다.
    thread = Thread(target=consumer)
    thread.start()

    print('생산자 데이터 추가')
    my_queue.put(object())     # 앞에서 본 get()이 실행되기 전에 실행된다.
    print('생산자 완료')
    thread.join()

# 파이프라인 중간이 막하는 경우를 해결하기 위해 Queue 클래스에서는 두 단계 사이에 허용할 수 있는 미완성 작업의 최대 개수를 지정할 수 있다.
# 이렇게 버퍼 크기를 정하면 큐가 이미 가득 찬 경우 put이 블록된다. 예를 들어 다음 코드는 큐 원소가 소비될 때까지 대기하는 스레드를 정의한다.
my_queue = Queue(1)  # 버퍼 크기 1

def consumer():
    time.sleep(0.1)  # 대기
    my_queue.get()  # 두 번째로 실행됨
    print('소비자 1')
    my_queue.get()  # 네 번째로 실행됨
    print('소비자 2')
    print('소비자 완료')

def use_Queue_2():
    thread = Thread(target=consumer)
    thread.start()

    # 큐에 원소가 없을 경우 소비자 스레드가 대기하므로, 생산자 스레드는 소비자 스레드가 get을 호출했는지 여부와 관계없이 put을 두 번
    # 호출해 객체를 큐에 추가할 수 있다. 하지만 이 코드에서 Queue의 크기는 1이다. 이는 생산자가 두번째 호출한 put이 큐에 두 번째
    # 원소를 넣으려면 소비자가 최소 한 번이라도 get을 호출할 때까지 기다려야 한다는 뜻이다.
    my_queue.put(object()) # 첫 번째로 실행됨
    print('생산자 1')
    my_queue.put(object()) # 세 번째로 실행됨
    print('생산자 2')
    print('생산자 완료')
    thread.join()


in_queue = Queue()

# Queue 클래스의 task_done 메서드를 통해 작업의 진행을 추적할 수 있다. 이 메서드를 사용하면 어떤 단계의 입력 큐가 다 소진될 때까지
# 기다릴 수 있고, 파이프라인의 마지막 단계를 폴링할 필요도 없어진다.
# 다음 코드는 소비자 스레드가 자신의 작업을 하나 완료한 다음에 task_done을 호출하게 만든다.
def consumer():
    print('소비자 대기')
    work = in_queue.get()  # 두 번째로 실행됨
    print('소비자 작업중')
    # Doing work
    print('소비자 완료')
    in_queue.task_done()  # 세 번째로 실행됨

# 이제 생산자 코드가 소비자 스레드를 조인하거나 폴링할 필요가 없다. 생산자는 Queue 인스턴스의 join 메서드를 호출함으로써 in_queue가
# 끝나기를 기다릴 수 있다. in_queue가 비어 있더라도 지금까지 이 큐에 들어간 모든 원소에 대해 task_done이 호출되기 전까지는 join이 끝나지 않는다.
def use_Queue_3():
    thread = Thread(target=consumer)
    thread.start()

    print('생산자 데이터 추가')
    in_queue.put(object())    # 첫 번째로 실행됨
    print('생산자 대기')
    in_queue.join()           # 네 번째로 실행됨
    print('생산자 완료')
    thread.join()

# 이 모든 동작을 Queue 하위 클래스에 넣고, 처리가 끝났음을 작업자 스레드에게 알리는 기능을 추가할 수 있다.
# 다음 코드는 큐에 더 이상 다른 입력이 없을을 표시하는 특별한 센티널 원소를 추가하는 close 메서드를 정의한다.
class ClosableQueue(Queue):
    SENTINEL = object()

    def close(self):
        self.put(self.SENTINEL)

    # 그 후 큐를 이터레이션 하다가 이 특별한 object를 찾으면 이터레이션을 끝낸다. 그리고 이 __iter__ 메서드는 큐의 작업 진행을 감시할 수 있게
    # 하고자 task_done을 적당한 횟수만큼 호출해준다.
    def __iter__(self):
        while True:
            item = self.get()
            try:
                if item is self.SENTINEL:
                    return   # 스레드를 종료시킨다
                yield item
            finally:
                self.task_done()


# 이제 작업자가 ClosableQueue 클래스의 동작을 활용하게 할 수 있다. 이 스레드는 for 루프가 끝나면 종료된다.
class StoppableWorker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        for item in self.in_queue:
            result = self.func(item)
            self.out_queue.put(result)

# 이렇게 정의한 새 작업자 클래스를 사용해 작업자 스레드를 새로 정의한다.
def use_Queue_4():
    download_queue = ClosableQueue()
    resize_queue = ClosableQueue()
    upload_queue = ClosableQueue()
    done_queue = ClosableQueue()
    threads = [
        StoppableWorker(download, download_queue, resize_queue),
        StoppableWorker(resize, resize_queue, upload_queue),
        StoppableWorker(upload, upload_queue, done_queue),
    ]
    
    # 이전과 마찬가지로 작업자 스레드를 실행하고 첫 번째 단계의 입력 큐에 모든 입력 작업을 추가한 다음, 입력이 모두 끝났음을 표시하는 신호를 추가한다.
    for thread in threads:
        thread.start()

    for _ in range(1000):
        download_queue.put(object())

    download_queue.close()

    # 마지막으로 각 단계를 연결하는 큐를 join함으로써 작업 완료를 기다린다. 각 단계가 끝날때마다 다음 단계의 입력 큐의 close를 호출해서
    # 작업이 더 이상 없을을 통지한다. 마지막 done_queue에는 예상대로 모든 출력들이 들어있다.
    download_queue.join()
    resize_queue.close()
    resize_queue.join()
    upload_queue.close()
    upload_queue.join()
    print(done_queue.qsize(), '개의 원소가 처리됨')

    for thread in threads:
        thread.join()

# 위 접근 방법을 확장해 단계마다 여러 작업자를 사용할 수 있다. 그러면 I/O 병렬성을 높일 수 있으므로 이런 유형에 속한 프로그램의 속도를
# 상당히 증가시킬 수 있다. 이를 위해 먼저 다중 스레드를 시작하고 끝내는 도우미 함수를 만든다. stop_threads 함수는 소비자 스레드의
# 입력 큐마다 close를 호출하는 방식으로 작동한다. 이렇게 하면 모든 작업자를 깔끔하게 종료시킬 수 있다.
def start_threads(count, *args):
    threads = [StoppableWorker(*args) for _ in range(count)]
    for thread in threads:
        thread.start()
    return threads


def stop_threads(closable_queue, threads):
    for _ in threads:
        closable_queue.close()

    closable_queue.join()

    for thread in threads:
        thread.join()

def use_Queue_5():
    # 이제 앞에서 본 예제처럼 각 조각을 서로 연결해 파이프라인에 객체를 넣고, 그 과정에서 큐와 스레드의 완료를 join을 통해 기다리고, 최종 결과를 소비할 수 있다.
    download_queue = ClosableQueue()
    resize_queue = ClosableQueue()
    upload_queue = ClosableQueue()
    done_queue = ClosableQueue()
    download_threads = start_threads(
        3, download, download_queue, resize_queue)
    resize_threads = start_threads(
        4, resize, resize_queue, upload_queue)
    upload_threads = start_threads(
        5, upload, upload_queue, done_queue)
    
    for _ in range(1000):
        download_queue.put(object())
    
    stop_threads(download_queue, download_threads)
    stop_threads(resize_queue, resize_threads)
    stop_threads(upload_queue, upload_threads)
    
    print(done_queue.qsize(), '개의 원소가 처리됨')

# 선형적인 파이프라인의 경우 Queue가 잘 작동하지만, 다른 도구가 더 나은 상황도 많다.
# ======================================================================================================================
# 스레드에서 데이터 경합을 피하기 위해 LOCK을 사용하라
# 초보 파이썬 프로그래머는 전역 인터프리터 락(GIL)을 배운 뒤 코드에서 더 이상 상호 배제 락(뮤텍스)을 사용하지 않아도 되는 것으로 생각하곤 한다.
# GIL이 다중 CPU에서 파이썬 스레드들이 병렬적으로 실행될 수 없게 막는다면, 파이썬 스레드들이 프로그램의 데이터 구조에 동시에 접근할 수 없게
# 막는 락 역할도 해줘야하지 않을까?

# 하지만 조심하라. GIL이 동시 접근을 보장해주는 락 역할을 하는 것처럼 보여도 실제로는 전혀 그렇지 않다. 파이썬 스레드는 한 번에
# 단 하나만 실행될 수 있지만, 파이썬 인터프리터에서 어떤 스레드가 데이터 구조에 대해 수행하는 연산은 연속한 두 바이트코드 사이에서
# 언제든지 인터럽트될 수 있다. 여러 스레드가 같은 데이터 구조에 동시에 접근하면 위험하다. 이런 인터럽트로 인해 실질적으로는 언제든지
# 데이터 구조에 대한 불변 조건이 위반될 수 있고, 그에 따라 프로그램의 상태가 오염될 수 있다.

# 예를 들어 병렬적으로 여러 가지의 개수를 세는 프로그램을 작성한다고 하자. 센서 네트워크에서 광센서를 통해 빛이 들어온 경우를 샘플링하는
# 예를 생각할 수 있다. 시간이 지나면서 빛이 들어온 횟수를 모두 세고 싶다면 새로운 클래스를 사용해 셀 수 있다.
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self, offset):
        self.count += offset

# 센서를 읽을 떄는 블로킹 I/O를 수행하므로 센서마다 작업자 스레드를 할당한다고 하자. 각 작업자 스레드는 센서 값을 측정한 다음에 카운터를 증가시킬 수 있다.
def worker(sensor_index, how_many, counter):
    for _ in range(how_many):
        # 센서를 읽는다
        counter.increment(1)

from threading import Thread

# 다음 코드는 병렬로 센서마다 하나씩 worker 스레드를 실행하고, 모든 스레가 값을 다 읽을때까지 기다린다.
def caution_thread_1():
    how_many = 10**5
    counter = Counter()

    threads = []
    for i in range(5):
        thread = Thread(target=worker,
                        args=(i, how_many, counter))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    expected = how_many * 5
    found = counter.count
    print(f'카운터 값은 {expected}여야 하는데, 실제로는 {found} 입니다')

# 이 코드는 단순해 보이고, 따라서 결과도 뻔할 것 같다. 하지만 실제 실행한 결과는 예상과 전혀다르다. 왜 그럴까?
# 파이썬 인터프리터는 실행되는 모든 스레드를 강제로 공평하게 취급해서 각 스레드의 실행시간을 거의 비슷하게 만든다.
# 이를 위해 파이썬은 실행 중인 스레드를 일시 중단시키고 다른 스레드를 실행시키는 일을 반복한다. 문제는 파이썬이 스레드를 언제 일시 중단
# 시킬지 알 수 없다는 점이다. 심지어 원자적(atomic)인 것처럼 보이는 연산을 수행하는 도중에도 파이썬이 스레드를 일시 중단시킬 수 있다.
# 이로 인해 위와같은 결과가 생긴다.

# Counter 객체의 increment 메서드는 간단해 보인다. 작업자 스레드 입장에서 보면 다음 문장과 같다.

# counter.count += 1

# 하지만 객체 애트리뷰트에 대한 += 연산자는 실제로는 세 가지 연산으로 이뤄진다. 방금 본 문장은 다음과 같다.
# value = getattr(counter, 'count')
# result = value + 1
# setattr(counter, 'count', result)

# 카운터를 증가시키는 파이썬 스레드는 세 연산 사이에서 일시 중단될 수 있다. 이런 일시중단으로 인해 스레드 간 연산 순서가 뒤섞이면서
# value의 이전 값을 카운터에 대입하는 일이 생길 수 있다. 다음은 두 스레드 A와B 사이에서 이런 나쁜 상호작용이 일어난 경우다.

# 스레드# A에서 실행
# value_a = getattr(counter, 'count')
# 스레드# B로 컨텍스트 전환
# value_b = getattr(counter, 'count')
# result_b = value_b + 1
# setattr(counter, '‘'count'', result_b)
# 다시 스레드 A로 컨텍스트 전환
# result_a = value_a + 1
# setattr(counter, 'count', result_a}

# 스레드 A가 완전히 끝나기 전에 인터럽트가 일어나서 스레드 B가 실행된다. 스레드 A의 실행이 끝나고 다시 스레드가 중간부터 실행을 재개한다.
# 이로 인해 스레드 B가 카운터를 증가시켰던 결과가 모두 사라진다. 앞에서 본 광센서 예제에서 벌어진 일이다.

# 이와 같은 데이터 경합이나 다른 유형의 데이터 구조 오염을 해결하기 위해 파이썬은 threading 내장 모듈 안에 여러가지 튼튼한 도구를 제공한다.
# 가장 간단하지만 유용한 도구로 Lock 클래스가 있다. Lock 클래스는 상호 배제 락(뮤텍스)이다.
# 락을 사용하면 Counter 클래스가 여러 스레드의 동시 접근으로부터 자신의 현재 값을 보호할 수 있다. 한 번에 단 하나의 스레드만 락을 획들 할 수 있다.
# 다음 코드는 with 문을 사용해 락을 획득하고 해제한다. with 문을 사용하면 락을 획득한 상태에서 수행해야하는 코드를 쉽게 알아볼 수 있다.
from threading import Thread
import select
import socket

from threading import Lock

class LockingCounter:
    def __init__(self):
        self.lock = Lock()
        self.count = 0

    def increment(self, offset):
        with self.lock:
            self.count += offset

def worker(how_many, counter):
    for _ in range(how_many):
        # 센서를 읽는다
        counter.increment(1)

from threading import Thread

def caution_thread_2():
    how_many = 10**5
    counter = LockingCounter()

    threads = []
    for i in range(5):
        thread = Thread(target=worker,
                        args=(i, how_many, counter))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    expected = how_many * 5
    found = counter.count
    print(f'카운터 값은 {expected}여야 하는데, 실제로는 {found} 입니다')
# 이제는 예상과 결과가 들어맞는 걸 볼 수 있다.

# ======================================================================================================================
# 블로킹 I/O의 경우 스레드를 사용하고 병렬성을 피해라
# 파이썬 표준 구현을 CPython이라고 한다. CPython은 두 단계를 거쳐 파이썬 프로그램을 실행한다.
# 첫 번째 단계는 소스 코드를 구문 분석해서 바이트코드 (3.6부터는 16비트 워드 코드)로 변환한다.
# 두 번째 단계는 바이트코드를 스택 기반 인터프린터를 통해 실행한다. 바이트코드 인터프린터에는 파이썬 프로그램이 실행되는 동안 일관성 있게
# 유지해야하는 상태가 존재한다. CPython은 전역 인터프린터 락(GIL)이라는 방법을 사용해 일관성을 강제로 유지한다.

# GIL은 근본적으로 상호 배제 락(뮤텍스 mutex)이며, CPython이 선점형(preemptive) 멀티스레드로 인해 영향을 받는 것을 방지한다.
# 선점형 멀티스레드에서는 한 스레드가 다른 스레드의 실행을 중간에 인터럽트시키고 제어를 가져올 수 있다. 이런 인터럽트가 예기치 못한 때
# 발생하면 인터프리터의 상태가 오염될 수 있다. GIL은 CPython 자체와 CPython이 사용하는 C 확장 모듈이 실행되면서 인터럽트가 함부로
# 발생하는 것을 방지해, 인터프리터 상태가 제대로 유지되고 바이트코드 명령들이 제대로 실행되도록 만든다.

# GIL에는 꼭 알아둬야하는 큰 부작용이 있다. C++나 자바로 작성된 프로그램에서 실행 스레드가 여럿 있다는 말은 프로그램이 여러 CPU 코어를
# 동시에 활용할 수 있다는 뜻이다. 파이썬도 다중 실행 스레드를 지원하지만, GIL로 인해 여러 스레드 중 어느 하나만 앞으로 진행할 수 있다.
# 따라 파이썬 프로그램의 속도를 높이고 병렬처리를 수행하고 스레드를 사용할 수 없다.

# CPython에서도 다중 코어를 활용할 수 있는 방법이 있지만 이 방법은 표준 Thread 클래스를 사용하지 않으며, 코딩하는데 상당한 노력이 필요하다.
# 이런 한계에도 불구하고 파이썬이 스레드를 지원하는 이유는 무엇일까? 두 가지 타당한 이유가 있다.

# 첫째, 다중 스레드를 사용하면 프로그램이 동시에 여러 일을 하는 것처럼 보이게 만들기 쉽다. 동시성 작업의 동작을 잘 조화시키는 코드를 직접 사용하긴 어렵다.
# 스레드를 사용하면 작성한 함수를 파이썬으로 동시에 실행시킬 수 있다. GIL로 인해 스레드 중 하나만 진행할 수 있음에도 불구하고, CPython이
# 어느 정도 균일하게 각 스레드를 실행시켜주므로 다중 스레드를 통해 여러 함수를 동시에 실행 가능하다.

# 둘째, 블로킹 I/O를 다루기 위해서다. 블로킹 I/O는 파이썬이 특정 시스템 콜을 사용할 때 일어난다. 파이썬 프로그램은 시스템 콜을 사용해 OS가
# 자기 대신 외부 환경과 상호작용하도록 의뢰한다. 파일 쓰기나 읽기, 네트워크와 상호작용하기, 디스플레이 장치와 통신하기 등의 작업이 블로킹 I/O에 속한다.
# 스레드를 사용하면 운영체제가 시스템 콜 요청에 응답하는 데 걸리는 시간 동안 파이썬 프로그램이 다른 일을 할 수 있다.

# 예를들어 시리얼 포트를 통해 원격 제어 헬리콥터에 신호를 보내고 싶다고 하자. 이 동작을 대신해 느린 시스템 콜을 사용할 것이다. 이 함수는
# 운영체제에게 0.1초 동안 블록한 다음에 제어를 돌려달라고 요청하는데, 동기적으로 직렬 포트를 사용할 때 벌어지는 상황과 비슷하다.
import select
import socket
import time


def slow_systemcall():
    select.select([socket.socket()], [], [], 0.1)


def use_thread_1():
    start = time.time()

    for _ in range(5):
        slow_systemcall()

    end = time.time()
    delta = end - start
    print(f'총 {delta:.3f} 초 걸림')

# 문제는 slow_systemcall 함수가 실행되는 동안 프로그램이 아무런 진전을 이룰 수 없다는 것이다. 이 프로그램의 주 실행 스레드는 select
# 시스템 콜에 의해 블록된다. 실전에서 이런 상황이 벌어진다는 끔찍할 것이다. 헬리콥터에 신호를 보내는 동안 헬리콥터가 다음에 어디로 이동할지 계산할 수 있어야한다,
# 블로킹 I/O와 계산을 동시에 수행해야 한다면 시스템 콜을 스레드로 옮기는 것을 고려해봐야 한다.

# 다음 코드에서는 slow_systemcall 함수를 여러 스레드에서 따로따로 호출한다. 이렇게 하면 여러 직렬포트와 통신하면서 주 스레드는 필요한 계산을 수행할 수 있다.
import select
import socket
import time
from threading import Thread


def compute_helicopter_location(index):
    pass


def use_thread_2():
    start = time.time()

    threads = []
    for _ in range(5):
        thread = Thread(target=slow_systemcall)
        thread.start()
        threads.append(thread)

    for i in range(5):
        compute_helicopter_location(i)

    # 스레드를 시작한 후, 시스템 콜 스레드가 끝나기 전에 헬리콤터의 다음 움직임을 계산한다.
    for thread in threads:
        thread.join()

    end = time.time()
    delta = end - start
    print(f'총 {delta:.3f} 초 걸림')

# 병렬화한 버전은 순차적으로 실행한 경우보다 시간이 1/5로 줄어든다. 이는 GIL로 인해 생기는 한계가 있더라도, 파이썬이 여러 스레드를 통해
# 시스템 콜을 병렬로 실행할 수 있음을 보여준다. GIL은 파이썬 프로그램이 병렬로 실행되지 못하게 막지만, 시스템 콜에는 영향을 끼칠 수 없다.
# 이런 코드가 동작하는 이유는 파이썬 스레드가 시스템 콜을 하기 전에 GIL을 해제하고 시스템 콜에서 반환되자마자 GIL을 획득하기 때문이다.
# ======================================================================================================================
# 동시성과 병렬성
# 동시성은 컴퓨터가 같은 시간에 여러 다른 작업을 처리하는 것처럼 보이는 것을 뜻한다. (단일 CPU)
# 병렬성은 컴퓨터가 같은 시간에 실제로 여러 다른 작업을 처리하는 것을 뜻한다. (다중 CPU)

# 파이썬을 사용하면 다양한 스타일로 동시성 프로그램을 작성할 수 있다.
# 스레드는 상대적으로 적은 양의 동시성을 제공하지만, 코루틴은 수많은 동시성 함수를 사용할 수 있게 해준다.
# 파이썬은 시스템 콜, 하위 프로세스 (subprocess), C 확장을 사용해 작업을 병렬로 수행할 수 있다.
# 하지만 동시성 파이썬 코드가 실제 병렬적으로 실행되게 만드는 것은 매우 어렵다.


# 자식 프로세스를 관리하기 위해 subprocess를 사용하라.
# 파이썬이 시작한 자식 프로세스는 서로 병렬적으로 실행되기에 파이썬이 컴퓨터의 모든 CPU 코어를 사용할 수 있고, 그에 따라 프로그램의
# 쓰루풋을 최대로 높일 수 있다. 파이썬 자체는한 CPU에 묶여있지만 파이썬을 사용해 CPU를 많이 사용하는 작업을 조작하며 서로 협력하게 조정하기는 쉽다.
# 파이썬이 파위 프로세스를 실행하는 방법은 많은데 (popen, exec 등), 자식 프로세스를 관리할때는 subprocess 내장 모듈을 사용하는 것이 가장 쉽다.

import subprocess
import time
import os
def use_subprocess():
    result = subprocess.run(['echo', '자식프로세스가 보내는 인사!'], capture_output=True, encoding='utf-8')

    result.check_returncode() # 예외가 발생하지 않으면 문제 없이 잘 종료한 것이다
    print(result.stdout)

# 파이썬에서 subprocess 등의 모듈을 통해 실행한 자식 프로세스는 부모 프로세스인 파이썬 인터프린터와 독립적으로 실행된다.
# run 함수대신 Popen 클래스를 사용해 하위 프로세르를 만들면, 파이썬이 다른 일을 하면서 주기적으로 자식 프로세스의 상태를 검사할 수 있다.
    proc = subprocess.Popen(['sleep', '1'])
    while proc.poll() is None:
        print('작업중...')
        # 시간이 걸리는 작업을 여기서 수행한다

    print('종료 상태', proc.poll())

# 자식 프로세스와 부모를 분리하면 부모 프로세스가 원하는 만큼 자식 프로세스를 병렬로 실행할 수 있다.
# 다음 코드는 Popen을 사용해 자식 프로세스를 한꺼번에 시작한다.
    start = time.time()
    sleep_procs = []
    for _ in range(10):
        proc = subprocess.Popen(['sleep', '1'])
        sleep_procs.append(proc)

    for proc in sleep_procs:
        proc.communicate()

    end = time.time()
    delta = end - start
    print(f'{delta:.3} 초만에 끝남') # 각 프로세스가 순차적으로 실행됐다면 총 지연시간은 10초 이상이겠지만, 병렬이므로 1초대가 출력된다.

# 파이썬 프로그램의 데이터를 다른 파이프를 사용해 하위 프로세스로 보내거나, 하위 프로세스의 출력을 받을 수 있다.
# 이를 통해 여러 다른 프로드램을 사용해서 병렬적으로 작업을 수행할 수 있다.
# 예를 들어 openssl 명령줄 도구를 사용해 데이터를 암호화한다고 사용해보자. 명렬줄 인자를 사용해 자식 프로세스를 시작하고, 자식 프로세스와 I/O파이프를 연결한다.

def run_encrypt(data):
    env = os.environ.copy()
    env['password'] = 'zf7ShyBhZOraQDdE/FiZpm/m/8f9X+M1'
    proc = subprocess.Popen(
        ['openssl', 'enc', '-des3', '-pass', 'env:password'],
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    proc.stdin.write(data)
    proc.stdin.flush() # 자식이 입력을 받도록 보장한다
    return proc

def use_subprocess_2():
    # 다음 코드는 난수 바이트 문자열을 암호화 함수에 연결하지만, 실전에서는 파이프를 통해 사용자 입력, 파일 핸들, 네트워크 소켓등에서
    # 받은 데이터를 암호화 함수에 보내게 된다.
    procs = []
    for _ in range(3):
        data = os.urandom(10)
        proc = run_encrypt(data)
        procs.append(proc)

    # 자식 프로세스는 병렬로 실행되면서 입력을 소비한다. 다음 코드는 자식 프로세스가 끝나기를 기다렸다가 마지막 출력을 가져온다.
    for proc in procs:
        out, _ = proc.communicate()
        print(out[-10:])


# 유닉스 파이프라인처럼 한 자식 프로세스의 출력을 다음 프로세스의 입력으로 계속 연결시켜서 여려 병렬 프로세스를 연쇄적으로 연결할 수도 있다.
# 다음 openssl 명렬줄 도구를 하위 프로세스로 만들어서 입력 스트림의 월풀 해시를 계산한다.
def run_hash(input_stdin):
    return subprocess.Popen(
        ['openssl', 'dgst', '-whirlpool', '-binary'],
        stdin=input_stdin,
        stdout=subprocess.PIPE)

def use_subprocess_3():
    # 이제 데이터를 암호화하는 프로세르를 실행하고, 이 프로세스들로부터 나온 해시를 게산하는 프로세스를 실행할 수 있다.
    encrypt_procs = []
    hash_procs = []

    for _ in range(3):
        data = os.urandom(100)

        encrypt_proc = run_encrypt(data)
        encrypt_procs.append(encrypt_proc)

        hash_proc = run_hash(encrypt_proc.stdout)
        hash_procs.append(hash_proc)

        # 자식이 입력 스트림에 들어오는 데이터를 소비하고 communicate() 메서드가
        # 불필요하게 자식으로부터 오는 입력을 훔쳐가지 못하게 만든다.
        # 또 다운스트림 프로세스가 죽으면 SIGPIPE를 업스트림 프로세스에 전달한다.
        encrypt_proc.stdout.close()
        encrypt_proc.stdout = None

    # 자식 프로세스륻ㄹ이 시작되면 프로세스간 I/O가 자동으로 일어난다.
    for proc in encrypt_procs:
        proc.communicate()
        assert proc.returncode == 0

    for proc in hash_procs:
        out, _ = proc.communicate()
        print(out[-10:])

    assert proc.returncode == 0

# 만약 프로세스가 끝나지 않아 입력이나 출력 파이프를 기다리다 블록되는 경우가 우려되면 timeout 파라미터를 communicate메서드에 전달할 수 있다.
# timeout 값을 전달하면 자식 프로세스가 주어진 시간에 끝나지 않을 시 예외가 발생한다.
def use_subprocess_4():
    proc = subprocess.Popen(['sleep', '10'])
    try:
        proc.communicate(timeout=0.1)
    except subprocess.TimeoutExpired:
        proc.terminate()
        proc.wait()

    print('종료 상태', proc.poll())



# ======================================================================================================================
if __name__ == "__main__":
    for mtd in [
        use_subprocess,
        use_subprocess_2,
        use_subprocess_3,
        use_subprocess_4,
        use_thread_1,
        use_thread_2,
        caution_thread_1,
        caution_thread_2,
        use_Queue_1,
        use_Queue_2,
        use_Queue_3,
        use_Queue_4,
        use_Queue_5
    ]:
        mtd()
        print('==================================================================')
