import os
from time import sleep
import requests
from urllib.parse import urljoin
import json

import credentials

class Client(object):
    def __init__(self, username, password):
        self.base_url = "https://demo-api.ig.com/"
        self.watchlists_url = urljoin(self.base_url, "gateway/deal/watchlists/")
        self.api_key = "1f4a7f4278c35d01ce561326abdd2d7433fee8f4"
        self.username = "VEIO_DEMO"
        self.password = "UzZ4mObXT929"
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

    def display_selected_instruments(self, watchlist="Popular%20Markets"):
        """Prints out the instruments information from a given watchlist"""
        for instrument in self.get_instruments(watchlist):
            print("{:25.25} : {:6.6} {:6.6} {}".format(
                                           instrument["instrumentName"],
                                           str(instrument["offer"]),
                                           str(instrument["bid"]),
                                           str(instrument["updateTimeUTC"])))

if __name__ == "__main__":
    client = Client(credentials.username, credentials.password)
    client.connect()
    while True:
        os.system('clear')
        client.display_selected_instruments()
        sleep(10)
