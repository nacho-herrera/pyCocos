# -*- coding: utf-8 -*-
"""
    pyCocos.main
    Main client.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
import pyotp
import json

from .components import (
    ApiException,
    Currency,
    InstrumentSubType,
    InstrumentType,
    OrderSide,
    OrderType,
    PerformanceTimeframe,
    RestClient,
    Segment,
    Settlement,
)


class Cocos:
    headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Content-Type": "application/json",
    }

    def __init__(self, email: str, password: str, gotrue_meta_security: Optional[Dict[str, Any]] = {}, api_key: Optional[str] = None, topt_secret_key: Optional[str] = None) -> None:
        ## Parameters validation
        required_fields: list[tuple[str, Any, Any]]  = [
            ("email", email, str),
            ("password", password, str),
            ("gotrue_meta_security", gotrue_meta_security, dict),
        ]
        self._check_fields(required_fields)

        ## REST Client
        self.client: RestClient = RestClient()

        ## Enums as instance variables
        self.currencies = Currency
        self.instrument_types = InstrumentType
        self.instrument_subtypes = InstrumentSubType
        self.order_sides = OrderSide
        self.order_types = OrderType
        self.performance_timeframes = PerformanceTimeframe
        self.segments = Segment
        self.settlements = Settlement

        ## Login Information
        self.email: str = email
        self.password: str = password
        self.gotrue_meta_security: Dict[str, Any] = gotrue_meta_security
        #self.recaptcha_token: str = recaptcha_token
        self.account_number: str = ""

        if topt_secret_key:
            self.topt = pyotp.TOTP(topt_secret_key)
        else:
            self.topt = None

        if not api_key: 
            self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzA0NjgyODAwLAogICJleHAiOiAxODYyNTM1NjAwCn0.f0w62k0q0eyyGBDkAP7vUUEg_Ingb9YbOlhsGCC4R3c"  # Working apikey from main JS File - 2024-02-05.
        else:
            self.api_key = api_key
                
        ## Current session variables # ! NEEDS TO BE DEVELOPED
        self.orders: List[str] = []
        self.connected: bool = False
        
        self.headers = {
            "Apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}"
        }

        ## Finally, tries to authenticate
        self._auth()

    def _auth(self) -> None:
        """Calls the Cocos API method to get an access token and updates the session headers.

        This method is responsible for authenticating the user by obtaining an access token from the Cocos API.
        It then updates the session headers with the obtained token for subsequent API requests.

        Raises:
            Exception: If there is an error during the authentication process.
            Exception: If the access token is not found in the API response.
        """
        params = "grant_type=password"
        payload: str = json.dumps({"email": self.email, "password": self.password, "gotrue_meta_security": self.gotrue_meta_security})
        self.client.update_session_headers(self.headers)

        response: Dict[str, Any] = self.client.get_token(params=params, data=payload)

        if "success" in response.keys() and response["success"] == False:
            raise Exception(f'Error: {response["message"]}')

        if "access_token" not in response.keys():
            raise Exception("Error: Access token not found in the API response")

        self.access_token = response["access_token"]
        self._2fa_challenge()

    def _2fa_challenge(self) -> None:
        headers_update: dict[str, str] = {
            "apikey": self.api_key,
            "authorization": f"Bearer {self.access_token}",
        }
        
        self.client.update_session_headers(headers_update)
        second_factor_response = self.client.get_2factors()
        if "requireChallenge" in second_factor_response.keys() and second_factor_response["requireChallenge"]:
            challenge_id = second_factor_response["id"]
        
        payload = json.dumps({
            "expires_at": 123, 
            "id": challenge_id,
        })

        challenge = self.client.submit_challenge_request(challenge_id=challenge_id)
        
        if challenge_id not in ["mail", "sms"] and self.topt is not None:
            code = self.topt.now()
        else:
            code = input("Insert 2FA Code: ")
        payload = {
            "challenge_id": "_",
            "code": code,
        }
        
        #self.client.update_session_headers(headers_update)        
        response = self.client.submit_challenge_verification(challenge_id=challenge_id, json=payload)

        if "access_token" not in response.keys():
            raise Exception("Error: Access token not found in the API response")
        else:
            self.access_token = response["access_token"]
            self._auth_phase_2()

    def _auth_phase_2(self) -> None:
        """Updates the session headers and performs additional steps after login.

        After successful login and obtaining the access token, this method is responsible for updating the session headers
        with the necessary authentication information. It replicates the workflow of the web app.

        """

        headers_update: dict[str, str] = {
            "apikey": "",
            "authorization": f"Bearer {self.access_token}",
            #"recaptcha-token": self.recaptcha_token,
            "x-account-id": self.account_number,
        }
        
        self.client.update_session_headers(headers_update)

        self.my_account_info: Dict[str, Any] = self.my_data()
        account_number = str(self.my_account_info["id_accounts"][0])
        self._update_account_number(account_number)

        self.client.update_session_headers({"x-account-id": self.account_number})
        self.connected = True

    def logout(self) -> None:
        """Logs out from the broker API.

        This method performs the logout operation on the broker API, ending the session and invalidating the authentication token.

        After calling this method, the instance will be disconnected from the API.

        Note: Make sure to handle any additional cleanup or resource release operations, if required, after calling this method.
        """
        self.client.logout()
        self.connected = False

    ###############
    ## PORTFOLIO ##
    ###############

    def my_data(self) -> Dict[str, Any]:
        """Retrieves the personal information of the account owner.

        This method calls the API to fetch the personal information associated with the account owner.

        Returns:
            Dict[str, Any]: A dictionary containing the account owner's personal information.

        Note:
            The returned dictionary may include details such as name, email, contact information, and other relevant data.

        Raises:
            Exception: If there is an error while retrieving the account owner's personal information.
        """
        return self.client.get_my_data()

    def my_bank_accounts(self) -> List[Dict[str, Any]]:
        """Retrieves the registered bank accounts associated with the account.

        This method calls the API to fetch the bank accounts registered for the account.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents a registered bank account.

        Note:
            Each bank account dictionary may contain details such as account number, bank name, account currency, and other relevant information.

        Raises:
            Exception: If there is an error while retrieving the registered bank accounts.
        """
        return self.client.get_bank_accounts()

    def my_portfolio(self) -> Dict[str, Any]:
        """Retrieves the portfolio information associated with the account.

        This method calls the API to fetch the portfolio information, including the holdings and market valuation of the account.

        Returns:
            Dict[str, Any]: A dictionary containing the portfolio information.

        Note:
            The returned dictionary may include details such as the list of holdings, their quantities, market values, and other relevant data.

        Raises:
            Exception: If there is an error while retrieving the portfolio information.
        """
        response: Dict[str, Any] = self.client.get_portfolio()
        return response

    def funds_available(self) -> Dict[str, Dict[str, float]]:
        """Retrieves the available funds for trading in T+0, T+1, and T+2 settlement dates.

        This method calls the API to fetch the available funds that can be used for trading on different settlement dates.

        Returns:
            Dict[str, Dict[str, float]: A dictionary containing the available funds for each settlement date.

        Note:
            The returned dictionary contains key-value pairs, where the keys represent the settlement dates (e.g., T+0, T+1, T+2),
            and the values represent the corresponding available funds as floating-point numbers.

        Raises:
            Exception: If there is an error while retrieving the available funds.
        """
        return self.client.get_buying_power()

    def stocks_available(self, long_ticker: str) -> Dict[str, int]:
        """Retrieves the available quantity of a stock that can be traded.

        This method calls the API to fetch the available quantity of a specific stock that can be traded.

        Args:
            long_ticker (str): The long ticker of the stock to check.

        Returns:
            Dict[str, int]: A dictionary containing the available quantity of the stock for trading.

        Note:
            The returned dictionary may include the available quantity of the stock as an integer value.

        Raises:
            Exception: If there is an error while retrieving the available quantity of the stock.
        """

        # Parameters validation
        required_fields: list[tuple[str, Any, Any]]  = [("long_ticker", long_ticker, str)]
        self._check_fields(required_fields)

        return self.client.get_selling_power(long_ticker)

    def account_activity(self, date_from: str, date_to: str) -> List[Dict[str, Any]]:
        """Retrieves the account funds activity for a given period of time.

        This method calls the API to fetch the account funds activity information, such as deposits, withdrawals,
        and other relevant transactions that occurred within the specified date range.

        Args:
            date_from (str): The start date of the period (format: YYYY-MM-DD).
            date_to (str): The end date of the period (format: YYYY-MM-DD).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the account funds activity information.

        Note:
            Each dictionary in the list represents a specific transaction or activity, with its associated details.

        Raises:
            Exception: If there is an error while retrieving the account funds activity.
        """

        # Parameters validation
        required_fields: list[tuple[str, Any, Any]]  = [("date_from", date_from, str), ("date_to", date_to, str)]

        self._check_fields(required_fields)

        return self.client.get_account_movements(date_from, date_to)

    def portfolio_performance(
        self, timeframe: PerformanceTimeframe, date_from: str = "", date_to: str = ""
    ) -> Dict[str, Any]:
        """Retrieves the portfolio performance statistics based on the specified timeframe.

        This method calls the API to fetch the portfolio performance statistics, such as returns, gains, and losses,
        for a given timeframe.

        Args:
            timeframe (PerformanceTimeframes): The type of report to retrieve. Possible values are 'daily', 'historical',
                and 'range'.
            date_from (str, optional): Only for the 'range' timeframe. The start date of the period (format: YYYY-MM-DD).
                Defaults to an empty string.
            date_to (str, optional): Only for the 'range' timeframe. The end date of the period (format: YYYY-MM-DD).
                Defaults to an empty string.

        Returns:
            Dict[str, Any]: A dictionary containing the portfolio performance statistics for the specified timeframe.

        Raises:
            Exception: If there is an error while retrieving the portfolio performance.

        Note:
            - For the 'daily' timeframe, the returned dictionary includes the performance statistics for the latest day.
            - For the 'historical' timeframe, the returned dictionary includes the performance statistics for a historical
                period, typically covering multiple days.
            - For the 'range' timeframe, the returned dictionary includes the performance statistics for a specific range of
                dates, as defined by the 'date_from' and 'date_to' arguments.

        """

        # Parameters validation
        required_fields: list[tuple[str, Any, Any]]  = [("timeframe", timeframe, PerformanceTimeframe)]
        self._check_fields(required_fields)

        if timeframe != self.performance_timeframes.RANGE:
            return self.client.get_daily_performance()
        else:
            return self.client.get_performance_period(date_from, date_to)

    def submit_new_bank_account(
        self, cbu: str, cuit: str, currency: Currency
    ) -> Dict[str, Any]:
        """Submits a request to add a new bank account through the API.

        This method sends a request to add a new bank account to the user's profile. The account is associated with the
        provided CBU/CVU and CUIT, and is specified in the specified currency.

        Args:
            cbu (str): The CBU/CVU of the new bank account.
            cuit (str): The CUIT (tax identification number) of the account owner.
            currency (Currency): The currency of the new bank account.

        Returns:
            Dict[str, Any]: A dictionary containing the response from the API.

        Raises:
            Exception: If there is an error while submitting the new bank account.

        """

        # Parameters validation
        required_fields: list[tuple[str, Any, Any]]  = [
            ("cbu_cvu", cbu, str),
            ("cuit", cuit, str),
            ("currency", currency, Currency),
        ]
        self._check_fields(required_fields)

        # Create payload object
        payload: str = json.dumps(
            {"cbu_cvu": cbu, "cuit": cuit, "currency": currency.value}
        )
        response: Dict[str, Any] = self.client.submit_new_bank_account(data=payload)
        return response

    def withdraw_funds(
        self, currency: Currency, amount: str, cbu_cvu: str
    ) -> Dict[str, Any]:
        """Submits a request to withdraw funds through the API.

        This method sends a request to withdraw funds from the user's account. The specified amount of funds in the given
        currency will be transferred to the provided bank account (CBU/CVU).

        Args:
            currency (Currency): The currency of the funds to withdraw.
            amount (str): The amount of funds to withdraw.
            cbu_cvu (str): The bank account (CBU/CVU) to transfer the funds to.

        Raises:
            ApiException: If the specified bank account is not available. Please add it to your account.

        Returns:
            Dict[str, Any]: A dictionary containing the response from the API.

        """

        # Parameters validation
        required_fields: list[tuple[str, Any, Any]]  = [
            ("currency", currency, Currency),
            ("amount", amount, str),
            ("cbu_cvu", cbu_cvu, str),
        ]
        self._check_fields(required_fields)

        # Check if the specified bank account exists
        if not self._check_cbu_cvu_exists(cbu_cvu_to_check=cbu_cvu):
            raise ApiException(
                f"Invalid account, {cbu_cvu} not found. Add account first."
            )

        # Create payload object
        payload = json.dumps(
            {
                "order": "1",
                "amount": amount,
                "currency": currency.value,
                "cbu_cvu": cbu_cvu,
            }
        )

        response = self.client.submit_funds_withdraw(data=payload)
        return response

    ############
    ## ORDERS ##
    ############

    def submit_buy_order(
        self,
        long_ticker: str,
        order_type: OrderType = OrderType.LIMIT,
        **kwargs: Dict[str, str]
    ) -> Dict[str, Any]:
        """Submits a buy order through the API.

        This method sends a request to place a buy order for a specific instrument. The order includes the long ticker
        of the instrument, the quantity to buy, the price at which to buy, and the order type (limit or market).

        Args:
            long_ticker (str): The long ticker of the instrument to buy.
            order_type (OrderTypes, optional): The type of order (limit or market). Defaults to OrderTypes.LIMIT.
            quantity (str): The quantity of the buy order.
            price (str): The price of the buy order.
            amount (float): The amount to pay for the buy order

        Returns:
            Dict[str, Any]: A dictionary containing the response from the API, including the new order ID.
        """

        # Create basic payload object
        payload: Dict[str, str] = {
            "long_ticker": long_ticker,
            "side": self.order_sides.BUY.value,
            "type": order_type.value
        }
        
        # create basic parameters validation list
        required_fields: list[tuple[str, Any, Any]] = [
            ("long_ticker", long_ticker, str),
            ("order_type", order_type, OrderType),
        ]

        # Add order parameters to payload object and validation list
        for k, v in kwargs.items():
            payload[k] = v
            required_fields.append((k, v ,str))                       

        # Validate all parameters
        self._check_fields(required_fields)

        # Check if account has enough money to purchase
        if not self._validate_buy_order(payload):
            raise ApiException(f"Not enough money to purchase")

        response: Dict[str, Any] = self.client.submit_order(json=payload)
        if "success" in response.keys():
            self._add_order(response["Orden"])
        return response

    def submit_sell_order(
        self,
        long_ticker: str,
        quantity: str,
        price: str,
        order_type: OrderType = OrderType.LIMIT,
    ) -> Dict[str, Any]:
        """Submits a sell order through the API.

        This method sends a request to place a sell order for a specific instrument. The order includes the long ticker
        of the instrument, the quantity to sell, the price at which to sell, and the order type (limit or market).

        Args:
            long_ticker (str): The long ticker of the instrument to sell.
            quantity (str): The quantity of the sell order.
            price (str): The price of the sell order.
            order_type (OrderTypes, optional): The type of order (limit or market). Defaults to OrderTypes.LIMIT.

        Returns:
            Dict[str, Any]: A dictionary containing the response from the API, including the new order ID.
        """
        ## Parameters validation
        required_fields: list[tuple[str, Any, Any]]  = [
            ("long_ticker", long_ticker, str),
            ("quantity", quantity, str),
            ("price", price, str),
            ("order_type", order_type, OrderType),
        ]
        self._check_fields(required_fields)

        # Check if account has enough stocks to sell
        if not self._validate_sell_power(long_ticker, quantity):
            raise ApiException(f"Not enough stocks to sell")

        ## Create Payload object
        payload: Dict[str, str] = {
            "type": order_type.value,
            "side": self.order_sides.SELL.value,
            "quantity": quantity,
            "long_ticker": long_ticker,
            "price": price,
        }

        response: Dict[str, Any] = self.client.submit_order(json=payload)
        return response

    def place_repo_order(
        self, currency: Currency, amount: float, term: int, rate: float
    ) -> Dict[str, Any]:
        """Submits a repo order through the API.

        This method sends a request to submit a repo order, which involves lending funds for a specified term and at a
        specified interest rate. The order includes the currency of the funds, the amount to be repo, the term of the repo,
        and the rate of the repo.

        Args:
            currency (Currency): The currency of the order.
            amount (float): The amount of funds to be repo.
            term (int): The term of the repo in days.
            rate (float): The interest rate of the repo.

        Returns:
            Dict[str, Any]: A dictionary containing the response from the API, including the order ID.

        """

        # Parameters validation
        required_fields: list[tuple[str, Any, Any]]  = [
            ("currency", currency, Currency),
            ("amount", amount, float),
            ("term", term, int),
            ("rate", rate, float),
        ]
        self._check_fields(required_fields)

        # Create payload object
        payload: str = json.dumps(
            {
                "currency": currency.value,
                "amount": amount,
                "term": term,
                "rate": rate,
            }
        )

        response: Dict[str, Any] = self.client.submit_repo_order(data=payload)
        return response

    def cancel_order(self, order_number: str) -> Dict[str, Any]:
        """Cancels an existing order through the API.

        This method sends a request to cancel a previously submitted order identified by its order number. The order will be
        cancelled, and the API response will provide information about the cancellation status.

        Args:
            order_number (str): The order number of the order to cancel.

        Returns:
            Dict[str, Any]: A dictionary containing the response from the API regarding the cancellation.

        """

        # Parameters validation
        required_fields: list[tuple[str, Any, Any]]  = [("order_number", order_number, str)]
        self._check_fields(required_fields)

        # Retrieve order information
        order: Dict[str, Any] = self.order_status(order_number)  # type: ignore

        # Create payload object
        payload: str = json.dumps(
            {"instrument": order["instrument"], "ticker": order["ticker"]}
        )

        response: Dict[str, Any] = self.client.cancel_order(order_number, data=payload)
        return response

    def order_status(
        self, order_number: str = ""
    ) -> Dict[str, Any] | List[Dict[str, Any]]:
        """Calls the API to retrieve order status information.

        This method retrieves the status information of one or more orders from the API. If an `order_number` is provided,
        it returns the status of the specific order. If no `order_number` is provided, it returns the status of all orders.

        Args:
            order_number (str, optional): The order number of the specific order to retrieve the status for.
                If not provided, the status of all orders will be returned. Defaults to "".

        Returns:
            Dict[str, Any]: A dictionary containing the response from the API with the order status information.

        """

        # Parameters validation
        required_fields: list[tuple[str, Any, Any]]  = [("order_number", order_number, str)]
        self._check_fields(required_fields)

        if order_number:
            return self.client.get_order(order_number)
        else:
            return self.client.get_orders()

    #################
    ## INSTRUMENTS  ##
    #################

    def get_daily_history(self, long_ticker: str, date_from: str) -> Dict[str, Any]:
        """Calls the API to retrieve historical price data for a given long ticker.

        This method retrieves the historical price data for a specified long ticker starting from a given date.

        Args:
            long_ticker (str): The full ticker name to retrieve the historical price data for.
            date_from (str): The starting date to retrieve the historical price data in the format "YYYY-MM-DD".

        Returns:
            Dict[str, Any]: A dictionary containing the response from the API with the historical price data for the ticker.

        """

        # Parameters validation
        required_fields: list[tuple[str, Any, Any]]  = [
            ("long_ticker", long_ticker, str),
            ("date_from", date_from, str),
        ]
        self._check_fields(required_fields)

        return self.client.get_historic_data(long_ticker, date_from)

    def get_instrument_snapshot(
        self, ticker: str, segment: Segment
    ) -> List[Dict[str, Any]]:
        """Calls the API to retrieve a snapshot of price data for a given ticker.

        This method retrieves the snapshot price data for a specified ticker in a specific segment.

        Args:
            ticker (str): The ticker symbol to retrieve the price data for.
            segment (Segment): The segment of the ticker.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the snapshot price data for all possible settlement dates of the ticker.

        """

        # Parameters validation
        required_fields: list[tuple[str, Any, Any]]  = [
            ("ticker", ticker, str),
            ("segment", segment, Segment),
        ]
        self._check_fields(required_fields)

        return self.client.get_tickers(ticker, segment.value)

    def get_instrument_list_snapshot(
        self,
        instrument_type: InstrumentType,
        instrument_subtype: InstrumentSubType,
        settlement: Settlement,
        currency: Currency,
        segment: Segment,
    ) -> List[Dict[str, Any]]:
        """Calls the API to retrieve a list of instruments based on specified criteria.

        This method retrieves a list of instruments based on the provided instrument type, instrument subtype,
        settlement, currency, and segment.

        Args:
            instrument_type (InstrumentType): The category type of the instruments.
            instrument_subtype (InstrumentSubType): The category subtype of the instruments.
            settlement (Settlements): The settlement type for the instruments.
            currency (Currency): The currency for the instruments.
            segment (Segment): The segment for the instruments.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the instrument information for the selected instruments.

        Raises:
            ValueError: If the combination of instrument type and subtype is invalid. Refer to the instrument_types_and_subtypes method.

        """

        # Parameters validation
        required_fields: list[tuple[str, Any, Any]]  = [
            ("instrument_type", instrument_type, InstrumentType),
            ("instrument_subtype", instrument_subtype, InstrumentSubType),
            ("settlement", settlement, Settlement),
            ("currency", currency, Currency),
            ("segment", segment, Segment),
        ]
        self._check_fields(required_fields)

        if not self._validate_list_parameters(
            instrument_type.value, instrument_subtype.value
        ):
            raise ValueError(
                "Invalid combination for instrument type and subtype. Check instrument_types_and_subtypes method."
            )

        return self.client.get_tickers_list(
            instrument_type.value,
            instrument_subtype.value,
            settlement.value,
            currency.value,
            segment.value,
        )

    def get_instrument_list_snapshot_paginated(
        self,
        instrument_type: InstrumentType,
        instrument_subtype: InstrumentSubType,
        settlement: Settlement,
        currency: Currency,
        segment: Segment,
        page: int,
        size: int,
    ) -> Dict[str, Any]:
        """Calls the API to retrieve a paginated list of instruments based on specified criteria.

        This method retrieves a paginated list of instruments based on the provided instrument type, instrument subtype,
        settlement, currency, segment, page number, and items per page.

        Args:
            instrument_type (InstrumentType): The category type of the instruments.
            instrument_subtype (InstrumentSubType): The category subtype of the instruments.
            settlement (Settlement): The settlement type for the instruments.
            currency (Currency): The currency for the instruments.
            segment (Segment): The segment for the instruments.
            page (int): The page number to retrieve.
            size (int): The number of items per page.

        Returns:
            Dict[str, Any]: A dictionary containing the paginated list of selected instruments.

        Raises:
            ValueError: If the combination of instrument type and subtype is invalid. Refer to the instrument_types_and_subtypes method.

        """
        raise ApiException("Disabled endpoint.")
        ## Parameters validation
        #required_fields: list[tuple[str, Any, Any]]  = [
        #    ("instrument_type", instrument_type, InstrumentType),
        #    ("instrument_subtype", instrument_subtype, InstrumentSubType),
        #    ("settlement", settlement, Settlement),
        #    ("currency", currency, Currency),
        #    ("segment", segment, Segment),
        #    ("page", page, int),
        #    ("size", size, int),
        #]
        #self._check_fields(required_fields)
        #
        #if not self._validate_list_parameters(
        #    instrument_type.value, instrument_subtype.value
        #):
        #    raise ValueError(
        #        "Invalid combination for instrument type and subtype. Check instrument_types_and_subtypes method."
        #    )
        #
        #return self.client.get_tickers_pagination(
        #    instrument_type.value,
        #    instrument_subtype.value,
        #    settlement.value,
        #    currency.value,
        #    segment.value,
        #    page,
        #    size,
        #)

    def get_recommended_tickers(self) -> Dict[str, Any]:
        """Calls the API to retrieve the list of recommended tickers from the home page.

        This method retrieves the list of recommended tickers provided on the home page of the application.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the recommended tickers.

        Note:
            The structure and content of the returned list may vary depending on the API response. Each dictionary in the list
            represents a recommended ticker and may contain different fields such as ticker symbol, company name, price, etc.

        """
        raise ApiException("Disabled endpoint.")
        #return self.client.get_home_list()

    def get_favorites_tickers(self) -> Dict[str, Any]:
        """Calls the API to retrieve the list of favorite instruments from the home page.

        This method retrieves the list of favorite instruments that have been saved by the user on the home page of the application.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the favorite instruments.

        Note:
            The structure and content of the returned list may vary depending on the API response. Each dictionary in the list
            represents a favorite instrument and may contain different fields such as ticker symbol, company name, price, etc.

        """
        raise ApiException("Disabled endpoint.")
        #return self.client.get_my_list()

    def search_ticker(self, query: str) -> List[Dict[str, Any]]:
        """Calls the API to search for a ticker by name.

        This method allows searching for a ticker by providing a query string representing the name or part of the name of the ticker.
        The API will return the search results matching the query.

        Args:
            query (str): The query string representing the ticker name to search.

        Returns:
            List[Dict[str, Any]]: The API response with the search results.

        Raises:
            ValueError: If the query string is less than 2 characters long.

        Note:
            The structure and content of the returned dictionary may vary depending on the API response.

        """

        ## Parameters validation
        required_fields: list[tuple[str, Any, Any]]  = [("query", query, str)]
        self._check_fields(required_fields)

        if len(query) < 2:
            raise ValueError("Query must be at least 2 characters long")
        return self.client.search_tickers(query)

    #################
    ## MARKET INFO ##
    #################

    def market_status(self) -> Dict[str, Any]:
        """Calls the API to retrieve the status of the different markets available.

        This method retrieves the status of the markets, providing information about whether they are open or closed.

        Returns:
            Dict[str, Any]: The API response with the status of the markets.

        Note:
            The structure and content of the returned dictionary may vary depending on the API response.

        """

        return self.client.get_market_status()

    def instruments_rules(self) -> Dict[str, Any]:
        """Calls the API to retrieve the rules for different instruments.

        This method retrieves the rules associated with various instruments, providing information on
        trading rules, margin requirements, order types, and other relevant specifications.

        Returns:
            Dict[str, Any]: The API response with the instrument rules.

        Note:
            The structure and content of the returned dictionary may vary depending on the API response.

        """

        return self.client.get_instrument_rules()

    def instrument_types_and_subtypes(self) -> List[Dict[str, Any]]:
        """Calls the API to retrieve the types and subtypes of available instruments.

        This method retrieves information about the different types and subtypes of instruments
        available for trading. It provides a comprehensive list of instrument categories and their
        corresponding subcategories.

        Returns:
            Dict[str, Any]: The API response with the instrument types and subtypes.

        Note:
            The structure and content of the returned dictionary may vary depending on the API response.

        """
        raise ApiException("Disabled endpoint.")
        #return self.client.get_instrument_types()

    @property
    def allowed_combinations(self) -> List[Tuple[str, str]]:
        """Returns the allowed combinations of instrument types and subtypes.

        This property retrieves the allowed combinations of instrument types and subtypes
        based on the available instrument categories and subcategories. It utilizes the
        `instrument_types_and_subtypes` method to fetch the information and constructs a list
        of tuples representing the allowed combinations.

        Returns:
            List[Tuple[str, str]]: A list of tuples representing the allowed combinations
            of instrument types and subtypes.

        Note:
            The structure and content of the returned list may vary depending on the API response
            from the `instrument_types_and_subtypes` method. Each tuple in the list consists of
            two strings: the instrument type and the instrument subtype.

        """

        #return [
        #    (_["instrument_type"], _["instrument_subtype"])
        #    for _ in self.instrument_types_and_subtypes()
        #]
        combinations = [
            ("ACCIONES", "LIDERES"),
            ("ACCIONES", "GENERAL"), 
            ("CEDEARS", "TOP"),
            ("CEDEARS", "ETF"),
            ("CEDEARS", "NUEVOS"),
            ("CEDEARS", "OTROS"),
            ("BONOS_PUBLICOS", "NACIONALES_USD"),
            ("BONOS_PUBLICOS", "NACIONALES_ARS"),
            ("BONOS_PUBLICOS", "PROVINCIALES"),
            ("BONOS_CORP", "TOP"),
            ("LETRAS", "TASA_FIJA"),
            ("LETRAS", "CER"),
            ("FCI", "PF")
            ]
        return combinations

    ###############
    ## DOLAR MEP ##
    ###############

    def get_dolar_mep_info(self) -> Dict[str, Any]:
        """Calls API to retrieve the current value of the Closed "Dólar MEP" exchange rate.

        The "Dólar MEP" is an exchange rate used in Argentina for the conversion of local currency
        to US dollars through electronic payment systems. This method calls the API to fetch the
        current value of the "Dólar MEP" exchange rate.

        According actual regulations, you can not buy and sell instruments on the same day, so you have some price risk until you finish both operations.
        Cocos Capital has a special Dolar Mep (closed price) venue with a warranted price.

        Returns:
            Dict[str, Any]: API Response with the current value of the "Dólar MEP" exchange rate.

        Note:
            The structure and content of the returned dictionary may vary depending on the API response.

        """

        return self.client.get_dolar_mep()

    def get_open_dolar_mep_info(self) -> Dict[str, Any]:
        """Calls API to retrieve the opening value of the "Dólar MEP" exchange rate.

        The "Dólar MEP" is an exchange rate used in Argentina for the conversion of local currency
        to US dollars through electronic payment systems. This method calls the API to fetch the
        opening value of the "Dólar MEP" exchange rate.

        Returns:
            Dict[str, Any]: API Response with the opening value of the "Dólar MEP" exchange rate.

        Note:
            The structure and content of the returned dictionary may vary depending on the API response.

        """
        raise ApiException("Disabled endpoint.")
        #return self.client.get_open_dolar_mep()

    ##########
    ## MISC ##
    ##########

    def get_ads_carrousel(self) -> List[Dict[str, Any]]:
        """Calls API to retrieve the carousel ads.

        The carousel ads are a collection of advertisements displayed in a carousel format.
        This method calls the API to fetch the carousel ads.

        Returns:
            Dict[str, Any]: API Response with the carousel ads.

        Note:
            The structure and content of the returned dictionary may vary depending on the API response.

        """
        raise ApiException("Disabled endpoint.")
        #return self.client.get_carrousel()

    def get_news(self) -> List[Dict[str, Any]]:
        """Calls API to retrieve news articles.

        This method calls the API to fetch the latest news articles. The returned news articles
        can contain information about various topics such as finance, economy, market updates, etc.

        Returns:
            Dict[str, Any]: API Response with the news articles.

        Note:
            The structure and content of the returned dictionary may vary depending on the API response.

        """
        raise ApiException("Disabled endpoint.")
        #return self.client.get_news()

    def get_cocos_university_articles(self) -> List[Dict[str, Any]]:
        """Calls API to retrieve articles from Cocos University.

        This method calls the API to fetch articles from Cocos University, which provides educational content
        related to finance, investing, trading, and other relevant topics. The articles aim to educate and
        inform users about various aspects of the financial industry.

        Returns:
            Dict[str, Any]: API Response with the articles from Cocos University.

        Note:
            The structure and content of the returned dictionary may vary depending on the API response.

        """

        return self.client.get_university()

    #############
    ## HELPERS ##
    #############

    def long_ticker(
        self,
        ticker: str,
        settlement: Settlement,
        currency: Currency,
        segment: Segment = Segment.DEFAULT,
    ) -> str:
        """
        Helper function to create a long ticker based on the ticker, settlement, segment, and currency.
        It does not validate the segment against valid ticker and segment combinations.
        If you're unsure, it's recommended to use the `search_instrument` method to validate.

        Args:
            ticker (str): Ticker symbol of the instrument.
            settlement (Settlements): Settlement date of the instrument.
            currency (Currency): Currency of the instrument.
            segment (Segment, optional): Segment of the instrument. Defaults to Segment.DEFAULT.

        Returns:
            str: The long ticker representing the ticker and settlement date.

        Notes:
            - The `segment` argument is not validated against valid ticker and segment combinations.
            It's important to ensure the appropriate segment is provided.
            - The long ticker format follows the pattern: "<TICKER>-<SETTLEMENT>-<SEGMENT>-<VENUE>-<CURRENCY>",
            where:
                - <TICKER> represents the ticker symbol in uppercase.
                - <SETTLEMENT> is a code representing the settlement date (e.g., "0001" for T0).
                - <SEGMENT> is the segment of the instrument.
                - <VENUE> indicates the BYMA market venue (e.g., "CT" for Price/Time Priority).
                - <CURRENCY> represents the currency code.

        Examples:
            long_ticker("AAPL", Settlements.T2, Currency.PESOS) returns "AAPL-0003-C-CT-ARS"
            long_ticker("GOOGD", Settlements.T0, Currency.USD) returns "GOOGD-0001-C-CT-USD"
            long_ticker("GFGC500.JU", Settlements.T1, Currency.PESOS, Segment.OPTIONS) returns "GFGC500.JU-0002-O-CT-ARS"

        """

        if segment is Segment.FCI:
            return ticker.upper()

        _settlement: str = self._get_byma_settlement(settlement)
        _currency: str = self._get_byma_currency(currency)

        return f"{ticker.upper()}-{_settlement}-{segment.value}-CT-{_currency}"

    def _validate_buy_order(self, payload: Dict[str, str]) -> bool:
        """
        Validates if there are sufficient funds available to place a buy order.

        Args:
            payload (Dict[str, str]): The payload to validate.

        Returns:
            bool: True if there are sufficient funds, False otherwise.
        """
        long_ticker: str = payload['long_ticker']
        instrument_code, settlement, segment, _, currency = long_ticker.split("-")
        
        #instrument_code = self._find_instrument_code(long_ticker)
        settlement = self._get_cocos_settlement(settlement)
        segment = self._get_cocos_segment(segment)
        
        if not settlement or not segment:
            return False

        # validate the possible combinations of order parameters
        if payload["type"] == OrderType.LIMIT:
            if not "price" in payload:
                raise ApiException("The parameter 'price' must be present in LIMIT order")
            if not "quantity" in payload or not "amount" in payload:
                raise ApiException("The parameter 'quantity' or 'amount' must be present in LIMIT order")
        if payload["type"] == OrderType.MARKET:
            if "price" in payload:
                raise ApiException("The paramenter 'price' can't be present in MARKET order")
            if "amount" in payload and "quantity" in payload:
                raise ApiException("The parameters 'amount' and 'quantity' can't be present simultaneously in MARKET order")
        
        # check order total
        if "price" not in payload:
            price = self._get_instrument_snapshot_value_by_key(instrument_code, long_ticker, segment, "ask")
        else:
            price = payload["price"]
        
        if 'amount' not in payload.items():
            price_factor = self._get_price_factor(instrument_code, long_ticker, segment)
            order_total = float(payload["quantity"]) * float(payload["price"]) / price_factor
        else:
            order_total = float(payload["amount"])
        
        available_funds = self.funds_available()
        available_at_settlement_currency: float = available_funds[settlement.value][
            currency.lower()
        ]

        return available_at_settlement_currency >= order_total

    def _validate_sell_power(self, long_ticker: str, quantity: str) -> bool:
        """
        Validates if there are sufficient stocks available to place a sell order.

        Args:
            long_ticker (str): The long ticker of the instrument.
            quantity (str): The quantity of instruments to sell.

        Returns:
            bool: True if there are sufficient stocks, False otherwise.
        """
        settlement = long_ticker.split("-")[1]
        settlement = self._get_cocos_settlement(settlement)
        available_stocks = self.stocks_available(long_ticker)
        if not settlement:
            return False

        available_at_settlement = available_stocks.get(settlement.value, 0)
        return available_at_settlement >= float(quantity)

    def _find_instrument_code(self, long_ticker: str) -> str:
        """
        Finds the instrument code for the given long ticker.

        Args:
            long_ticker (str): The long ticker of the instrument.

        Returns:
            str: The instrument code, or "" if not found.
        """
        ticker_search: List[Dict[str, Any]] = self.search_ticker(
            long_ticker.split("-")[0]
        )
        for ticker in ticker_search:
            for subtype in ticker["instrument_subtypes"]:
                for data in subtype["market_data"]:
                    if data.get("long_ticker") == long_ticker:
                        return data["instrument_code"]
        return ""

    def _get_instrument_snapshot_value_by_key(self, instrument_code: str, long_ticker:str, segment: Segment, key: str) -> Any:
        """Retrieves the value of a specified key in the instrument snapshot list

        Args:
            instrument_code (str): The instrument code.
            long_ticker (str): The long ticker of the instrument.
            segment (Segment): The segment of the instrument.
            key (str): The key to search

        Returns:
            _type_: _description_
        """
        instrument_snapshot: List[Dict[str, Any]] = self.get_instrument_snapshot(
            instrument_code, segment
        )
        for instrument in instrument_snapshot:
            if instrument.get("long_ticker") == long_ticker:
                return instrument.get(key)
        return ""
        

    def _get_price_factor(
        self, instrument_code: str, long_ticker: str, segment: Segment
    ) -> float:
        """
        Retrieves the price factor for the given instrument code and long ticker.

        Args:
            instrument_code (str): The instrument code.
            long_ticker (str): The long ticker of the instrument.
            segment (Segment): The segment of the instrument.

        Returns:
            float: The price factor if found, or 1 if not found.
        """
        return self._get_instrument_snapshot_value_by_key(instrument_code, long_ticker, segment, "price_factor")
        

    ##############
    ## INTERNAL ##
    ##############

    def _get_byma_settlement(self, settlement: Settlement) -> str:
        """
        Retrieves the BYMA settlement code for the given settlement type.

        Args:
            settlement (Settlement): The settlement type.

        Returns:
            str: The corresponding BYMA settlement code.
        """
        byma_settlement_map: dict[Settlement, str] = {
            Settlement.T0: "0001",
            Settlement.T1: "0002",
            Settlement.T2: "0003",
        }
        return byma_settlement_map.get(settlement, "")

    def _get_cocos_settlement(self, settlement: str) -> Optional[Settlement]:
        """
        Retrieves the Settlement type for the given BYMA settlement code in Cocos.

        Args:
            settlement (str): The BYMA settlement code.

        Returns:
            Settlement or None: The corresponding Settlement type, or None if not found.
        """
        cocos_settlement_map: dict[str, Settlement] = {
            "0001": Settlement.T0,
            "0002": Settlement.T1,
            "0003": Settlement.T2,
        }
        return cocos_settlement_map.get(settlement)

    def _get_cocos_segment(self, segment: str) -> Segment:
        return self.segments(segment)

    def _get_byma_currency(self, currency: Currency) -> str:
        """
        Retrieves the BYMA currency code for the given currency type.

        Args:
            currency (Currency): The currency type.

        Returns:
            str: The corresponding BYMA currency code.
        """
        return currency.value

    def _get_cocos_currency(self, currency: str) -> Currency:
        """
        Retrieves the Currency type for the given BYMA currency code in Cocos.

        Args:
            currency (str): The BYMA currency code.

        Returns:
            Currency or None: The corresponding Currency type, or None if not found.
        """

        return self.currencies(currency)

    def _check_cbu_cvu_exists(self, cbu_cvu_to_check: str) -> bool:
        """
        Private helper function that checks if a given CBU/CVU exists in the user's bank accounts.

        Args:
            cbu_cvu_to_check (str): The CBU/CVU to check for existence.

        Returns:
            bool: True if the CBU/CVU exists in the user's bank accounts, False otherwise.
        """
        accounts_list: List[Dict[str, Any]] = self.my_bank_accounts()
        return any(item["cbu_cvu"] == cbu_cvu_to_check for item in accounts_list)

    def _add_order(self, order_number: str) -> None:
        """
        Private helper function to add an order number to the list of orders.

        Args:
            order_number (str): The order number to add.

        Returns:
            None
        """
        self.orders.append(order_number)

    def _update_account_number(self, new_account_number: str) -> None:
        """
        Private helper function to update the account number with a new value.

        Args:
            new_account_number (str): The new account number to set.

        Returns:
            None
        """
        self.account_number = new_account_number

    def _check_fields(self, fields: List[Tuple[str, Any, Any]]) -> None:
        """
        Private helper function to check the types of fields.

        Args:
            fields (list): A list of tuples containing the field name, field value, and field type.

        Raises:
            ValueError: If a field's value doesn't match its expected type.

        Returns:
            None
        """
        for field_name, field_value, field_type in fields:
            if not isinstance(field_value, field_type):
                raise ValueError(f"{field_name} is not of type {field_type.__name__}")

    def _validate_list_parameters(self, type: str, subtype: str) -> bool:
        """
        Private helper function to validate instrument type and subtype combinations.

        Args:
            type (str): Instrument type.
            subtype (str): Instrument subtype.

        Returns:
            bool: True if the combination is valid, False otherwise.
        """
        for tpl in self.allowed_combinations:
            if type in tpl and subtype in tpl:
                return True
        return False
