# ======================================================================================================================
# asyncio로 쉽게 옮겨갈 수 있도록 스레드와 코루틴을 함께 사용하라.
# better way 62 참조
# asyncio 이벤트 루프의 run_in_executor 메서드를 사용하면 코루틴이 ThreadPoolExecutor 스레드 풀을 사용해 동기적인 함수를 호출할 수 있다.
# 이 기능을 활용하면 코드를 하향식으로 asyncio로 마이그레이션할 수 있다.
# asyncio 이벤트 루프의 run_until_complete 메서드를 사용하면 동기적인 코드가 코루틴을 호출하고 완료를 기다릴 수있다.
# 이 메서드를 활용하면 코드를 상향식으로 asyncio로 마이그레이션할 때 도움이 된다.

# 응답성을 최대로 높이려면 asyncio 이벤트 루프를 블록하지 말라.
# better way 63 참조
# 시스템 콜(블로킹 I/O와 스레드 시작도 포함해)을 코루틴으로 만들면 프로그램의 응답성이 좋아지고 사용자가 느끼는 지연 시간을 줄일 수 있다.
# debug=True 파라미터를 asyncio.run에 넘기면 이벤트 루프가 빨리 반응하지 못하게 방해하는 코루틴을 식별할 수 있다.

# 진정한 병렬성을 살리려면 concurrent.futures를(ThreadPoolExecutor, ProcessPoolExecutor[multiprocessing]) 사용하라.
# better way 64 참조
# multiprocessing 모듈을 사용하면 특정 유형의 파이썬 계산을 최소의 노력으로 병렬화할 수 있다. (큰 단위 추천, 작은 단위는 복잡하지만 구현 가능)
# concurrent.futures 내장 모듈이 제공하는 간단한 ProcessPoolExecutor 클래스를 활용하면 multiprocessing의 능력을 최대한 활용할 수 있다.
# 사용할 수 있는 모든 방법을 다 써보기전에는 multiprocessing이 제공하는 (복잡한) 고급 기능을 시도하지 말라.
# ======================================================================================================================
# 아래 기능을 코루틴으로 포팅해보자
class EOFError(Exception):
    pass


class AsyncConnectionBase:
    def __init__(self, reader, writer):  # 변경됨
        self.reader = reader  # 변경됨
        self.writer = writer  # 변경됨

    async def send(self, command):
        line = command + '\n'
        data = line.encode()
        self.writer.write(data)  # 변경됨
        await self.writer.drain()  # 변경됨

    async def receive(self):
        line = await self.reader.readline()  # 변경됨
        if not line:
            raise EOFError('연결 닫힘')
        return line[:-1].decode()

import random

WARMER = '더따뜻함'
COLDER = '더차가움'
UNSURE = '잘모르겠음'
CORRECT = '맞음'

class UnknownCommandError(Exception):
    pass

class AsyncSession(AsyncConnectionBase):  # 변경됨
    def __init__(self, *args):
        super().__init__(*args)
        self._clear_state(None, None)

    def _clear_state(self, lower, upper):
        self.lower = lower
        self.upper = upper
        self.secret = None
        self.guesses = []

    async def loop(self):  # 변경됨
        while command := await self.receive():  # 변경됨
            parts = command.split(' ')
            if parts[0] == 'PARAMS':
                self.set_params(parts)
            elif parts[0] == 'NUMBER':
                await self.send_number()  # 변경됨
            elif parts[0] == 'REPORT':
                self.receive_report(parts)
            else:
                raise UnknownCommandError(command)

    def set_params(self, parts):
        assert len(parts) == 3
        lower = int(parts[1])
        upper = int(parts[2])
        self._clear_state(lower, upper)

    def next_guess(self):
        if self.secret is not None:
            return self.secret

        while True:
            guess = random.randint(self.lower, self.upper)
            if guess not in self.guesses:
                return guess

    async def send_number(self):
        guess = self.next_guess()
        self.guesses.append(guess)
        await self.send(format(guess))

    def receive_report(self, parts):
        assert len(parts) == 2
        decision = parts[1]
        last = self.guesses[-1]
        if decision == CORRECT:
            self.secret = last

        print(f'서버: {last}는 {decision}')


import contextlib
import math

