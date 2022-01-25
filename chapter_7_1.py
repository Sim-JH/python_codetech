# ======================================================================================================================
# I/O를 할 때는 코루틴을 사용해 동시성을 높여라.
# better way 56~59에서는 생명 게임 예제를 사용해 병렬 I/O 문제를 해결하려 노력했고, 다양한 수준의 성공을 거둘 수 있었다.
# 다만 수천 개의 동시성 함수를 다룰 때 다른 접근 방식은 모두 한계가 있었다.

# 파이썬은 높은 I/O 동시성을 처리하기 위해 코루틴을 사용한다. 코루틴을 사용하면 파이썬 안에서 동시에 실행되는 것처럼 보이는 함수를 아주 많이 쓸 수 있다.
# 코루틴은 async와 await 키워드를 사용해 구현되며, 제너레이터를 실행하기 위한 인프라를 사용한다.

# 코루틴을 시작하는 비용은 함수 호출뿐이다. 활성화된 코루틴은 종료될 때까지 1KB 미만의 메모리를 사용한다. 스레드와 마찬가지로 코루틴도
# 환경으로부터 입력을 소비하고 결과를 출력할 수 있는 독립적인 함수다. 코루틴과 스레드를 비교해보면, 코루틴은 매 await 식에서 일시 중단되고
# 일시 중단된 대기 가능성(awaitable)이 해결된 다음에 async 함수로부터 실행을 재개한다는 차이점이있다. (제너레이터의 yield 동작과 비슷하다)

# 여러 분리된 async 함수가 서로 장단을 맞춰 실행되면 마치 모든 async 함수가 동시에 실행되는 것처럼 보이며, 이를 통해 파이썬 스레드의
# 동시성 동작을 흉내 낼 수 있다. 하지만 이런 동작을 하는 코루틴은 스레드와 달리 메무리 부가 비용이나 시작비용, 컨텍스트 전환 비용이
# 들지 않고 복잡한 락과 동기화 코드가 필요하지 않다. 코루틴을 가능하게 하는 매커니즘은 이벤트 루프(event loop)로 다수의 I/O를 효율적으로
# 동시에 실행할 수 있고 이벤트 루프에 맞춰 작성된 함수들을 빠르게 전환해가면서 골고루 실행할 수 있다.

# 코루틴을 사용해 생명 게임을 구현해보자. Thread나 Queue를 사용한 방법에 나타난 문제를 극복하면서 game_logic 함수 안에서 I/O를
# 발생시키는 것이 목표다. 이를 위해 먼저 async def를 사용해 game_logic 함수를 코루틴으로 만든다.
# 이렇게 async def로 함수를 정의하면 그 함수 안에서 I/O에 await 구문(소켓에서 비동기적으로 read하기 등)을 사용할 수 있다.
from queue import Queue
from threading import Thread
from threading import Lock
import time

from queue import Queue
# 파이썬 3.6이하에서는 실행되지 않는다.

class ClosableQueue(Queue):
    SENTINEL = object()

    def close(self):
        self.put(self.SENTINEL)

    def __iter__(self):
        while True:
            item = self.get()
            try:
                if item is self.SENTINEL:
                    return   # 스레드를 종료시킨다
                yield item
            finally:
                self.task_done()

in_queue = ClosableQueue()
logic_queue = ClosableQueue()
out_queue = ClosableQueue()

class StoppableWorker(Thread):
    def __init__(self, func, in_queue, out_queue, **kwargs):
        super().__init__(**kwargs)
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        for item in self.in_queue:
            result = self.func(item)
            self.out_queue.put(result)

ALIVE = '*'
EMPTY = '-'

class SimulationError(Exception):
    pass

class Grid:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.rows = []
        for _ in range(self.height):
            self.rows.append([EMPTY] * self.width)

    def get(self, y, x):
        return self.rows[y % self.height][x % self.width]

    def set(self, y, x, state):
        self.rows[y % self.height][x % self.width] = state

    def __str__(self):
        output = ''
        for row in self.rows:
            for cell in row:
                output += cell
            output += '\n'
        return output

