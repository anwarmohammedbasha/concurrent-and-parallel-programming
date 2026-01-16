import time


from workers.SquaredSumWorkers import SquaredSumWorker
from workers.SleepyWorkers import SleepyWorker

def main():

    start_time = time.time()

    for i in range(5):
        max_value = (i+1) * 1000000
        squaredSumWorker = SquaredSumWorker(n=max_value)

    squaredSumWorker.join()

    print("Calculating sum of squares took:",
          round(time.time() - start_time, 1))

    start_time = time.time()

    for seconds in range(1, 6):
        sleepyWorker = SleepyWorker(seconds=seconds)
    
    sleepyWorker.join()

    print("Sleep took:", round(time.time() - start_time, 1))


if __name__ == "__main__":
    main()
