#!/usr/bin/env python

import argparse  # https://docs.python.org/3/library/argparse.html
import defusedxml.ElementTree as defused_ElementTree

from utils import Utils


class CurrencyTranslator(object):
    '''
    A simple utility to convert multiple currencies between them,
        retrieves the exchanges from boi - Bank of Israel:
        https://www.boi.org.il/en/Markets/Pages/explainxml.aspx
    '''

    NIS_STR = 'NIS'

    boi_urls = [
        'https://www.boi.org.il/currency.xml?curr=01',
        'https://www.boi.org.il/currency.xml?curr=02',
        'https://www.boi.org.il/currency.xml?curr=27',
    ]

    def __init__(self, currencies_dict=None):
        self.currencies_dict = dict()
        if type(currencies_dict) is dict:
            self.currencies_dict = currencies_dict
        elif type(currencies_dict) is list:
            for element in currencies_dict:
                self.currencies_dict[element.currency_name] = element

    def calculate_nis_from_other(self, amount=0, currency=''):
        if not currency.upper() in self.currencies_dict:
            raise TypeError('Not familiar currency: {}'.format(currency))

        CurrencyObj = self.currencies_dict[currency.upper()]
        amount_in_nis = round(
            float(amount) * CurrencyObj.exchange_rate_to_NIS, 3)

        return amount_in_nis

    def calculate_all(self, amount=0, currency=''):

        if not currency.upper() in self.currencies_dict:
            raise TypeError('Not familiar currency: {}'.format(currency))

        CurrencyObj = self.currencies_dict[currency.upper()]
        amount_in_nis = round(
            float(amount) * CurrencyObj.exchange_rate_to_NIS, 3)
        results_dict = dict()

        for currency_name, currencyObj in self.currencies_dict.items():
            results_dict[currency_name] = round(amount_in_nis
                                                / currencyObj.exchange_rate_to_NIS, 3)

        return results_dict


class CurrencyObj(object):
    def __init__(self, currency_name='', exchange_rate_to_NIS=0, url_of_exchange_xml=''):
        self.currency_name = currency_name
        self.url_of_exchange_xml = url_of_exchange_xml
        self.exchange_rate_to_NIS = float(exchange_rate_to_NIS)

    def __eq__(self, other):
        if not other:
            return False

        return self.currency_name == other.currency_name \
            and self.exchange_rate_to_NIS == other.exchange_rate_to_NIS \
            and self.url_of_exchange_xml == other.url_of_exchange_xml

    def __str__(self):
        return '{}<<{}, {}, {}>>'.format('CurrencyObj',
                                         self.currency_name, self.exchange_rate_to_NIS,
                                         self.url_of_exchange_xml)

    @staticmethod
    def extract_data_from_boi_xml(xml_root_element=None):
        # static method can't access: "cls" nor "self" ->
        # can't neither modify object state nor class state
        currency_name = xml_root_element[1][2].text
        exchange_rate = xml_root_element[1][4].text
        # print ('{} : {}'.format(currency_name, exchange_rate))
        return (currency_name, exchange_rate)

    @classmethod
    def create_currency_obj_from_xml(cls, xml_root_element=None,
                                     url_of_exchange_xml=''):
        # class method can't access "self" ->
        # can't object state.
        currency_name, exchange_rate = cls.extract_data_from_boi_xml(
            xml_root_element)
        currency_obj = CurrencyObj(
            currency_name, exchange_rate, url_of_exchange_xml)
        return currency_obj

    def set_exchange_rate_from_boi(self):
        '''
            can be used for refreshing the rates -> caching etc
        '''
        success_flag = False
        if self.url_of_exchange_xml:
            r = Utils.load_url(self.url_of_exchange_xml, timeout=60)
            xml_root_element = defused_ElementTree.fromstring(r)
            currency_name, exchange_rate = self.extract_data_from_boi_xml(
                xml_root_element)
            self.currency_name = currency_name
            self.exchange_rate_to_NIS = exchange_rate
            success_flag = True

        return success_flag


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("amount", help="the amount of currency",
                        type=float, nargs='?', const='0', default='0')
    parser.add_argument("currency", help="the currency type: USD, NIS etc..",
                        type=str, nargs='?', const=None, default=None)
    args = parser.parse_args()
    return args


def main(num=None, currency_name='None'):

    # TODO utilize redis db as a caching mechanism - reduces amount
    futures_dict = Utils.async_crawl(CurrencyTranslator.boi_urls)
    list_of_currencies = []
    result = ''

    for executed_future, url in futures_dict.items():
        xml_root_element = defused_ElementTree.fromstring(
            executed_future.result())
        currency_obj = CurrencyObj.create_currency_obj_from_xml(
            xml_root_element, url)

        list_of_currencies.append(currency_obj)

    nis_currency_obj = CurrencyObj(CurrencyTranslator.NIS_STR, 1)
    list_of_currencies.append(nis_currency_obj)
    currency_manager = CurrencyTranslator(list_of_currencies)

    result = currency_manager.calculate_all(1, CurrencyTranslator.NIS_STR)
    print('Current NIS exchange rate is:\n{}\n'.format(result))

    if currency_name and num:
        currency_name = currency_name.upper()
        print('Exchanging {} {} ---> '.format(num, currency_name))
        result = currency_manager.calculate_all(num, currency_name)
        print(result)

    return result


if __name__ == '__main__':
    sys_args = parse_arguments()
    # import pdb; pdb.set_trace()
    main(sys_args.amount, sys_args.currency)
