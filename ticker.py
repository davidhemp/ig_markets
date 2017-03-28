import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
from urllib.parse import urljoin
from urllib.error import URLError, HTTPError
import json

import matplotlib.pyplot as plt

import credentials as cred

class Client(object):
    def __init__(self, username, password, api_key):
        self.base_url = "https://demo-api.ig.com/"
        self.watchlists_url = urljoin(self.base_url, "gateway/deal/watchlists")
        self.instrument_url = urljoin(self.base_url, "gateway/deal/markets/")
        self.api_key = api_key
        self.username = username
        self.password = password
        self.headers = {"X-IG-API-KEY": self.api_key}
        self.connect()

    def connect(self):
        """Connects to the account and gets the session keys"""
        self.headers['version'] = "2";
        payload = {"identifier": self.username,
                    "password": self.password}
        url = urljoin(self.base_url, "gateway/deal/session")
        r = requests.post(url, headers=self.headers, json=payload)
        self.headers["X-SECURITY-TOKEN"] = r.headers["X-SECURITY-TOKEN"]
        self.headers["CST"] = r.headers["CST"]

    def get_watchlists(self):
        """Returns a list of all the default and user watchlists. Important
            stocks can be added to a watchlist and only those ones updated"""
        r = requests.get(self.watchlists_url, headers=self.headers)
        self.watchlists = json.loads(r.content.decode())["watchlists"]
        return self.watchlist

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
        self.headers['Version'] = "3"
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

    def get_history(self, epic, start_date=None, end_date=None):
        """Take a datetime object for start_date and/to end_date. If only
            start_date is given then it uses datetime.datetime.now() as the
            end_date"""
        #check inputs
        if end_date and not start_date:
                raise ValueError("End date without start date")
        if not start_date:
            start_date = datetime.now() - relativedelta(months=3)
            end_date = datetime.now()
        if not isinstance(end_date, datetime) \
            or not isinstance(start_date,datetime):
                raise ValueError(
                    "Start date and End date must be datetime obects")
        url = urljoin(self.base_url, "gateway/deal/prices/")
        url = urljoin(url, epic)
        self.headers['version'] = "3"
        params = {'pageSize':int(1e6)}
        params['from'] = "2017-03-20T12:30:00"
        params['to'] = "2017-03-28T12:30:00"
        # if start_date:
        #     str_start = start_date.strftime("%Y-%m-%dT%H:%M:%S")
        #     params['from'] = str_start
        #     if end_date:
        #         str_end = start_date.strftime("%Y-%m-%dT%H:%M:%S")
        #         params["to"] = str_end

        r = requests.get(url, headers=self.headers, params=params)
        return r
        if r.ok:
            data = json.loads(r.content.decode())['prices']
            bid = {'time':[], 'open':[], 'close':[], 'high':[], 'low':[]}
            ask = {'time':[], 'open':[], 'close':[], 'high':[], 'low':[]}
            for price in data:
                for sale, op in zip([bid, ask], ["bid", "ask"]):
                    sale['time'].append(datetime.strptime(price['snapshotTimeUTC'], "%Y-%m-%dT%H:%M:%S"))
                    sale['open'].append(price['openPrice'][op])
                    sale['close'].append(price['closePrice'][op])
                    sale['high'].append(price['highPrice'][op])
                    sale['low'].append(price['lowPrice'][op])
            return bid, ask
        else:
            raise URLError(":Request failed with code {}".format(r.status_code))

    def _candlestick(data, width=0.2, colorup='k', colordown='r',
                 alpha=1.0, ochl=True):

        """
        Plot the time, open, high, low, close as a vertical line ranging
        from low to high.  Use a rectangular bar to represent the
        open-close span.  If close >= open, use colorup to color the bar,
        otherwise use colordown
        Parameters
        ----------
        ax : `Axes`
            an Axes instance to plot to
        quotes : sequence of quote sequences
            data to plot.  time must be in float date format - see date2num
            (time, open, high, low, close, ...) vs
            (time, open, close, high, low, ...)
            set by `ochl`
        width : float
            fraction of a day for the rectangle width
        colorup : color
            the color of the rectangle where close >= open
        colordown : color
             the color of the rectangle where close <  open
        alpha : float
            the rectangle alpha level
        ochl: bool
            argument to select between ochl and ohlc ordering of quotes
        Returns
        -------
        ret : tuple
            returns (lines, patches) where lines is a list of lines
            added and patches is a list of the rectangle patches added
        """

        OFFSET = width / 2.0

        lines = []
        patches = []
        for q in quotes:
            if ochl:
                t, open, close, high, low = q[:5]
            else:
                t, open, high, low, close = q[:5]

            if close >= open:
                color = colorup
                lower = open
                height = close - open
            else:
                color = colordown
                lower = close
                height = open - close

            vline = Line2D(
                xdata=(t, t), ydata=(low, high),
                color=color,
                linewidth=0.5,
                antialiased=True,
            )

            rect = Rectangle(
                xy=(t - OFFSET, lower),
                width=width,
                height=height,
                facecolor=color,
                edgecolor=color,
            )
            rect.set_alpha(alpha)

            lines.append(vline)
            patches.append(rect)
            ax.add_line(vline)
            ax.add_patch(rect)
        ax.autoscale_view()

        return lines, patches

if __name__ == "__main__":
    client = Client(cred.username, cred.password, cred.api_key)
    client.connect()
    client.display_history(epic="IX.D.FTSE.IFM.IP")
    # offers = []
    # bids = []
    # t = []
    # plt.ion()
    # fig, ax = plt.subplots()
    # while True:
    #     os.system('clear')
    #     # client.display_watchlist_instruments()
    #     data = client.display_from_epic("IX.D.FTSE.CFD.IP")
    #     offers.append(data['offer'])
    #     bids.append(data['bid'])
    #     t.append(datetime.now())
    #     ax.plot(t, offers)
    #     ax.plot(t, bids)
    #     plt.gcf().autofmt_xdate()
    #     plt.show()
    #     plt.pause(10)
    #     ax.clear()
