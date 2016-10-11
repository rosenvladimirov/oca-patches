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


class BG_CUSTOMS_getter(Currency_getter_interface):
    """Implementation of Currency_getter_factory interface
    for Bulgarian customs currency special rate for any taxes"""
    def get_updated_currency(self, currency_array, main_currency, max_delta_days):
        """implementation of abstract method of Curreny_getter_interface"""
        #_logger.info("BG_customs_getter start")
        self.validate_cur(main_currency)
        if main_currency != 'BGN':
                raise Exception('Could not update different currency %s'%(main_currency))
        url = "http://www.customs.bg/bg/page/25"
        if main_currency in currency_array :
            currency_array.remove(main_currency)
        #soup = BeautifulSoup(self.get_url_by_browser(url),"html.parser")
        soup = BeautifulSoup(self.get_url(url),"html.parser")
        data_table = soup.find('div', {'id': 'content'})
        for date in data_table.find_all('p'):
             date_now = date.find(text=lambda text: text.encode('utf-8').strip().startswith('валидни за периода от'))
             if date_now != None:
                 break
        date_start = datetime.strptime(date_now.split()[4],'%d.%m.%Y')
        date_end = datetime.strptime(date_now.split()[7],'%d.%m.%Y')
        self.check_rate_date(datetime.today(), (date_end-datetime.today()).days)
        # collect currency rate from webpage
        table = data_table.find('table')
        table_body = table.find('tbody')
        data = []
        rates = []
        for j, row in enumerate(table_body.find_all('tr')):
                if j == 0: # skip first row of title in table
                        continue
                row_in = []
                for i, cell in enumerate(row.find_all('td')):
                        cell_inc = cell.find(text=True)
                        if i in {1, 3, 4}:
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
            val = float(data[inx][2])/float(data[inx][1])
            rates.append([data[inx][0], 1/val])
            if val :
                self.updated_currency['rate_statistics'][data[inx][0]] = 1/val
                #_logger.info("Row %s" % 1/val)
            else :
                raise Exception('Could not update the %s'%(data[inx][0]))
        _logger.debug("Rate retrieved : 1 %s = %s" % (main_currency, rates))
        return self.updated_currency, self.log_info

