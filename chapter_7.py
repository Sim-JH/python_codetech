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
        use_subprocess_2
    ]:
        mtd()
        print('==================================================================')
