#!/usr/bin/python

import logging
import logging.config
import os
import re
import pandas_datareader.data as web
from datetime import datetime
from datetime import timedelta


MY_PATH = os.path.abspath(os.path.dirname(__file__))
logging.config.fileConfig(os.path.join(MY_PATH, 'logging.conf'))


class Prices(object):
    def __init__(self, ticker, start_date=None):
        self.price_data = self.load_historical_prices(ticker, start_date)
        self.open = []
        self.close = []
        self.high = []
        self.low = []

        for k, v in self.price_data.items():
            self.open.append(v["open"])
            self.close.append(v["close"])
            self.high.append(v["high"])
            self.low.append(v["low"])


    def load_historical_prices(self, ticker, start_date=None):
        logging.info("Getting historical prices for {}".format(ticker))

        # To simplify, get year's worth of prices
        end = datetime.now()
        start = end + timedelta(days=-365)
        data = web.DataReader(ticker.upper(), 'iex', start, end).to_dict()

        price_data = {}

        keys = data.get("open").keys()

        for date in keys:
            price_data[date] = {
                "open": data.get("open").get(date),
                "high": data.get("high").get(date),
                "low": data.get("low").get(date),
                "close": data.get("close").get(date)
            }

        return price_data


class Screener(object):
    def __init__(self, ticker, start_date=None):
        self.ticker = ticker
        self.price = Prices(ticker, start_date)


    def cross_over(self, fast_moving_avg, slow_moving_avg):
        last_fast = self.last_moving_average(fast_moving_avg)
        last_slow = self.last_moving_average(slow_moving_avg)
        prev_fast = self.prev_moving_average(fast_moving_avg)
        prev_slow = self.prev_moving_average(slow_moving_avg)

        return prev_fast < prev_slow and last_fast > last_slow


    def cross_under(self, fast_moving_avg, slow_moving_avg):
        last_fast = self.last_moving_average(fast_moving_avg)
        last_slow = self.last_moving_average(slow_moving_avg)
        prev_fast = self.prev_moving_average(fast_moving_avg)
        prev_slow = self.prev_moving_average(slow_moving_avg)

        return prev_fast > prev_slow and last_fast < last_slow


    def last_moving_average(self, day_range):
        return sum(self.price.close[(-1 * day_range):])/day_range


    def prev_moving_average(self, day_range):
        return sum(self.price.close[((-1 * day_range) - 1):-1])/day_range


    def last_closing_price(self):
        return self.price.close[-1]


    def run_screen(self, conditions):
        """
        Condition formats
        ARG1 OPERATOR ARG2

        ARG Formats:
            MA### = ### Moving Average
            OP = Last Opening Price
            CP = Last Closing Price
            DC### = ### Donchian Channel

        OPERATOR Formats:
            GT = Greater Than
            LT = Less Than
            GTE = Greater Than or Equal
            LTE = Less Than or Equal
            EQ = Equal
            XOVER = Cross Over
            XUNDER = Cross Under
        """
        operations = ["GT", "LT", "GTE", "LTE", "EQ", "XOVER", "XUNDER"]

        results = []

        for condition in conditions:
            logging.debug("Check condition {} for {}".format(condition,
                                                             self.ticker))
            (arg1, operator, arg2) = condition.split(" ")
            if arg1.startswith("MA"):
                a1 = int(arg1.replace("MA",""))
            elif arg1.startswith("DC"):
                pass
            elif arg1 == "OP":
                a1 = self.price.open[-1]
            elif arg1 == "CP":
                a1 = self.price.close[-1]
            else:
                msg = "Unrecognized argument {}".format(arg1)
                logging.error(msg)
                raise Exception(msg)

            if arg2.startswith("MA"):
                a2 = int(arg2.replace("MA",""))
            elif arg2.startswith("DC"):
                pass
            elif arg2 == "OP":
                a2 = self.price.open[-1]
            elif arg2 == "CP":
                a2 = self.price.close[-1]
            else:
                msg = "Unrecognized argument {}".format(arg2)
                logging.error(msg)
                raise Exception(msg)

            if operator not in operations:
                msg = "Unrecognized operation {}".format(operator)
                logging.error(msg)
                raise Exception(msg)
            else:
                if operator == "XOVER":
                    # Assumes fast moving average is first value
                    results.append(self.cross_over(a1, a2))
                elif operator == "XUNDER":
                    # Assumes fast moving average is first value
                    results.append(self.cross_under(a1, a2))
                elif operator == "GT":
                    results.append(a1 > a2)
                elif operator == "LT":
                    results.append(a1 < a2)
                elif operator == "GTE":
                    results.append(a1 >= a2)
                elif operator == "LTE":
                    results.append(a1 <= a2)
                else:
                    results.append(a1 == a2)

            logging.debug("Result for condition {} was {}".format(condition,
                                                                  results[-1]))

        if len(results) == 0:
            msg = "No conditions defined or passed"
            logging.error(msg)
            raise Exception(msg)
        else:
            if False in results:
                return False
            else:
                return True
