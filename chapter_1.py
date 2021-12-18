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

    


    pass

if __name__ == "__main__":
    str_and_bytes()