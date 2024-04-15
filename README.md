# Welcome to pyCocos' Documentation

## Overview

*pyCocos* is a Python library that enables interaction with Cocos Capital REST APIs. It is designed to save developers hours of research and coding required to connect to Cocos Capital REST APIs.

## Disclaimer

*pyCocos* is not owned by Cocos Capital, and the authors are not responsible for the use of this library.

## Installation

To install *pyCocos*, you can use the following command:

```shell
pip install pycocos
```

## API Credentials

To use this library, you need to have the correct authentication credentials.

## Dependencies

The library has the following dependency:

```
requests>=2.31.0
simplejson>=3.19.1
pyotp>=2.9.0
```
## Features

#### Available Methods

#### Initialization

Before using the library, you need to initialize it with a valid email and password. The library includes the working webpage API key token. If that token is updated, you can find it using the browser dev-tools and pass it on initialization with the api_key parameter.

#### 2nd Factor Authentication

As of 4/13/2024, Cocos Capital has implemented second-factor authentication (2FA) for all users, offering options such as SMS, email, or TOTP (Time-Based One-Time Password) app authentication. This library incorporates the pyotp module for automated code generation. To utilize this feature, the TOTP secret key must be provided as the totp_secret_key parameter during initialization. If the parameter is not supplied, the library will prompt for the code interactively.

For those with an activated TOTP app, you can retrieve your secret key using this method. If your account lacks Google Authenticator activation, it's advisable to scan the QR code first with a QR reader, note the URL, and then add it to the Google Authenticator app. The QR code typically contains a text resembling: otpauth://totp/app.cocos.capital:<your_email>?algorithm=SHA1&digits=6&issuer=app.cocos.capital&period=30&secret=<random_string>. The <random_string> within the URL is the TOTP secret key, which needs to be passed as the aforementioned parameter.

The PyOTP implementation was graciously developed by @El_Raulo on Telegram.

#### REST

The library provides functions to make requests to the REST API and retrieve the corresponding responses.

###### Functions

- **logout**: Performs a logout.
- **my_data**: Retrieves customer information.
- **my_bank_accounts**: Retrieves the bank accounts available for withdrawal.
- **my_portfolio**: Retrieves the available portfolio.
- **funds_available**: Retrieves the available funds for each settlement date.
- **stocks_available**: Retrieves the amount of stock available for each settlement date.
- **account_activity**: Retrieves the account activity for a given period.
- **portfolio_performance**: Retrieves the portfolio performance for a given timeframe.
- **submit_new_bank_account**: Sends a new bank account.
- **withdraw_funds**: Sends a withdrawal order.
- **submit_buy_order**: Sends a buy order.
- **submit_sell_order**: Sends a sell order.
- **place_repo_order**: Sends a repo (caucion) order.
- **cancel_order**: Sends a cancel order request, if possible.
- **order_status**: Retrieves the status of one or all orders.
- **get_daily_history**: Retrieves the closing price history for a given instrument and period.
- **get_instrument_snapshot**: Retrieves the market price information for a given instrument.
- **get_instrument_list_snapshot**: Retrieves the market price information for predefined instrument types.
- **search_ticker**: Queries the API to search for a particular instrument based on the name.
- **market_status**: Retrieves the status of the market session.
- **instruments_rules**: Retrieves the price rules for every type of instrument.
- **get_dolar_mep_info**: Retrieves the Cocos Capital "closed" Dolar MEP quote.
- **get_cocos_university_articles**: Retrieves the University articles from the Cocos Capital app's homepage.

> All functions return a dictionary representing the JSON response.

#### Websocket

Cocos Capital uses SocketIO for real-time quote updates. These methods are not available in the library at the moment.

#### Enumerations

The library also provides enumerations to help developers avoid errors and improve readability.

- **Currencies**: Identifies the available currencies in the app.
- **OrderTypes**: Identifies the available order types.
- **OrderSides**: Identifies the order sides.
- **Segments**: Identifies the different market segments.
- **InstrumentTypes**: Identifies the instrument types.
- **InstrumentSubTypes**: Identifies the instrument subtypes.
- **Settlements**: Identifies the different settlement dates.
- **PerformanceTimeframes**: Identifies the different timeframes available in the performance report.

## Usage

Once the library has been installed, you can import and initialize it. The initialization sets the email and password. It then attempts to authenticate with the provided credentials. If the authentication fails, an `ApiException` is thrown.

```python
from pycocos import Cocos

app = Cocos(email="sample@email.com", password="S4mp13.p4ssW0rd", api_key="OPTIONAL", topt_secret_key="OPTIONAL")

```

*api_key* and *topt_secret_key* are optional parameters, default values are None.

#### REST

```python
# Get the available portfolio with the current market valuation
app.my_portfolio()

# Get the available funds
app.funds_available()

# Send a withdrawal order of 1000 pesos
app.withdraw_funds(currency=app.currencies.PESOS, 
                   amount="1000", 
                   cbu_cvu="0123456789012345678912")

# Get the long ticker for AL30 with T+2 settlement
long_ticker = app.long_ticker(ticker="AL30", 
                              settlement=app.settlements.T2, 
                              currency=app.currencies.PESOS)

# Send a buy order for 200 AL30 bonds with T+2 settlement at $9000. By default, all orders are *LIMIT* orders.
order = app.submit_buy_order(long_ticker=long_ticker, 
                             quantity="200", 
                             price="9000")

# Cancel an order by order_id
app.cancel_order(order_number=order['Orden'])

# Get the quoteboard for "Acciones panel Lideres", T+2 settlement, traded in Pesos
app.instrument_list_snapshot(instrument_type=app.instrument_types.ACCIONES, 
                             instrument_subtype=app.instrument_subtypes.LIDERES, 
                             settlement=app.settlements.T2, 
                             currency=app.currencies.PESOS, 
                             segment=app.segments.DEFAULT)
```
For more information you can check this [article.](https://medium.com/@nachoherrera/biblioteca-pycocos-a3579721c79e)

## Official API Documentation

There is no official API documentation for this library. The library was created by webscraping the app.

## Acknowledgements

This library was created with the support of the Scrappers Argentinos and Inversiones y Algoritmos Telegram Groups.
The updated version that includes OTP validation is based on the development and testing of @El_Raulo, @mjcolom, and @sebivaq. Special thanks to them.
