import threading
import requests
import datetime
import time
import random
from lxml import html

class YahooFinancePriceScheduler(threading.Thread):
    def __init__(self, input_queue, output_queue, **kwargs):
        super(YahooFinancePriceScheduler, self).__init__(**kwargs)
        self._input_queue = input_queue
        self._output_queue = output_queue

    def run(self):
        while True:
            try:
                val = self._input_queue.get()
                if val == 'DONE':
                    break

                # Create worker and fetch price
                worker = YahooFinancePriceWorker(symbol=val)
                price = worker.get_price()
                
                # Only save if we got a valid number
                if isinstance(price, float):
                    print(f"{val}: {price}")
                    if self._output_queue is not None:
                        output_values = (val, price, datetime.datetime.utcnow())
                        self._output_queue.put(output_values)
                else:
                    print(price) # Print the error message (e.g., "Error 404")

            except Exception as e:
                print(f"Yahoo Scheduler Error: {e}")

class YahooFinancePriceWorker:
    def __init__(self, symbol):
        self._symbol = symbol.replace('.', '-')
        base_url = "https://finance.yahoo.com/quote/"
        self._url = f"{base_url}{self._symbol}"

    def get_price(self):
        time.sleep(random.uniform(0.5, 2.0))
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(self._url, headers=headers, timeout=20, verify=False)
            
            if response.status_code != 200:
                return f"{self._symbol}: Error {response.status_code}"

            page_contents = html.fromstring(response.content)
            xpath_str = '//*[@id="main-content-wrapper"]/section[1]/div[2]/div[1]/section/div/section[1]/div[1]/span[1]'
            elements = page_contents.xpath(xpath_str)
            
            if not elements:
                return f"{self._symbol}: No Price Found"

            raw_text = elements[0].text
            if raw_text:
                clean_text = raw_text.replace(',', '').strip()
                return float(clean_text)
                
        except Exception as e:
            return f"{self._symbol}: Failed ({e})"
            
        return f"{self._symbol}: Unknown Error"