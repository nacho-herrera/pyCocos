# -*- coding: utf-8 -*-
"""
    pyCocos.enums
    Enumerators for common constants
"""

from enum import Enum


class Currency(Enum):
    """Enumerates the supported currencies in the application."""

    ALL = "INDISTINTO"
    CABLE = "EXT"
    NONE = ""
    PESOS = "ARS"
    USD = "USD"

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

    For FCI instruments use Segment.FCI;
    for stock options use Segment.OPTIONS;
    for Repo instruments use Segment.REPO.
    Otherwise use Segment.DEFAULT for everything else
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
    CRYPTO = "CRYPTO"
    ETF = "ETF"
    FIXED = "TASA_FIJA"
    GENERAL = "GENERAL"
    LIDERES = "LIDERES"
    NEW = "NUEVOS"
    NONE = ""
    OTROS = "OTROS"
    PF = "PF"
    PROV = "PROVINCIALES"
    TOP = "TOP"
    USD = "NACIONALES_USD"
    BONOS_CORP = "BONOSC"


class Settlement(Enum):
    """Enumerates the settlement options for trades in the application."""

    T0 = "CI"
    T1 = "24hs"
    T2 = "48hs"
    NONE = ""

class PerformanceTimeframe(Enum):
    """Enumerates the different types of performance reports available in the application."""

    DAILY = "daily"
    HISTORICAL = "historical"
    RANGE = "range"
