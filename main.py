import time
import threading


def calculate_sum_of_squares(n):
    sum_of_squares = 0
    for i in range(n):
        sum_of_squares += i ** 2

    print(sum_of_squares)


def sleep_a_little(seconds):
    time.sleep(seconds)


def main():

    start_time = time.time()

    current_threads = []

    for i in range(5):
        max_value = (i+1) * 1000000
        t = threading.Thread(
            target=calculate_sum_of_squares, args=(max_value, ))
        t.start()
        current_threads.append(t)

    for i in range(len(current_threads)):
        current_threads[i].join()

    print("Calculating sum of squares took:",
          round(time.time() - start_time, 1))

    start_time = time.time()

    for seconds in range(1, 6):
        t = threading.Thread(target=sleep_a_little, args=(seconds,))
        t.start()
        current_threads.append(t)
        
    for i in range(len(current_threads)):
        current_threads[i].join()

    print("Sleep took:", round(time.time() - start_time, 1))


if __name__ == "__main__":
    main()
