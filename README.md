# Concurrent S&P 500 Stock Scraper

This project builds a high-speed data pipeline that grabs the list of S&P 500 companies from Wikipedia, scrapes their live stock prices from Yahoo Finance in parallel, and saves the data into a Postgres database.

## The Core Concept: Producer-Consumer Pattern

The "secret sauce" of this project is the **Producer-Consumer Pattern**.

Imagine a busy restaurant kitchen:

1. **The Waiter (WikiWorker)**: Takes orders (stock symbols) and puts them on a ticket rail.
2. **The Ticket Rail (Queue)**: Holds the orders until a chef is free.
3. **The Chefs (Yahoo Workers)**: 15 chefs working at the same time. As soon as one finishes a dish, they grab the next ticket. They don't wait for each other.
4. **The Pass (Queue 2)**: Finished dishes go here.
5. **The Expiditer (Postgres Worker)**: Takes finished dishes and delivers them to the table (Database).

If we did this sequentially (one person doing everything), it would take hours. By using **Concurrency** (multiple chefs), we finish in minutes.

## How It Works (The Pipeline)

### 1. The Setup (Main.py)

The `main.py` script is the manager. It sets up the queues (our "ticket rails") and hires the workers.

* It launches **1 Postgres Thread** (to write data).
* It launches **15 Yahoo Threads** (to scrape data).

### 2. Getting the List (WikiWorker)

First, the `WikiWorker` goes to Wikipedia and scrapes the table of all 500 companies. It puts every symbol (e.g., AAPL, GOOG, MSFT) into the `Symbol_Queue`.

### 3. Scraping in Parallel (YahooWorkers)

This is where the speed happens.

* The 15 threads act like hungry piranhas. They constantly check the `Symbol_Queue`.
* When a thread gets a symbol, it visits Yahoo Finance.
* It extracts the price, cleans it up (removes commas), and packages it with a timestamp.
* It puts the result into the `Postgres_Queue`.

### 4. Saving the Data (PostgresWorker)

The `PostgresMasterScheduler` watches the `Postgres_Queue`. Whenever a new price arrives, it inserts it into your database. It uses a single database connection to be efficient, rather than opening 500 separate connections.

## Why use Threads?

* **Sequential (Old way):** Download A... wait... save. Download B... wait... save. (Time: ~50 mins)
* **Concurrent (This way):** Download A, B, C, D, E... all at once. (Time: ~3 mins)

## How to Run It

1. **Prerequisites:**
* Python installed.
* A Postgres database running.
* Environment variables set for DB credentials (`PG_USER`, `PG_PW`, etc.).


2. **Install Dependencies:**
```bash
pip install requests lxml sqlalchemy psycopg2-binary

```


3. **Run the Script:**
```bash
python main.py

```



You will see logs showing the scrapers starting, followed by a stream of "Saved [SYMBOL] to DB" messages as the threads race to finish the work.