class AsyncClient(AsyncConnectionBase):
    def __init__(self, *args):
        super().__init__(*args)
        self._clear_state()

    def _clear_state(self):
        self.secret = None
        self.last_distance = None

    @contextlib.asynccontextmanager                         # 변경됨
    async def session(self, lower, upper, secret):          # 변경됨
        print(f'\n{lower}와 {upper} 사이의 숫자를 맞춰보세요!'
              f' 쉿! 그 숫자는 {secret} 입니다.')
        self.secret = secret
        await self.send(f'PARAMS {lower} {upper}')          # 변경됨
        try:
            yield
        finally:
            self._clear_state()
            await self.send('PARAMS 0 -1')                   # 변경됨

    async def request_numbers(self, count):            # 변경됨
        for _ in range(count):
            await self.send('NUMBER')                  # 변경됨
            data = await self.receive()                # 변경됨
            yield int(data)
            if self.last_distance == 0:
                return

    async def report_outcome(self, number):                    # 변경됨
        new_distance = math.fabs(number - self.secret)
        decision = UNSURE

        if new_distance == 0:
            decision = CORRECT
        elif self.last_distance is None:
            pass
        elif new_distance < self.last_distance:
            decision = WARMER
        elif new_distance > self.last_distance:
            decision = COLDER

        self.last_distance = new_distance

        await self.send(f'REPORT {decision}')                  # 변경됨

        # 잠시 대기해서 출력 순서 조정
        await asyncio.sleep(0.01)
        return decision

import asyncio

async def handle_async_connection(reader, writer):
    session = AsyncSession(reader, writer)
    try:
        await session.loop()
    except EOFError:
        pass

async def run_async_server(address):
    server = await asyncio.start_server(
        handle_async_connection, *address)
    async with server:
        await server.serve_forever()

async def run_async_client(address):
    # 서버가 시작될 수 있게 기다려주기
    await asyncio.sleep(0.1)

    streams = await asyncio.open_connection(*address)   # New
    client = AsyncClient(*streams)                      # New

    async with client.session(1, 5, 3):
        results = [(x, await client.report_outcome(x))
                   async for x in client.request_numbers(5)]

    async with client.session(10, 15, 12):
        async for number in client.request_numbers(5):
            outcome = await client.report_outcome(number)
            results.append((number, outcome))

    _, writer = streams                                # 새 기능
    writer.close()                                     # 새 기능
    await writer.wait_closed()                         # 새 기능

    return results

async def main_async():
    address = ('127.0.0.1', 4321)

    server = run_async_server(address)
    asyncio.create_task(server)

    results = await run_async_client(address)
    for number, outcome in results:
        print(f'클라이언트: {number}는 {outcome}')

# ======================================================================================================================
# 스레드를 사용한 I/O를 어떻게 asynico로 포팅할 수 있는지 알아둬라
# 파이썬은 for 루프, with 문, 제너레이터, 컴프리헨션의 비동기 버전을 제공하고, 코루틴 안에서 기존 라이브러리 도우미 함수를 대신해 즉시 사용할 수 있는 대안을 제공한다.
# asyncio 내장 모듈을 사용하면 스레드와 블로킹 I/O를 사용하는 기존 코드를 코루틴과 비동기 I/O를 사용하는 코드로 쉽게 포팅할 수 있다.

# 예를 들어 숫자를 추측하는 게임을 실행해주는 TCP 기반의 서버를 생각해보자.
# 이 서버는 고려할 숫자의 범위를 표현하는 lower와 upper 파라미터를 받는다. 그 후 클라이언트가 요청할 때마다 서버는 이 범위 안의 숫자를 반환한다.
# 마지막으로 서버는 자신이 추측한 숫자가 클러이언트가 정한 코드에 가까운지(따뜻함), 아니면 먼지(차가움)에 대한 정보를 클라이언트로 부터 받는다.

# 아런 유형의 클라이언트/서버 시스템을 구축하는 가장 일반적인 방법은 블로컹 I/O와 스레드를 사용하는 것이다.
# 그러려면 메세지 송수신을 처리하는 도우미 클래스가 필요하다. 이 경우 서버가 보내거나 받는 메세지 한 줄 한 줄은 처리할 명령을 표현한다.
class ConnectionBase:
    def __init__(self, connection):
        self.connection = connection
        self.file = connection.makefile('rb')

    def send(self, command):
        line = command + '\n'
        data = line.encode()
        self.connection.send(data)

    def receive(self):
        line = self.file.readline()
        if not line:
            raise EOFError('연결 닫힘')
        return line[:-1].decode()

# 서버는 한 번에 하나씩 연결을 처리하고 클라이언트의 세션 상태를 유지하는 클래스로 구현된다.
import random