def count_neighbors(y, x, get):
    n_ = get(y - 1, x + 0) # 북(N)
    ne = get(y - 1, x + 1) # 북동(NE)
    e_ = get(y + 0, x + 1) # 동(E)
    se = get(y + 1, x + 1) # 남동(SE)
    s_ = get(y + 1, x + 0) # 남(S)
    sw = get(y + 1, x - 1) # 남서(SW)
    w_ = get(y + 0, x - 1) # 서(W)
    nw = get(y - 1, x - 1) # 북서(NW)
    neighbor_states = [n_, ne, e_, se, s_, sw, w_, nw]
    count = 0
    for state in neighbor_states:
        if state == ALIVE:
            count += 1
    # 여기서 블러킹 I/O를 수행한다
    #data = my_socket.recv(100)
    return count

async def game_logic(state, neighbors):
    if state == ALIVE:
        if neighbors < 2:
            return EMPTY # 살아 있는 이웃이 너무 적음: 죽음
        elif neighbors > 3:
            return EMPTY # 살아 있는 이웃이 너무 많음: 죽음
    else:
        if neighbors == 3:
            return ALIVE # 다시 생성됨

    # 여기서 I/O를 수행한다
    #data = await my_socket.recv(100)
    return state

# 위와 비슷한 방식으로 step_cell 정의에 def를 추가하고 game_logic 함수 호출앞에 await를 덧붙이면 step_cell을 코루틴으로 바꿀 수 있다.
async def step_cell(y, x, get, set):
    state = get(y, x)
    neighbors = count_neighbors(y, x, get)
    next_state = await game_logic(state, neighbors)
    set(y, x, next_state)

