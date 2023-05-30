# -*- coding: utf-8 -*-
"""
    pyCocos.enums
    Enumerators for common constants
"""

from enum import Enum


class Currency(Enum):
    """Enumerates the supported currencies in the application."""

    DOLAR_CABLE = "CABLE"
    DOLAR_MEP = "MEP"
    PESOS = "ARS"


class OrderType(Enum):
    """Enumerates the types of orders supported in the application."""

    LIMIT = "LIMIT"
    MARKET = "MARKET"


class OrderSide(Enum):
    """Enumerates the sides (buy/sell) of orders in the application."""

    BUY = "BUY"
    SELL = "SELL"


class Segment(Enum):
    """Enumerates the market segments in the application.
    
    For FCI instruments use Segments.FCI; 
    for stock options use Segments.OPTIONS; 
    for Repo instruments use Segments.REPO. 
    Otherwise use Segments.DEFAULT for everything else
    """

    DEFAULT = "C"
    FCI = "FCI"
    OPTIONS = "O"
    REPO = "U"


class InstrumentType(Enum):
    """Enumerates the instruments categories in the application."""

    ACCIONES = "ACCIONES"
    BONOS = "BONOS_PUBLICOS"
    CEDEARS = "CEDEARS"
    CORP = "BONOS_CORP"
    FCI = "FCI"
    LETRAS = "LETRAS"
    REPO = "CAUCION"


class InstrumentSubType(Enum):
    """Enumerates the instruments sub-categories in the application."""

    ARS = "NACIONALES_ARS"
    CER = "CER"
    ETF = "ETF"
    FIXED = "TASA_FIJA"
    GENERAL = "GENERAL"
    LIDERES = "LIDERES"
    NEW = "NUEVOS"
    PROV = "PROVINCIALES"
    TOP = "TOP"
    USD = "NACIONALES_USD"
    NONE = None

class Settlement(Enum):
    """Enumerates the settlement options for trades in the application."""

    T0 = "CI"
    T1 = "24hs"
    T2 = "48hs"


class PerformanceTimeframe(Enum):
    """Enumerates the different types of performance reports available in the application."""

    DAILY = "daily"
    HISTORICAL = "historical"
    RANGE = "range"
