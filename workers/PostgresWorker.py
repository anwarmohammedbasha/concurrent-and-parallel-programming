import threading
from sqlalchemy import create_engine, text
import os

class PostgresMasterScheduler(threading.Thread):
    def __init__(self, input_queue, **kwargs):
        super(PostgresMasterScheduler, self).__init__(**kwargs)
        self._input_queue = input_queue
        
        # OPTIMIZATION: Create the DB Engine ONCE, not 500 times.
        self._PG_USER = os.environ.get('PG_USER') or 'postgres'
        self._PG_PW = os.environ.get('PG_PW') or 'admin' # Make sure this matches your DB password
        self._PG_HOST = os.environ.get('PG_HOST') or 'localhost'
        self._PG_DB = os.environ.get('PG_DB') or 'postgres'
        
        db_url = f'postgresql://{self._PG_USER}:{self._PG_PW}@{self._PG_HOST}/{self._PG_DB}'
        self._engine = create_engine(db_url)

    def run(self):
        while True:
            try:
                val = self._input_queue.get()
                if val == 'DONE':
                    break
                
                symbol, price, extracted_time = val
                
                # Pass the existing engine to the worker
                worker = PostgresWorker(symbol, price, extracted_time, self._engine)
                worker.insert_into_db()
                print(f"Saved {symbol} to DB")
                
            except Exception as e:
                print(f"Postgres Scheduler Error: {e}")

class PostgresWorker:
    def __init__(self, symbol, price, extracted_time, engine):
        self._symbol = symbol
        self._price = price
        self._extracted_time = extracted_time
        self._engine = engine

    def _create_insert_query(self):
        return text("INSERT INTO prices (symbol, price, extracted_time) VALUES (:symbol, :price, :extracted_time)")
    
    def insert_into_db(self):
        try:
            with self._engine.connect() as conn:
                conn.execute(self._create_insert_query(), {
                    'symbol': self._symbol,
                    'price': self._price,
                    'extracted_time': self._extracted_time
                })
                conn.commit() # IMPORTANT: Commit the transaction
        except Exception as e:
            print(f"Error inserting {self._symbol}: {e}")