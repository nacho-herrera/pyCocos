# -*- coding: utf-8 -*-
"""
    pyCocos.main
    Main client.
"""

from typing import Any, Dict, List, Optional, Tuple

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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Content-Type": "application/json",
    }

    def __init__(self, email: str, password: str, recaptcha_token: str) -> None:
        ## Parameters validation
        required_fields = [
            ("email", email, str),
            ("password", password, str),
            ("recaptcha_token", recaptcha_token, str),
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
        self.recaptcha_token: str = recaptcha_token
        self.account_number: str = ""

        ## Current session variables # ! NEEDS TO BE DEVELOPED
        self.orders: List[str] = []
        self.connected: bool = False

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
        payload = json.dumps({"email": self.email, "password": self.password})

        self.client.update_session_headers(self.headers)

        response = self.client.get_token(params=params, data=payload)
        
        if "error" in response.keys():
            raise Exception(f'Error: {response["error_description"]}')

        if "access_token" not in response.keys():
            raise Exception("Error: Access token not found in the API response")

        self.access_token = response["access_token"]
        self._auth_phase_2()

    def _auth_phase_2(self) -> None:
        """Updates the session headers and performs additional steps after login.

        After successful login and obtaining the access token, this method is responsible for updating the session headers
        with the necessary authentication information. It replicates the workflow of the web app.

        """

        headers_update = {
            "authorization": f"Bearer {self.access_token}",
            "recaptcha-token": self.recaptcha_token,
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
        response = self.client.get_portfolio()
        return response

    def funds_available(self) -> Dict[str, float]:
        """Retrieves the available funds for trading in T+0, T+1, and T+2 settlement dates.

        This method calls the API to fetch the available funds that can be used for trading on different settlement dates.

        Returns:
            Dict[str, float]: A dictionary containing the available funds for each settlement date.

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
        required_fields = [("long_ticker", long_ticker, str)]
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
        required_fields = [("date_from", date_from, str), ("date_to", date_to, str)]
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
        required_fields = [("timeframe", timeframe, PerformanceTimeframe)]
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
            currency (Currencies): The currency of the new bank account.

        Returns:
            Dict[str, Any]: A dictionary containing the response from the API.

        Raises:
            Exception: If there is an error while submitting the new bank account.

        """

        # Parameters validation
        required_fields = [
            ("cbu_cvu", cbu, str),
            ("cuit", cuit, str),
            ("currency", currency, Currency),
        ]
        self._check_fields(required_fields)

        # Create payload object
        payload = json.dumps({"cbu_cvu": cbu, "cuit": cuit, "currency": currency.value})
        response = self.client.submit_new_bank_account(data=payload)
        return response

    def withdraw_funds(
        self, currency: Currency, amount: str, cbu_cvu: str
    ) -> Dict[str, Any]:
        """Submits a request to withdraw funds through the API.

        This method sends a request to withdraw funds from the user's account. The specified amount of funds in the given
        currency will be transferred to the provided bank account (CBU/CVU).

        Args:
            currency (Currencies): The currency of the funds to withdraw.
            amount (str): The amount of funds to withdraw.
            cbu_cvu (str): The bank account (CBU/CVU) to transfer the funds to.

        Raises:
            ApiException: If the specified bank account is not available. Please add it to your account.

        Returns:
            Dict[str, Any]: A dictionary containing the response from the API.

        """

        # Parameters validation
        required_fields = [
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
        quantity: str,
        price: str,
        order_type: OrderType = OrderType.LIMIT,
    ) -> Dict[str, Any]:
        """Submits a buy order through the API.

        This method sends a request to place a buy order for a specific instrument. The order includes the long ticker
        of the instrument, the quantity to buy, the price at which to buy, and the order type (limit or market).

        Args:
            long_ticker (str): The long ticker of the instrument to buy.
            quantity (str): The quantity of the buy order.
            price (str): The price of the buy order.
            order_type (OrderTypes, optional): The type of order (limit or market). Defaults to OrderTypes.LIMIT.

        Returns:
            Dict[str, Any]: A dictionary containing the response from the API, including the new order ID.
        """

        # Parameters validation
        required_fields = [
            ("long_ticker", long_ticker, str),
            ("quantity", quantity, str),
            ("price", price, str),
            ("order_type", order_type, OrderType),
        ]
        self._check_fields(required_fields)

        # Check if account has enough money to purchase
        if not self._validate_buy_power(long_ticker, quantity, price):
            raise ApiException(f"Not enough money to purchase")

        # Create payload object
        payload = {
            "type": order_type.value,
            "side": self.order_sides.BUY.value,
            "quantity": quantity,
            "long_ticker": long_ticker,
            "price": price,
        }

        response = self.client.submit_order(json=payload)
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
        required_fields = [
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
        payload = {
            "type": order_type.value,
            "side": self.order_sides.SELL.value,
            "quantity": quantity,
            "long_ticker": long_ticker,
            "price": price,
        }

        response = self.client.submit_order(json=payload)
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
        required_fields = [
            ("currency", currency, Currency),
            ("amount", amount, float),
            ("term", term, int),
            ("rate", rate, float),
        ]
        self._check_fields(required_fields)

        # Create payload object
        payload = json.dumps(
            {
                "currency": currency.value,
                "amount": amount,
                "term": term,
                "rate": rate,
            }
        )

        response = self.client.submit_repo_order(data=payload)
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
        required_fields = [("order_number", order_number, str)]
        self._check_fields(required_fields)

        # Retrieve order information
        order = self.order_status(order_number)

        # Create payload object
        payload = json.dumps(
            {"instrument": order["instrument"], "ticker": order["ticker"]}
        )

        response = self.client.cancel_order(order_number, data=payload)
        return response

    def order_status(self, order_number: str = "") -> Dict[str, Any]:
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
        required_fields = [("order_number", order_number, str)]
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
        required_fields = [
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
            segment (Segments): The segment of the ticker.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the snapshot price data for all possible settlement dates of the ticker.

        """

        # Parameters validation
        required_fields = [("ticker", ticker, str), ("segment", segment, Segment)]
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
            instrument_type (InstrumentTypes): The category type of the instruments.
            instrument_subtype (InstrumentSubTypes): The category subtype of the instruments.
            settlement (Settlements): The settlement type for the instruments.
            currency (Currencies): The currency for the instruments.
            segment (Segments): The segment for the instruments.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the instrument information for the selected instruments.

        Raises:
            ValueError: If the combination of instrument type and subtype is invalid. Refer to the instrument_types_and_subtypes method.

        """

        # Parameters validation
        required_fields = [
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
            instrument_type (InstrumentTypes): The category type of the instruments.
            instrument_subtype (InstrumentSubTypes): The category subtype of the instruments.
            settlement (Settlements): The settlement type for the instruments.
            currency (Currencies): The currency for the instruments.
            segment (Segments): The segment for the instruments.
            page (int): The page number to retrieve.
            size (int): The number of items per page.

        Returns:
            Dict[str, Any]: A dictionary containing the paginated list of selected instruments.

        Raises:
            ValueError: If the combination of instrument type and subtype is invalid. Refer to the instrument_types_and_subtypes method.

        """

        # Parameters validation
        required_fields = [
            ("instrument_type", instrument_type, InstrumentType),
            ("instrument_subtype", instrument_subtype, InstrumentSubType),
            ("settlement", settlement, Settlement),
            ("currency", currency, Currency),
            ("segment", segment, Segment),
            ("page", page, int),
            ("size", size, int),
        ]
        self._check_fields(required_fields)

        if not self._validate_list_parameters(
            instrument_type.value, instrument_subtype.value
        ):
            raise ValueError(
                "Invalid combination for instrument type and subtype. Check instrument_types_and_subtypes method."
            )

        return self.client.get_tickers_pagination(
            instrument_type.value,
            instrument_subtype.value,
            settlement.value,
            currency.value,
            segment.value,
            page,
            size,
        )

    def get_recommended_tickers(self) -> List[Dict[str, Any]]:
        """Calls the API to retrieve the list of recommended tickers from the home page.

        This method retrieves the list of recommended tickers provided on the home page of the application.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the recommended tickers.

        Note:
            The structure and content of the returned list may vary depending on the API response. Each dictionary in the list
            represents a recommended ticker and may contain different fields such as ticker symbol, company name, price, etc.

        """

        return self.client.get_home_list()

    def get_favorites_tickers(self) -> List[Dict[str, Any]]:
        """Calls the API to retrieve the list of favorite instruments from the home page.

        This method retrieves the list of favorite instruments that have been saved by the user on the home page of the application.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the favorite instruments.

        Note:
            The structure and content of the returned list may vary depending on the API response. Each dictionary in the list
            represents a favorite instrument and may contain different fields such as ticker symbol, company name, price, etc.

        """

        return self.client.get_my_list()

    def search_ticker(self, query: str) -> Dict[str, Any]:
        """Calls the API to search for a ticker by name.

        This method allows searching for a ticker by providing a query string representing the name or part of the name of the ticker.
        The API will return the search results matching the query.

        Args:
            query (str): The query string representing the ticker name to search.

        Returns:
            Dict[str, Any]: The API response with the search results.

        Raises:
            ValueError: If the query string is less than 2 characters long.

        Note:
            The structure and content of the returned dictionary may vary depending on the API response.

        """

        ## Parameters validation
        required_fields = [("query", query, str)]
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

    def instrument_types_and_subtypes(self) -> Dict[str, Any]:
        """Calls the API to retrieve the types and subtypes of available instruments.

        This method retrieves information about the different types and subtypes of instruments
        available for trading. It provides a comprehensive list of instrument categories and their
        corresponding subcategories.

        Returns:
            Dict[str, Any]: The API response with the instrument types and subtypes.

        Note:
            The structure and content of the returned dictionary may vary depending on the API response.

        """

        return self.client.get_instrument_types()

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

        return [
            (_["instrument_type"], _["instrument_subtype"])
            for _ in self.instrument_types_and_subtypes()
        ]

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

        return self.client.get_open_dolar_mep()

    ##########
    ## MISC ##
    ##########

    def get_ads_carrousel(self) -> Dict[str, Any]:
        """Calls API to retrieve the carousel ads.

        The carousel ads are a collection of advertisements displayed in a carousel format.
        This method calls the API to fetch the carousel ads.

        Returns:
            Dict[str, Any]: API Response with the carousel ads.

        Note:
            The structure and content of the returned dictionary may vary depending on the API response.

        """

        return self.client.get_carrousel()

    def get_news(self) -> Dict[str, Any]:
        """Calls API to retrieve news articles.

        This method calls the API to fetch the latest news articles. The returned news articles
        can contain information about various topics such as finance, economy, market updates, etc.

        Returns:
            Dict[str, Any]: API Response with the news articles.

        Note:
            The structure and content of the returned dictionary may vary depending on the API response.

        """

        return self.client.get_news()

    def get_cocos_university_articles(self) -> Dict[str, Any]:
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
            currency (Currencies): Currency of the instrument.
            segment (Segments, optional): Segment of the instrument. Defaults to Segments.DEFAULT.

        Returns:
            str: The long ticker representing the ticker and settlement date.

        Notes:
            - The `segment` argument is not validated against valid ticker and segment combinations.
            It's important to ensure the appropriate segment is provided.
            - The long ticker format follows the pattern: "<TICKER>-<SETTLEMENT>-<SEGMENT>-CT-<CURRENCY>",
            where:
                - <TICKER> represents the ticker symbol in uppercase.
                - <SETTLEMENT> is a code representing the settlement date (e.g., "0001" for T0).
                - <SEGMENT> is the segment of the instrument.
                - CT indicates the BYMA market venue.
                - <CURRENCY> represents the currency code.

        Examples:
            long_ticker("AAPL", Settlements.T1, Currencies.PESOS) returns "AAPL-0002-C-CT-ARS"
            long_ticker("GOOGD", Settlements.T0, Currencies.DOLAR_MEP) returns "GOOGD-0001-C-CT-USD"
            long_ticker("GFGC500.JU", Settlements.T2, Currencies.PESOS, Segments.OPTIONS) returns "GFGC500.JU-0001-O-CT-ARS"

        """

        if segment is Segment.FCI:
            return ticker.upper()

        _settlement = self._get_byma_settlement(settlement)
        _currency = self._get_byma_currency(currency)

        return f"{ticker.upper()}-{_settlement}-{segment.value}-CT-{_currency}"

    def _validate_buy_power(self, long_ticker: str, quantity: str, price: str) -> bool:
        """
        Validates if there are sufficient funds available to place a buy order.

        Args:
            long_ticker (str): The long ticker of the instrument.
            quantity (str): The quantity of instruments to buy.
            price (str): The price per instrument.

        Returns:
            bool: True if there are sufficient funds, False otherwise.
        """
        _, settlement, segment, _, currency = long_ticker.split("-")

        settlement = self._get_cocos_settlement(settlement)
        segment = self._get_cocos_segment(segment)
        instrument_code = self._find_instrument_code(long_ticker)
        price_factor = self._get_price_factor(instrument_code, long_ticker, segment)

        available_funds = self.funds_available()
        available_at_settlement_currency = available_funds[settlement.value][
            currency.lower()
        ]
        order_total = float(quantity) * float(price) / price_factor

        print(f"{order_total}, {available_at_settlement_currency}")

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
        available_at_settlement = available_stocks.get(settlement.value, 0)

        return available_at_settlement >= float(quantity)

    def _find_instrument_code(self, long_ticker: str) -> str:
        """
        Finds the instrument code for the given long ticker.

        Args:
            long_ticker (str): The long ticker of the instrument.

        Returns:
            str: The instrument code, or None if not found.
        """
        ticker_search = self.search_ticker(long_ticker.split("-")[0])
        for ticker in ticker_search:
            for subtype in ticker["instrument_subtypes"]:
                for data in subtype["market_data"]:
                    if data.get("long_ticker") == long_ticker:
                        return data["instrument_code"]
        return None

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
        instrument_snapshot = self.get_instrument_snapshot(instrument_code, segment)
        for instrument in instrument_snapshot:
            if instrument.get("long_ticker") == long_ticker:
                return instrument["price_factor"]
        return 1

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
        byma_settlement_map = {
            Settlement.T0: "0001",
            Settlement.T1: "0002",
            Settlement.T2: "0003",
        }
        return byma_settlement_map.get(settlement, "")

    def _get_byma_currency(self, currency: Currency) -> str:
        """
        Retrieves the BYMA currency code for the given currency type.

        Args:
            currency (Currency): The currency type.

        Returns:
            str: The corresponding BYMA currency code.
        """
        byma_currency_map = {
            Currency.PESOS: "ARS",
            Currency.DOLAR_MEP: "USD",
            Currency.DOLAR_CABLE: "",
        }
        return byma_currency_map.get(currency, "")

    def _get_cocos_settlement(self, settlement: str) -> Optional[Settlement]:
        """
        Retrieves the Settlement type for the given BYMA settlement code in Cocos.

        Args:
            settlement (str): The BYMA settlement code.

        Returns:
            Settlement or None: The corresponding Settlement type, or None if not found.
        """
        cocos_settlement_map = {
            "0001": Settlement.T0,
            "0002": Settlement.T1,
            "0003": Settlement.T2,
        }
        return cocos_settlement_map.get(settlement)

    def _get_cocos_segment(self, segment: str) -> Segment:
        cocos_segment_map = {
            "C": Segment.DEFAULT,
            "O": Segment.OPTIONS,
            "U": Segment.REPO,
        }
        return cocos_segment_map.get(segment)

    def _get_cocos_currency(self, currency: str) -> Optional[Currency]:
        """
        Retrieves the Currency type for the given BYMA currency code in Cocos.

        Args:
            currency (str): The BYMA currency code.

        Returns:
            Currency or None: The corresponding Currency type, or None if not found.
        """
        cocos_currency_map = {"ARS": Currency.PESOS, "USD": Currency.DOLAR_MEP}
        return cocos_currency_map.get(currency)

    def _check_cbu_cvu_exists(self, cbu_cvu_to_check: str) -> bool:
        """
        Private helper function that checks if a given CBU/CVU exists in the user's bank accounts.

        Args:
            cbu_cvu_to_check (str): The CBU/CVU to check for existence.

        Returns:
            bool: True if the CBU/CVU exists in the user's bank accounts, False otherwise.
        """
        accounts_list = self.my_bank_accounts()
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

    def _check_fields(self, fields) -> None:
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

    def _validate_list_parameters(self, type, subtype) -> bool:
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
