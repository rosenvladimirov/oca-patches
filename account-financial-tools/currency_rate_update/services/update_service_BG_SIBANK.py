# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2009 CamptoCamp. All rights reserved.
#    @author Nicolas Bessi
#
#    Abstract class to fetch rates from Yahoo Financial
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from .currency_getter_interface import Currency_getter_interface

from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from bs4 import BeautifulSoup, Comment, NavigableString
from selenium import webdriver

import logging
_logger = logging.getLogger(__name__)


class BG_SIBANK_getter(Currency_getter_interface):
    """Implementation of Currency_getter_factory interface
    for Bulgarian customs currency special rate for any taxes"""
    def get_updated_currency(self, currency_array, main_currency, max_delta_days):
        """implementation of abstract method of Curreny_getter_interface"""
        self.validate_cur(main_currency)
        if main_currency != 'BGN':
                raise Exception('Could not update different currency %s'%(main_currency))
        url = "https://www.cibank.bg/bg/currency"
        if main_currency in currency_array :
            currency_array.remove(main_currency)
        #soup = BeautifulSoup(self.get_url_by_browser(url),"html.parser")
        soup = BeautifulSoup(self.get_url(url),"html.parser")
        data_table = soup.find('table', {'id': 'currency_table'})
        thead = data_table.find('thead')
        rate_date = datetime.strptime(thead.find('tr').find('td'),'%d.%m.%Y')
        self.check_rate_date(rate_date, max_delta_days)
        # collect currency rate from webpage
        table_body = data_table.find('tbody')
        data = []
        rates = []
        for j, row in enumerate(table_body.find_all('tr')):
                row_in = []
                for i, cell in enumerate(row.find_all('td')):
                        cell_inc = cell.find(text=True)
                        if i in {0, 1, 2, 3}:
                                row_in.append(cell_inc)
                data.append(row_in)
                #_logger.info("Row %s" % row_in)

        _logger.info("Array %s" % currency_array)
        _logger.info("Currency %s" % [x[0] for x in data])
        # Check and fill currency rate
        res = [[x[0] for x in data].index(y) for y in currency_array]
        _logger.info("Array %s" % res)
        for inx in res:
            _logger.info("Cur %s" % data[inx][0])
            self.validate_cur(data[inx][0])
            val1 = float(data[inx][2])/float(data[inx][1])
            val2 = float(data[inx][3])/float(data[inx][1])
            rates.append([data[inx][0], 1/val1, 1/val2])
            if val :
                self.updated_currency['rate_buy'][data[inx][0]] = 1/val1
                self.updated_currency['rate_sell'][data[inx][0]] = 1/val2
                #_logger.info("Row %s" % 1/val)
            else :
                raise Exception('Could not update the %s'%(data[inx][0]))
        _logger.debug("Rate retrieved : 1 %s = %s" % (main_currency, rates))
        return self.updated_currency, self.log_info

