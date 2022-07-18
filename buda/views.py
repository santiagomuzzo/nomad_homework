import time

from django.shortcuts import render
from django.views import View

import requests


class TradeObtainer(View):

    def __init__(self):
        self.in_period = True
        self.selected_trade = {}
        self.all_trades_in_market = []
        self.response = {}
        self.actual_time = time.time_ns()
        self.timestamp = time.time_ns()
        self.last_timestamp = time.time_ns()
        self.one_day_ns = 60 * 60 * 24 * 1000000000
        self.value_top_trade = 0
        self.url = ''
        self.market_ids = self._obtain_markets()
        self.top_trades = 'self.get()'

    def _obtain_markets(self):
        market_ids = []
        self.url = 'https://www.buda.com/api/v2/markets'
        self.response = requests.get(self.url)
        self.response = self.response.json()
        for market in self.response['markets']:
            market_ids.append(market['id'])
        return market_ids

    def get_one_period_trades(self, market):
        self.url = f'https://www.buda.com/api/v2/markets/{market}/trades'
        self.response = requests.get(self.url, params={
            'timestamp': self.last_timestamp / 1000000,
            'limit': 100,
        })
        return self.response.json()

    def top_trade_calculator(self):
        self.value_top_trade = 0
        self.selected_trade = {
            'timestamp': '0', 'amount': '0', 'price': '0', 'direction': '-',
            }
        for trade in self.all_trades_in_market:
            trade_value = float(trade[1]) * float(trade[2])
            if self.value_top_trade < (trade_value):
                self.value_top_trade = trade_value
                self.selected_trade['timestamp'] = trade[0]
                self.selected_trade['amount'] = trade[1]
                self.selected_trade['price'] = trade[2]
                self.selected_trade['direction'] = trade[3]

    def market_trades(self, market):
        self.in_period = True
        self.all_trades_in_market = []
        self.last_timestamp = time.time_ns()
        while self.in_period:
            self.response = self.get_one_period_trades(market)
            self.last_timestamp = (int(
                self.response['trades']['last_timestamp']) * 1000000)
            if (self.actual_time - self.last_timestamp) <= self.one_day_ns:
                trades = self.response['trades']['entries']
                self.all_trades_in_market = self.all_trades_in_market + trades
            else:
                self.in_period = False
                for trade in self.response['trades']['entries']:
                    if (self.actual_time - (int(trade[0]) * 1000000)) <= (
                            self.one_day_ns):
                        self.all_trades_in_market.append(trade)

    def get(self, request):
        top_trades = []
        for market in self.market_ids:
            self.market_trades(market)
            self.top_trade_calculator()
            self.selected_trade['market'] = market
            self.selected_trade['value'] = self.value_top_trade
            if self.selected_trade['amount'] != '0':
                self.selected_trade['timestamp'] = time.ctime(
                    int(self.selected_trade['timestamp']) / 1000)
            else:
                self.selected_trade['timestamp'] = '-'
            top_trades.append(self.selected_trade)

        context = {'top_trades': top_trades}
        return render(request, 'buda/callampa.html', context)
