import time


def reverse():
    s = ["H", "a", "n", "n", "a", "h"]
    return s.reverse()


if __name__ == '__main__':
    start = time.time()
    for i in range(0, 100000):
        reverse()
    print((time.time() - start) * 1000)
