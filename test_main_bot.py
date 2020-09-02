import unittest
from main import *


class CalcTest(unittest.TestCase):
    """rate bot tests"""

    @classmethod
    def setUpClass(cls):
        print("==========")

    def test_get_history_url(self):
        self.assertIsNone(get_history_url(10, 'not_valid_currency'))
        self.assertTrue(get_history_url(1000, 'eur'))
        self.assertEqual(get_history_url(-10, 'eur'), {})

    def test_get_list_url(self):
        self.assertTrue(get_list_url())

    def test_get_actual_rates(self):
        self.assertTrue(get_actual_rates("test_chat_id"))

    def test_is_valid_exchange_params(self):

        self.assertTrue(is_valid_exchange_params(['$20', 'To', 'Eur']))
        self.assertTrue(is_valid_exchange_params(['100', 'usD', 'to', 'eur']))
        self.assertFalse(is_valid_exchange_params(['usd', 'to', 'eur']))
        self.assertFalse(is_valid_exchange_params(['twenty', 'usd', 'to', 'eur']))
        self.assertFalse(is_valid_exchange_params(['20', 'usd', 'eur']))
        self.assertFalse(is_valid_exchange_params(['$20', 'usd', 'to', 'eur']))
        self.assertFalse(is_valid_exchange_params(['20', 'usd', 'to', 'dollar']))
        self.assertFalse(is_valid_exchange_params(['20', 'eur', 'to', 'eur']))

    def test_check_currency_name(self):

        self.assertTrue(check_currency_name('eur'))
        self.assertTrue(check_currency_name('CAD'))
        self.assertFalse(check_currency_name('dlo'))
        self.assertFalse(check_currency_name('Ca'))

    def test_build_chart(self):

        rate_and_period = {'2020-08-27': {'EUR': 0.8470269355},
                           '2020-08-28': {'EUR': 0.8392782207},
                           '2020-08-31': {'EUR': 0.837520938}}
        directory_name = 'charts'
        chart_path = build_chart(rate_and_period, 'eur')
        self.assertTrue(os.path.exists(directory_name))
        self.assertTrue(os.path.exists('{}'.format(chart_path)))

        # rate_and_period = {}
        # chart_path = build_chart(rate_and_period, 'eur')
        # self.assertFalse(os.path.exists('{}'.format(chart_path)))

    def test_is_valid_history_params(self):

        self.assertTrue(is_valid_history_params(['usd/EUR', 'for', '4', 'days']))
        self.assertTrue(is_valid_history_params(['USD/cad', 'for', '100', 'days']))
        self.assertFalse(is_valid_exchange_params(['usd', 'for', '4', 'days']))
        self.assertFalse(is_valid_exchange_params(['/EUR', 'for', '4', 'days']))
        self.assertFalse(is_valid_exchange_params(['usd/EUR', '4', 'days']))
        self.assertFalse(is_valid_exchange_params(['usd/EUR', 'for', 'days']))
        self.assertFalse(is_valid_exchange_params(['usd/EUR', 'for', '4' 'day']))
        self.assertFalse(is_valid_exchange_params(['usd/EUR']))


if __name__ == '__main__':
    unittest.main()
