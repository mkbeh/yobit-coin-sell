# -*- coding: utf-8 -*-
import os
import time
import logging

from yobit_api import api


main_cfg = """currency1:
currency2:btc
api_key:
secret_key:
lt:1
"""
nonce_cfg = "0"
cfgs_lst = [main_cfg, nonce_cfg]

logging.basicConfig(filename='coin_sell.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


class CoinSell(object):
    def __init__(self):
        self.main_cfg = os.path.join(os.getcwd(), 'getme.cfg')
        self.nonce_cfg = os.path.join(os.getcwd(), 'nonce.cfg')
        self.public = api.PublicApi
        self.trade = api.TradeApi

    @staticmethod
    def is_file(*args):
        """
        Method which check configs on current directory , if not exist - create them.
        :param args: configs
        :return:
        """
        for num, arg in enumerate(args):
            if os.path.isfile(arg) is False:
                with open(arg, 'w') as file:
                    file.write(cfgs_lst[num].format(1))

    def get_data_from_cfg(self):
        """
        Method which read main config by line and return data.
        :return:
        """
        with open(self.main_cfg, 'r') as file:
            data_lst = [line.split(':')[1].replace('\n', '') for line in file]

        return data_lst

    def get_balance(self, api_key, secret_key, main_currency):
        """
        Method which get account balance of main currency , which must be set in getme config file.
        :param api_key:
        :param secret_key:
        :param main_currency:
        :return:
        """
        info = self.trade(key=api_key, secret_key=secret_key).get_info()
        time.sleep(3)

        return float(info['return']['funds'][main_currency])

    def drain_balance(self, bal, main_currency, alt_currency, key, secret_key):
        """
        Method which sell all amount of main currency on pair main_currency/alt_currency.
        :param bal: current balance
        :param main_currency: pair1 in getme.cfg file.
        :param alt_currency: pair2 in getme.cfg file.
        :param key:
        :param secret_key:
        :return:
        """
        pair = f'{main_currency}_{alt_currency}'
        starting_balance = balance = bal
        trade = self.trade(key=key, secret_key=secret_key)

        while balance > 1:
            time.sleep(3)
            last_bid_order = self.public().get_pair_depth(pair, 1)['bids']
            subtrahend = balance if balance < last_bid_order[0][1] else last_bid_order[0][1]

            try:
                order_id = trade.sell(f'{main_currency}_{alt_currency}', last_bid_order[0][0],
                                      subtrahend)['return']['order_id']
            except KeyError:
                raise Exception('The total amount of the transaction is less than the minimum acceptable value.')

            # Check on worked order.
            time.sleep(20)
            active_order = trade.get_active_orders(pair)['success']

            if int(active_order) != 0:
                # Cancel opened order.
                trade.cancel_order(order_id)

            # Get new balance.
            balance = self.get_balance(key, secret_key, main_currency)

        logging.info(f'{starting_balance} {main_currency} was successfully sold.')

    def run(self):
        """
        Method which:
        1. Check configs on exist.
        2. Drain balance of main currency (pair1 in config file).
        :return:
        """
        self.is_file(self.main_cfg, self.nonce_cfg)                                         # Check on configs exists
        main_currency, alt_currency, api_key, secret_key, lt = self.get_data_from_cfg()     # Get data from config.

        try:
            balance = self.get_balance(api_key, secret_key, main_currency)                  # Get balance.
        except KeyError:
            raise Exception('Non data in config.')

        if balance > float(lt):
            self.drain_balance(balance, main_currency, alt_currency, api_key, secret_key)   # Drain all balance.
        else:
            logging.info(f'Balance of {main_currency} is low than {lt}.')


if __name__ == '__main__':
    CoinSell().run()
