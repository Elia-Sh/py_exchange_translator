#!/usr/bin/env python

import types
import argparse  # https://docs.python.org/3/library/argparse.html
import defusedxml.ElementTree as defused_ElementTree

from utils import Utils
from py_exchange_translator import CurrencyTranslator, CurrencyObj


class CurrencyTester(object):
    '''

        test_case_input=<>,expected_result=<> ==  (actual_result=execute_method(<func(<>)>)
    '''

    _debug = False

    class FuncResult(object):
        def __init__(self, result=None, is_exception=False):
            self.is_exception = is_exception
            if is_exception:
                self.f_output = self.handle_exception(result)
            else:
                self.f_output = result

        def __str__(self):
            return '{}<{}, is_exception={}>'.format('FuncResult', self.f_output, self.is_exception)

        def handle_exception(self, raised_exception=None):
            handed_exception = '!!Raised Exception:\n\t{}'.format(
                str(raised_exception))
            return handed_exception

    @classmethod
    def run_test_case(cls, func_to_run=None, test_args=[],
                      expected_result=None, test_desc_str=''):

        print('Test Description:\t{}'.format(test_desc_str))
        if expected_result is None or func_to_run is None:
            raise SyntaxError(
                'Test Syntax ERROR: Please provide: <expected_result> and <func_to_run>'
            )

        result_test_success = False
        actual_result = cls.func_runner(test_args, func_to_run)

        if actual_result.f_output == expected_result:
            result_test_success = True
            print('Test Result:\t\tpassed :)\n')
        else:
            print('Test Result:\t\tFailed :(\n')

        if cls._debug:
            print('DEBUG: actual_result: \n\t{}'.format(actual_result))

        return (result_test_success, actual_result)

    @classmethod
    def func_runner(cls, test_args=[], func_to_run=None):

        if not (isinstance(func_to_run, types.FunctionType)
                or isinstance(func_to_run, types.MethodType)):
            # not that I'm explicitly excluding: callable(func_to_run)
            # since this way I'm blocking the user to provide class as: func_to_run
            #   classes have initiators that are callable methods -> currently not testing objects instantiations..
            raise SyntaxError(
                'Test Syntax ERROR: func_to_run={}; is not a function -> please provide a function;'.format(
                    func_to_run)
            )

        func_result = None
        if cls._debug:
            print('DEBUG: Running: {}\n  with args: {}'.format(
                func_to_run, test_args))
        try:
            func_result = cls.FuncResult(func_to_run(test_args))
        except Exception as e:
            func_result = cls.FuncResult(e, is_exception=True)
        return func_result


def main():

    # Execute multiple test cases and assert expected_r == actual_r
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

    test_root_xml = defused_ElementTree.fromstring(
        '''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
    <CURRENCIES>
    <LAST_UPDATE>2020-09-29</LAST_UPDATE>
    <CURRENCY>
        <NAME>Dollar</NAME>
        <UNIT>1</UNIT>
        <CURRENCYCODE>USD</CURRENCYCODE>
        <COUNTRY>USA</COUNTRY>
        <RATE>3.459</RATE>
        <CHANGE>-0.231</CHANGE>
    </CURRENCY>
    </CURRENCIES>
    ''')
    # not testing: CurrencyObj('USD', 3.459, '');
    # CurrencyObj initiator set 3 attributes to the instance, that's all.
    expected_result_obj = CurrencyObj('USD', 3.459, '')

    CurrencyTester.run_test_case(CurrencyObj.create_currency_obj_from_xml,
                                 test_root_xml, expected_result_obj,
                                 'Testing creation of currency object from BOI xml')


if __name__ == '__main__':
    # import pdb; pdb.set_trace()
    main()