class ColumnPrinter:
    def __init__(self):
        self.columns = []

    def append(self, data):
        self.columns.append(data)

    def __str__(self):
        row_count = 1
        for data in self.columns:
            row_count = max(
                row_count, len(data.splitlines()) + 1)

        rows = [''] * row_count
        for j in range(row_count):
            for i, data in enumerate(self.columns):
                line = data.splitlines()[max(0, j - 1)]
                if j == 0:
                    padding = ' ' * (len(line) // 2)
                    rows[j] += padding + str(i) + padding
                else:
                    rows[j] += line

                if (i + 1) < len(self.columns):
                    rows[j] += ' | '

        return '\n'.join(rows)

import asyncio

# 마찬가지로 simulate 함수도 코루틴으로 만들어야 한다.

# simulate 함수의 코루틴 버전을 자세히 살펴보자.
# step_cell을 호출해도 이 함수가 즉시 호출되지 않는다. 대신 step_cell 호출은 나중에 await 식에 사용할 수 있는 coroutine 인스턴스를 반환한다.
# 마치 yield를 사용하는 제너레이터 함수를 호출하면 즉시 실행하지 않고 제너레이터를 반호나하는 것과 같다. 이와 같은 실행 연기 메커니즘이 팬아웃을 수행한다.

# asyncio 내장 라이브러리가 제공하는 gather 함수는 팬인을 수행한다. gather에 대해 적용한 await 식은 이벤트 루프가 step_cell 코루틴을
# 동시에 실행하면서 step_cell 코루틴이 완료될 때마다 simulate 코루틴 실행을 재개하라고 요청한다.
# 모든 실행이 단일 스레드에서 이뤄지므로 Grid 인스턴스에 락을 사용할 필요가 없다. I/O는 asyncio가 제공하는 이벤트 루프의 일부분을 병렬화한다,
async def simulate(grid):
    next_grid = Grid(grid.height, grid.width)

    tasks = []
    for y in range(grid.height):
        for x in range(grid.width):
            task = step_cell(
                y, x, grid.get, next_grid.set)  # 팬아웃
            tasks.append(task)

    await asyncio.gather(*tasks)  # 팬인

    return next_grid

grid = Grid(5, 9)
grid.set(0, 3, ALIVE)
grid.set(1, 4, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(2, 3, ALIVE)
grid.set(2, 4, ALIVE)

# 마지막으로 asyncio.run 함수를 사용해 simulate 코루틴을 이벤트 루프상에서 실행하고 각 함수가 의존하는 I/O를 수행한다.
columns = ColumnPrinter()
for i in range(5):
    columns.append(str(grid))
    # python 3.7이상에서만 asyncio.run을 제공함
    grid = asyncio.run(simulate(grid)) # 이벤트 루프를 실행한다

print(columns)


# ======================================================================================================================
# 언제 동시성이 필요한지 인식하는 방법을 알아둬라

# 프로그램이 다루는 영역이 커짐에 따라 불가피하게 복작도도 증가한다. 프로그램의 명확성, 테스트 가능성, 효율성을 유지하면서 늘어나는 요구
# 조건을 만족하는 것은 프로그래밍에서 가장 어려운 부분이다. 그 중에서도 가장 처리하기 어려운 게 단일 스레드 프로그램을 동시 실행되는
# 여러 흐름으로 이뤄진 프로그램으로 바꾸는 경우일거다.

# 동시성을 율하는 가장 일반적인 방법으로는 팬아웃(새로운 동시성 단위들을 만듦)과 팬인(기존 동시성 단위들의 실행이 끝나기를 기다림)이 있다.
# 파이썬은 팬아웃과 팬인을 구현하는 다양한 방법들을 제공한다.
# 자세한 내용은 better way 56 참조

# 요구에 따라 팬아웃을 진행하려면 새로운 스레드를 생성하지 말아라.
# 자세한 내용은 better way 57 참조
# 스레드에는 많은 단점이 있다. 스레드를 시작하고 실행하는 데 비용이 들기 때문에 스레드가 많이 필요하면 상당히 많은 메모리를 사용한다.
# 그리고 스레드 사이를 조율하기 위해 Lock과 같은 특별한 도구를 사용해야 한다.
# 스레드를 시작하거나 스레드가 종료하기를 기다리는 코드에게 스레드 실행 중에 발생한 예외를 돌려주는 파이썬 내장 기능은 없다. 이로 인해
# 스레드 디버깅이 어려워진다.

# 동시성과 Queue를 사용하기 위해 코드를 어떻게 리팩터링해야 하는지 이해하라.
# 자세한 내용은 better way 58 참조
# 작업자 스레드 수를 고정하고 Queue와 함께 사용하면 스레드를 사용할 떄 팬인과 팬 아웃의 규모 확장성을 개선할 수 있다.
# Queue를 사용하도록 기존 코드를 리팩터링하려면 상당히 많은 작업이 필요하다. 특히 다단계로 이뤄진 파이프라인이 필요하면 작업량이 더 늘어난다.
# 다른 파이썬 내장 기능이나 모듈이 제공하는 병렬 I/O를 가능하게 해주는 다른 기능과 비교하면, Queue는 프로그램이 활용할 수 있는 전체 I/P 병렬성을 제한한다는 단전이 있다.

# 동시성을 위해 스레드가 필요한 경우에는 ThreadpoolExecutor를 사용하라
# 자세한 내용은 better way 59 참조
# ThreadpoolExecutor를 사용하면 한정된 리팩터링만으로 간단한 I/O 병렬성을 활성화할 수 있고, 동시성을 팬아웃해야하는 경우에 발생하는 스레드 시작 비용을 쉽게 줄일 수 있다.
# ThreadpoolExecutor를 사용하면 스레드를 직접 사용할 때 발생할 수 있는 잠재적인 메모리 낭비 문제를 없애주지만, max_workers의 개수를
# 미리 지정해야하므로 I/O 병렬성을 제한한다.
# ======================================================================================================================
if __name__ == "__main__":
    for mtd in [
    ]:
        mtd()
        print('==================================================================')
