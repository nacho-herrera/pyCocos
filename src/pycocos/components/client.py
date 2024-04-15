# -*- coding: utf-8 -*-
"""
    pyCocos.client
    Manages api calls
"""

from typing import Any, Dict, List
import requests
import simplejson
import datetime

from . import urls
from .exceptions import ApiException


class RestClient:
    def __init__(self):
        self.session = requests.Session()
        self.messages: List[Dict[str, str]] = []

    def get_token(self, params: str, data: str) -> Dict[str, Any]:
        """Makes a request to the api to get an access token

        Args:
            params (dict): Dictionary with grant type
            data (str): String with email and password

        Returns:
            dict: Dict with token and user data
        """
        return self.api_request(
            urls.endpoints["token"], method="post", params=params, data=data
        )

    def get_2factors(self):
        return self.api_request(urls.endpoints["2factors"])

    def submit_challenge_request(self, challenge_id: str):
        return self.api_request(
            urls.endpoints["challenge"].format(challenge_id), method="post"
        )

    def submit_challenge_verification(self, challenge_id: str, json: str):
        return self.api_request(
            urls.endpoints["verify"].format(challenge_id), method="post", json_data=json
        )

    def logout(self) -> None:
        """Makes a request to the api to logout current session

        Returns:
            dict: empty dict
        """
        return self.api_request(urls.endpoints["logout"], method="post")

    def get_market_status(self) -> Dict[str, bool]:
        """Makes a request to the api to know if market is open


        Returns:
            dict: Market status (0-CI, 1-24hs, 2-48hs, 3-DolarMEP Bot, 4-??, 5-??) as boolean
        """
        return self.api_request(urls.endpoints["open_market"])

    def get_university(self) -> List[Dict[str, str]]:
        """Makes a request to the api to get Cocos University articles

        Returns:
            list: List of Cocos University articles
        """
        return self.api_request(urls.endpoints["university"])

    def get_carrousel(self) -> List[Dict[str, str]]:
        """Makes a request to the api to get home page's promoted instruments

        Returns:
            list: List of home page's promoted instruments
        """
        return self.api_request(urls.endpoints["carrousel"])

    def get_news(self) -> List[Dict[str, Any]]:
        """Makes a request to the api to get home page's news

        Returns:
            list: List of home page's news
        """
        return self.api_request(urls.endpoints["news"])

    def get_my_data(self) -> Dict[str, Any]:
        """Makes a request to the api to get my account data

        Returns:
            dict: Dict with account information
        """
        return self.api_request(urls.endpoints["my_data"])

    def get_investor_test(self) -> List[Dict[str, Any]]:
        """Makes a request to get the investor test questions

        Returns:
            list: List of questions
        """
        return self.api_request(urls.endpoints["investor_test"])

    def submit_investor_test(self, data: str) -> Dict[str, Any]:
        """Sends investor test answers

        Args:
            data (dict): Dictionary with the answers

        Returns:
            dict: API Response
        """
        return self.api_request(
            urls.endpoints["investor_test"], method="post", data=data
        )

    def get_daily_performance(self) -> Dict[str, Any]:
        """Makes a request to get daily performance of our account

        Returns:
            dict: Dictionary with the daily performance by ticker
        """
        return self.api_request(urls.endpoints["daily_performance"])

    def get_historic_performance(self) -> List[Dict[str, Any]]:
        """Makes a request to get historic performance of our account

        Returns:
            list: List of historic performance by ticker
        """
        return self.api_request(urls.endpoints["historic_performance"])

    def get_performance_period(self, date_from: str, date_to: str) -> Dict[str, Any]:
        """Makes a request to get internal rate of return of our account in a specified period of time

        Returns:
            dict: Dictionary with the account performance
        """
        return self.api_request(
            urls.endpoints["performance_period"].format(date_from, date_to)
        )

    def get_portfolio(self) -> Dict[str, Any]:
        """Makes a request to get account portfolio components with valuation

        Returns:
            dict: Dict with the valued portfolio
        """
        return self.api_request(urls.endpoints["portfolio"])

    def get_account_movements(
        self, date_from: str, date_to: str
    ) -> List[Dict[str, Any]]:
        """Makes a request to get account movements by currency in a given dateframe

        Args:
            date_from (str): Start date. Format: yyyy-MM-dd
            date_to (str): End date. Format: yyyy-MM-dd
            currency (Currency (Enum)): Currency of the account

        Returns:
            list: List of account movements
        """
        return self.api_request(
            urls.endpoints["account_movements"].format(date_from, date_to)
        )

    def get_transfers_receipt(self, receipt_id: str) -> Dict[str, Any]:
        """Makes a request to get movement receipt

        Args:
            r (str): Receipt id

        Returns:
            PDF Object: Receipt
        """
        return self.api_request(urls.endpoints["receipt"].format(receipt_id))

    def get_bank_accounts(self) -> List[Dict[str, Any]]:
        """Makes a request to get available customer bank accounts

        Returns:
            list: List of available accounts
        """
        return self.api_request(urls.endpoints["bank_accounts"])

    def submit_new_bank_account(self, data: str) -> Dict[str, Any]:
        """Sends new customer bank account information

        Args:
            data (dict): Dictionary with bank account data

        Returns:
            dict: API Response
        """
        return self.api_request(urls.endpoints["new_account"], method="post", data=data)

    def submit_funds_withdraw(self, data: str) -> Dict[str, Any]:
        """Sends money withdraw request

        Args:
            json (dict): Dictionary with withdraw information

        Returns:
            dict: API Response
        """
        return self.api_request(urls.endpoints["withdraw"], method="post", data=data)

    def get_orders(self) -> List[Dict[str, Any]]:
        """Makes a request to get the status of all orders

        Returns:
            list: List of orders statuses
        """
        return self.api_request(urls.endpoints["orders"])

    def submit_order(self, json: Dict[str, Any]) -> Dict[str, Any]:
        """Sends a new order to the market

        Args:
            json (dict): Dictionary with order parameters

        Returns:
            dict: API Response
        """
        return self.api_request(urls.endpoints["orders"], method="post", json_data=json)

    def get_order(self, order_number: str) -> Dict[str, Any]:
        """Makes a request to get a specific order, identified by number, status

        Args:
            order_number (str): Order number

        Returns:
            dict: Dictionary with order status
        """
        return self.api_request(urls.endpoints["order"].format(order_number))

    def cancel_order(self, order_number: str, data: str) -> Dict[str, Any]:
        """Sends a cancel working order request

        Args:
            order_number (str): Order number
            json (dict): Dictionary with ticker information

        Returns:
            dict: API Response
        """

        return self.api_request(
            urls.endpoints["order"].format(order_number), method="delete", data=data
        )

    def submit_repo_order(self, data: str) -> Dict[str, Any]:
        """Sends new repo (caucion) order

        Args:
            data (dict): Dictionary with order parameters

        Returns:
            dict: API Response
        """
        return self.api_request(urls.endpoints["repo"], method="post", data=data)

    def get_buying_power(self) -> Dict[str, Any]:
        """Makes a request to get available money

        Returns:
            dict: Dictionary with available money in the following settlements dates
        """
        return self.api_request(urls.endpoints["buying_power"])

    def get_selling_power(self, long_ticker: str) -> Dict[str, Any]:
        """Makes a request to get available stocks for selling

        Args:
            long_ticker (str): Long ticker of the instrument

        Returns:
            dict: Dictionary with available stocks in the following settlement dates
        """
        return self.api_request(urls.endpoints["selling_power"].format(long_ticker))

    def get_dolar_mep(self) -> Dict[str, Any]:
        """Makes a request to get bot's dolar mep quotes

        Returns:
            dict: Dictionary with quotes and additional info
        """
        return self.api_request(urls.endpoints["new_dolar_mep"])

    def get_open_dolar_mep(self) -> Dict[str, Any]:
        """Makes a request to get bot's dolar mep quotes

        Returns:
            dict: Dictionary with quotes and additional info
        """
        return self.api_request(urls.endpoints["open_dolar_mep"])

    def get_home_list(self) -> Dict[str, Any]:
        """Makes a request to get Home page quote list

        Returns:
            list: List of homepage quotes
        """
        return self.api_request(urls.endpoints["home_list"])

    def get_my_list(self) -> Dict[str, Any]:
        """Makes a request to get favorite quote list

        Returns:
            list: List of favorite quotes
        """
        return self.api_request(urls.endpoints["my_list"])

    def get_tickers_list(
        self,
        instrument_type: str,
        instrumet_subtype: str,
        settlement: str,
        currency: str,
        segment: str,
    ) -> List[Dict[str, Any]]:
        """Makes a request to get instruments quote list information filtered by instrument type and subtype

        Args:
            instrument_type (str): Type of instruments
            instrument_subtype (str): Subtype of instruments
            settlement_date (str): Settlement date of instruments
            currency (str): Currency of instruments
            segment (str): Segment of instruments

        Returns:
            list: List of instruments quotes
        """
        return self.api_request(
            urls.endpoints["tickers_list"].format(
                instrument_type.value,
                instrumet_subtype.value,
                settlement.value,
                currency.value,
                segment.value,
            )
        )

    def get_tickers_pagination(
        self,
        instrument_type: str,
        instrument_subtype: str,
        settlement: str,
        currency: str,
        segment: str,
        page_number: int,
        page_size: int,
    ) -> Dict[str, Any]:
        """Makes a request to get instruments a paginated quote list information filtered by instrument type and subtype

        Args:
            instrument_type (str): Type of instruments
            instrument_subtype (str): Subtype of instruments
            settlement_date (str): Settlement date of instruments
            currency (str): Currency of instruments
            segment (str): Segment of instruments
            page_number (str): page number
            page_size (str): items per page

        Returns:
            list: List of instruments quotes
        """
        return self.api_request(
            urls.endpoints["tickers_pagination"].format(
                instrument_type,
                instrument_subtype,
                settlement,
                currency,
                segment,
                page_number,
                page_size,
            )
        )

    def get_historic_data(self, long_ticker: str, date_from: str) -> Dict[str, Any]:
        """Makes a request to get daily close price for a given instrument and range.

        Args:
            long_ticker (str): Long ticker of the instrument
            date_from (str): Start date. Format yyyy-MM-dd

        Returns:
            list: List of closing prices
        """
        return self.api_request(
            urls.endpoints["historic_data"].format(long_ticker, date_from)
        )

    def get_tickers(self, ticker: str, segment: str) -> List[Dict[str, Any]]:
        """Makes a request to get every possible long ticker combination for a given short ticker

        Args:
            ticker (str): short ticker. Example: AL30
            segment (Segments (Enum)): Segment of the instrument

        Returns:
            list: List of long tickers for the same short ticker
        """
        return self.api_request(urls.endpoints["tickers"].format(ticker, segment))

    def search_tickers(self, ticker: str) -> List[Dict[str, Any]]:
        """Makes a request to search tickers

        Args:
            ticker (str): Query of the search

        Returns:
            list: List of possible tickers
        """
        return self.api_request(urls.endpoints["tickers_search"].format(ticker))

    def get_instrument_rules(self) -> Dict[str, Any]:
        """Makes a request to get BYMA price rules

        Returns:
            list: List of rules for specific instruments price ranges
        """
        return self.api_request(urls.endpoints["rules"])

    def get_instrument_types(self) -> List[Dict[str, Any]]:
        """Makes a request to get types of instruments lists

        Returns:
            list: List of Types and Subtypes of available instruments
        """
        return self.api_request(urls.endpoints["types"])

    #####################
    ###    HELPERS    ###
    #####################

    def api_request(
        self,
        path: str,
        retry: bool = True,
        method: str = "get",
        params: str = "",
        json_data: Dict[str, Any] = {},
        data: str = "",
    ):
        response = None

        if method not in ["get", "post", "delete"]:
            raise ApiException(f"Method {method} not suported")
        if method == "get":
            response = self.session.get(self._api_url(path))

        if method == "post":
            response = self.session.post(
                self._api_url(path),
                params=params,
                data=data,
                json=json_data,
            )

        if method == "delete":
            response = self.session.delete(self._api_url(path), json=json_data)

        if not response:
            raise ApiException("Bad HTTP API Response")

        json_response = simplejson.loads(response.text)

        if response.status_code == 401:
            if retry:
                self.api_request(path, retry=False)
            else:
                raise ApiException("Authentication Fails.")

        if response.status_code == 500:
            raise ApiException(f"Error 500 {json_response}")

        if response.status_code == 200:
            self._log_message(path, str(json_response))
        return json_response

    def update_session_headers(self, header_update: Dict[str, Any]) -> None:
        self.session.headers.update(header_update)

    def _api_url(self, path: str) -> str:
        return urls.api_url + path

    def _log_message(self, url: str, message: str) -> None:
        msg: Dict[str, str] = {
            "url": url,
            "timestamp": self._get_timestamp_string(),
            "message": message,
        }
        self.messages.append(msg)

    def _get_timestamp_string(self) -> str:
        return datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
