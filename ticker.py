import os
from datetime import datetime
import requests
from urllib.parse import urljoin
import json

import matplotlib.pyplot as plt

import credentials as cred

class Client(object):
    def __init__(self, username, password, api_key):
        self.base_url = "https://demo-api.ig.com/"
        self.watchlists_url = urljoin(self.base_url, "gateway/deal/watchlists/")
        self.instrument_url = urljoin(self.base_url, "gateway/deal/markets/")
        self.api_key = api_key
        self.username = username
        self.password = password
        self.headers = {"X-IG-API-KEY": self.api_key}

    def connect(self):
        """Connects to the account and gets the session keys"""
        payload = {"identifier": self.username,
                    "password": self.password}
        url = urljoin(self.base_url, "gateway/deal/session")
        r = requests.post(url, headers=self.headers, json=payload)
        self.headers["X-SECURITY-TOKEN"] = r.headers["X-SECURITY-TOKEN"]
        self.headers["CST"] = r.headers["CST"]

    def get_watchlists(self):
        """Returns a list of all the default and user watchlists. Important
            stocks can be added to a watchlist and only those ones updated"""
        r = requests.get(watchlists_url, headers=self.headers)
        self.watchlists = json.loads(r.content.decode())["watchlists"]

    def get_instruments(self, watchlist):
        """Pulls all the instruments from a given watchlist. The reply is JSON
            under 'markets'. Will fail if run before connect"""
        url = urljoin(self.watchlists_url, watchlist)
        r = requests.get(url, headers=self.headers)
        return json.loads(r.content.decode())["markets"]

    def display_watchlist_instruments(self, watchlist="Popular%20Markets"):
        """Prints out the instruments information from a given watchlist"""
        for instrument in self.get_instruments(watchlist):
            print("{:25.25} : {:6.6}/{:6.6} {}".format(
                                           instrument["instrumentName"],
                                           str(instrument["offer"]),
                                           str(instrument["bid"]),
                                           str(instrument["updateTimeUTC"])))

    def get_from_epic(self, epic):
        url = urljoin(self.instrument_url, epic)
        r = requests.get(url, headers=self.headers)
        data = json.loads(r.content.decode())
        rtn = dict()
        rtn['name'] = data['instrument']['name']
        rtn['bid'] = data['snapshot']['bid']
        rtn['offer'] = data['snapshot']['offer']
        rtn['high'] = data['snapshot']['high']
        rtn['low'] = data['snapshot']['low']
        rtn['percent'] = data['snapshot']['percentageChange']
        rtn['time'] = data['snapshot']['updateTime']
        return rtn

    def display_from_epic(self, epic):
        data = self.get_from_epic(epic)
        print("{:20.20}: {:6.6}/{:6.6} High:{:6.6} Low:{:6.6} %{} {}".format(
            data['name'], data['offer'], data['bid'],
            data['high'], data['low'], data['percent'], data['time']))
        return data
if __name__ == "__main__":
    client = Client(cred.username, cred.password, cred.api_key)
    client.connect()
    offers = []
    bids = []
    t = []
    plt.ion()
    fig, ax = plt.subplots()
    while True:
        os.system('clear')
        # client.display_watchlist_instruments()
        data = client.display_from_epic("IX.D.FTSE.CFD.IP")
        offers.append(data['offer'])
        bids.append(data['bid'])
        t.append(datetime.now())
        ax.plot(t, offers)
        ax.plot(t, bids)
        plt.gcf().autofmt_xdate()
        plt.show()
        plt.pause(10)
        ax.clear()
