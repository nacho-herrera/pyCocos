# -*- coding: utf-8 -*-
"""
pyCocos.urls
Defines all API Paths
"""

api_url = "https://api.cocos.capital/"

endpoints = {
    "token": "auth/v1/token",
    "logout": "auth/v1/logout",
    "2factors": "auth/v1/factors/default",
    "challenge": "auth/v1/factors/{}/challenge",
    "verify": "auth/v1/factors/{}/verify",
    "open_market": "api/v1/calendar/open-market",
    "carrousel": "api/v1/home/carrousel",
    "news": "api/v1/home/news",
    "university": "api/v1/home/university",
    "dolar_mep": "api/v1/markets/dolar-mep",
    "new_dolar_mep": "api/v1/public/mep-prices",
    "home_list": "api/v1/markets/lists/home",
    "my_list": "api/v1/markets/lists/me",
    "tickers_list": "api/v1/markets/lists/tickers/?instrument_type={}&instrument_subtype={}&settlement_days={}&currency={}&segment={}",
    "tickers_pagination": "api/v1/markets/lists/tickers-pagination?instrument_type={}&instrument_subtype={}&settlement_days={}&currency={}&segment={}&page={}&size={}",
    "historic_data": "api/v1/markets/tickers/{}/historic-data?date_from={}",
    "tickers": "api/v1/markets/tickers/{}?segment={}",
    "tickers_search": "api/v1/markets/tickers/search?q={}",
    "rules": "api/v1/markets/tickers/rules",
    "types": "api/v1/markets/types",
    "open_dolar_mep": "api/v1/public/open-dolar-mep",
    "account_movements": "api/v1/transfers?date_from={}&date_to={}",
    "receipt": "api/v1/transfers/receipt?ext_id_receipt={}",
    "bank_accounts": "api/v1/transfers/accounts",
    "new_account": "api/v1/transfers/accounts",
    "withdraw": "api/v1/transfers/withdraw",
    "my_data": "api/v1/users/me",
    "investor_test": "api/v1/users/investor-profile-test",
    "daily_performance": "api/v1/wallet/performance/daily",
    "historic_performance": "api/v1/wallet/performance/historic",
    "performance_period": "api/v1/wallet/performance/global?date_from={}&date_to={}",
    "portfolio": "api/v1/wallet/portfolio",
    "orders": "api/v2/orders",
    "order": "api/v2/orders/{}",
    "repo": "api/v2/orders/caucion",
    "buying_power": "api/v2/orders/buying-power",
    "selling_power": "api/v2/orders/selling-power/?long_ticker={}",
}
