#!/usr/bin/python

from stock_metrics import Prices, Screener

import argparse
import importlib
import json
import logging
import logging.config
import os
import re
import requests
import time


MY_PATH = os.path.abspath(os.path.dirname(__file__))
SCREEN_PLUGIN_DIR = os.listdir(os.path.join(MY_PATH, "screens"))
TICKER_FILE = os.path.join(MY_PATH, "tickers")

logging.config.fileConfig(os.path.join(MY_PATH, 'logging.conf'))


def valid_date(s):
    if re.match("^\d{1,2}/\d{1,2}/\d{4}", s) is not None:
        return s
    else:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


def load_screens():
    logging.info("Loading screens...")

    importlib.import_module("screens")

    pyfiles = re.compile(".py$", re.IGNORECASE)
    screen_plugins = filter(pyfiles.search, SCREEN_PLUGIN_DIR)
    form_module = lambda fp: '.' + os.path.splitext(fp)[0]
    plugins = map(form_module, screen_plugins)

    modules = []

    for plugin in plugins:
        if not plugin.startswith(".__"):
            try:
                mod = importlib.import_module(plugin, package="screens")
                logging.info("Loading {}".format(getattr(mod,
                                                         'SCREEN').get("name")))
                modules.append(mod)

            except ImportError, ie:
                logging.info("Ignoring ImportError {}".format(ie.message))

    return modules


def run(tickers, start_date=None):
    modules = load_screens()
    results = {}

    for ticker in tickers:
        scr = Screener(ticker, start_date)

        for module in modules:
            screen = getattr(module, 'SCREEN')
            name = screen.get("name")

            if name not in results:
                results[name] = {}
                results[name]["tickers"] = []
                results[name]["description"] = screen.get("description")
                results[name]["criteria"] = screen.get("criteria", [])

            logging.info("Running {} screen on ticker {}".format(name, ticker))

            if scr.run_screen(screen.get("conditions")):
                results[name]["tickers"].append(ticker)

    logging.info("Screens complete")
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--startdate",
                    action="store",
                    dest="startdate",
                    required=False,
                    help="Date (month/date/year) #/#/#### or ##/##/####",
                    type=valid_date)

    args = ap.parse_args()

    if args.startdate is not None:
        start_date = args.startdate
    else:
        start_date = time.strftime("%m/%d/%Y")

    tickers = []
    with open(TICKER_FILE, "r") as fh:
        for line in fh.readlines():
            if not line.startswith("#"):
                tickers.append(line.strip())

    results = run(tickers, start_date)

    logging.info("#" * 150)
    logging.info("Tickers Screened: {}".format(", ".join(tickers)))
    logging.info("Start Date: {}".format(start_date))

    for k, v in results.iteritems():
        logging.info("")
        logging.info("*" * 75)
        logging.info("***** {} *****".format(k))
        logging.info("{}".format(v["description"]))

        if len(v["criteria"]) > 0:
            logging.info("")
            logging.info("Criteria:")

        for c in v["criteria"]:
            logging.info("  * {}".format(c))

        logging.info("")

        logging.info("Matches:")

        if len(v["tickers"]) == 0:
            logging.info("  * None")
        else:
            for t in v["tickers"]:
                logging.info("  * {}".format(t))

        logging.info("*" * 75)

    logging.info("")
    logging.info("#" * 150)
