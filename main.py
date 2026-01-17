import time
import urllib3
from multiprocessing import Queue

from workers.WikiWorker import WikiWorker
from workers.YahooFinanceWorkers import YahooFinancePriceScheduler
from workers.PostgresWorker import PostgresMasterScheduler

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    symbol_queue = Queue()
    postgres_queue = Queue()
    scraper_start_time = time.time()

    wikiWorker = WikiWorker()
    yahoo_finance_threads = []

    # --- STEP 1: Start Postgres Consumer (The Database Writer) ---
    print("Starting Postgres Scheduler...")
    postgresMasterScheduler = PostgresMasterScheduler(input_queue=postgres_queue)
    postgresMasterScheduler.start()  # <--- CRITICAL FIX: MUST START THE THREAD!

    # --- STEP 2: Start Yahoo Producers (The Scrapers) ---
    # We use 15 threads to actually scrape in parallel
    num_yahoo_threads = 15
    print(f"Starting {num_yahoo_threads} Yahoo Scrapers...")
    
    for _ in range(num_yahoo_threads):
        y_scheduler = YahooFinancePriceScheduler(input_queue=symbol_queue, output_queue=postgres_queue)
        y_scheduler.start()
        yahoo_finance_threads.append(y_scheduler)

    # --- STEP 3: Fill the Queue ---
    print("Fetching symbols...")
    for symbol in wikiWorker.get_sp_500_companies():
        symbol_queue.put(symbol)

    # --- STEP 4: Send Stop Signals (Poison Pills) ---
    # We need one 'DONE' for every Yahoo thread
    for _ in range(num_yahoo_threads):
        symbol_queue.put("DONE")

    # --- STEP 5: Wait for Scrapers to Finish ---
    print("Waiting for scrapers to finish...")
    for t in yahoo_finance_threads:
        t.join()

    # --- STEP 6: Stop Postgres Consumer ---
    # Now that scrapers are done, tell Postgres to stop
    postgres_queue.put("DONE")
    postgresMasterScheduler.join()

    print("Extracting time took:", round((time.time() - scraper_start_time), 1))

if __name__ == "__main__":
    main()