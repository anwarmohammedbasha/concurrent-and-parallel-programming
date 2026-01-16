"""
Docstring for main
"""
import time


def calculate_sum_of_squares(n):
    sum_of_squares = 0
    for i in range(n):
        sum_of_squares += i ** 2

    print(sum_of_squares)


def sleep_a_little(seconds):
    time.sleep(seconds)


def main():

    start_time = time.time()

    for i in range(5):
        calculate_sum_of_squares((i+1) * 1000000)

    print("Calculating sum of squares took:",
          round(time.time() - start_time, 1))

    start_time = time.time()

    for i in range(1, 6):
        sleep_a_little(i)

    print("Sleep took:", round(time.time() - start_time, 1))


if __name__ == "__main__":
    main()