class Session(ConnectionBase):
    def __init__(self, *args):
        super().__init__(*args)
        self._clear_state(None, None)

    def _clear_state(self, lower, upper):
        self.lower = lower
        self.upper = upper
        self.secret = None
        self.guesses = []

    # 이 클래스에서 가장 중요한 메서드는 다음에 보이는 메서드다. 이 메서드는 클라이언트에서 들어오는 메세지를 처리해 명령에 맞는 메서드를 호출해준다.
    # 대입식을 사용해 코드를 짧게 유지한다.
    def loop(self):
        while command := self.receive():
            parts = command.split(' ')
            if parts[0] == 'PARAMS':
                self.set_params(parts)
            elif parts[0] == 'NUMBER':
                self.send_number()
            elif parts[0] == 'REPORT':
                self.receive_report(parts)
            else:
                raise UnknownCommandError(command)

    # 첫 번째 명령은 서버가 추측할 값의 상한과 하한을 설정한다.
    def set_params(self, parts):
        assert len(parts) == 3
        lower = int(parts[1])
        upper = int(parts[2])
        self._clear_state(lower, upper)

    # 두 번째 명령은 클라이언트에 해당하는 Session 인스턴스에 저장된 이전 상태를 바탕으로 새로운 수를 추측한다.
    # 특히 이 코드는 서버가 파라미터가 설정된 시점 이후에 같은 수를 두 번 반복해 추측하지 않도록 보장한다.
    def next_guess(self):
        if self.secret is not None:
            return self.secret

        while True:
            guess = random.randint(self.lower, self.upper)
            if guess not in self.guesses:
                return guess

    def send_number(self):
        guess = self.next_guess()
        self.guesses.append(guess)
        self.send(format(guess))

    # 서 번째 명력은 서버의 추측이 따뜻한지 차가운지에 대해 클라이언트가 보낸 결과를 받은 후 Session 상태를 적절하게 바꾼다.
    def receive_report(self, parts):
        assert len(parts) == 2
        decision = parts[1]
        last = self.guesses[-1]
        if decision == CORRECT:
            self.secret = last

        print(f'서버: {last}는 {decision}')

# 클라이언트도 상태가 있는 클래스를 사용해 구현된다.
import contextlib
import math

class Client(ConnectionBase):
    def __init__(self, *args):
        super().__init__(*args)
        self._clear_state()

    def _clear_state(self):
        self.secret = None
        self.last_distance = None

    # 추측 게임의 파라미터를 with 문을 통해 설정함으로써 서버 측에서 상태를 제대로 관리하게 만든다.
    # 다음 명령은 첫 번쨰 명령을 서버에게 보낸다.
    @contextlib.contextmanager
    def session(self, lower, upper, secret):
        print(f'\n{lower}와 {upper} 사이의 숫자를 맞춰보세요!'
              f' 쉿! 그 숫자는 {secret} 입니다.')
        self.secret = secret
        self.send(f'PARAMS {lower} {upper}')
        try:
            yield
        finally:
            self._clear_state()
            self.send('PARAMS 0 -1')

    # 두 번째 명령을 구현하는 다른 메서드를 사용해 새로운 추측을 서버에게 요청한다.
    def request_numbers(self, count):
        for _ in range(count):
            self.send('NUMBER')
            data = self.receive()
            yield int(data)
            if self.last_distance == 0:
                return

    # 세번째 명령은 구현하는 마지막 메서드를 통해 서버가 돌려준 추측이 마지막으로 결과를 알려준 추측보다 더 차갑거나 따뜻한지를 알린다.
    def report_outcome(self, number):
        new_distance = math.fabs(number - self.secret)
        decision = UNSURE

        if new_distance == 0:
            decision = CORRECT
        elif self.last_distance is None:
            pass
        elif new_distance < self.last_distance:
            decision = WARMER
        elif new_distance > self.last_distance:
            decision = COLDER

        self.last_distance = new_distance

        self.send(f'REPORT {decision}')
        return decision

import socket
from threading import Thread

# 소켓에 listen하는 스레드를 하나 사용하고 새 연결이 들어올 때마다 스레드를 추가로 시작하는 방식으로 서버를 실행한다.
def handle_connection(connection):
    with connection:
        session = Session(connection)
        try:
            session.loop()
        except EOFError:
            pass


def run_server(address):
    with socket.socket() as listener:
        listener.bind(address)
        listener.listen()
        while True:
            connection, _ = listener.accept()
            thread = Thread(target=handle_connection,
                            args=(connection,),
                            daemon=True)
            thread.start()

# 클라이언트는 주 스레드에서 실행되며 추측 게임의 결과를 호출한 쪽에 돌려준다. 이 코드는 명시적으로 다양한 파이썬 언어 기능(for, with,
# 제너레이터, 컴프리헨션)을 활용한다.
def run_client(address):
    with socket.create_connection(address) as connection:
        client = Client(connection)

        with client.session(1, 5, 3):
            results = [(x, client.report_outcome(x))
                       for x in client.request_numbers(5)]

        with client.session(10, 15, 12):
            for number in client.request_numbers(5):
                outcome = client.report_outcome(number)
                results.append((number, outcome))

    return results

# 마지막으로 지금까지 만든 모든 요소를 하나로 붙여서 제대로 작동하는지 확인한다.
def main():
    address = ('127.0.0.1', 1234)
    server_thread = Thread(
        target=run_server, args=(address,), daemon=True)
    server_thread.start()

    results = run_client(address)
    for number, outcome in results:
        print(f'클라이언트: {number}는 {outcome}')

# ======================================================================================================================
if __name__ == "__main__":
    # Event loop is closed 에러는 window/python 3.8 이상 일때 발생하는 에러. 작동자체는 정상적으로 이뤄짐.
    main()
    asyncio.run(main_async())
