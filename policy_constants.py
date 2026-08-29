"""Canonical 2026 DSC policy values.

All rates are decimals: 0.19 means 19 percent.
All thresholds and amounts are DZD.

Single source of truth per docs/DSC Constants and CI Implementation Guide.md (§1).
Generators import from here; verify_rates.py keeps an independent REVIEWED snapshot
so an accidental edit here cannot self-affirm.
"""
from __future__ import annotations

from math import inf

TAX_YEAR = 2026

TVA_STANDARD_RATE = 0.19
TVA_REDUCED_RATE = 0.09

IBS_PRODUCTION_RATE = 0.19
IBS_BTP_TOURISM_RATE = 0.23
IBS_SERVICES_COMMERCE_RATE = 0.26

IFU_PRODUCTION_RATE = 0.05
IFU_SERVICES_RATE = 0.12
IFU_AUTO_ENTREPRENEUR_RATE = 0.005

CNAS_EMPLOYER_RATE = 0.255
CNAS_EMPLOYEE_RATE = 0.09
CNAS_COMBINED_PAYROLL_RATE = CNAS_EMPLOYER_RATE + CNAS_EMPLOYEE_RATE
SNMG_MONTHLY = 24_000
CASNOS_RATE = 0.15
CASNOS_MIN_MONTHLY = 3_000

VAN_DISCOUNT_RATE = 0.12
DEFAULT_BANK_LOAN_RATE = 0.09

NESDA_INTEREST_RATE = 0.0
NESDA_REPAYMENT_YEARS = 7
NESDA_GRACE_YEARS = 1.5
NESDA_BANK_SHARE = 0.70

# Canonical IRG representation: annual thresholds in DZD.
IRG_ANNUAL_BRACKETS = (
    (240_000, 0.00),
    (480_000, 0.23),
    (960_000, 0.27),
    (1_920_000, 0.30),
    (3_840_000, 0.33),
    (inf, 0.35),
)


def annual_to_monthly_brackets(brackets=IRG_ANNUAL_BRACKETS):
    """Derive monthly thresholds from the canonical annual policy table."""
    return tuple(
        (threshold if threshold == inf else threshold / 12, rate)
        for threshold, rate in brackets
    )


IRG_MONTHLY_BRACKETS = annual_to_monthly_brackets()

WILAYAS = (
    "01-Adrar",
    "02-Chlef",
    "03-Laghouat",
    "04-Oum El Bouaghi",
    "05-Batna",
    "06-Béjaïa",
    "07-Biskra",
    "08-Béchar",
    "09-Blida",
    "10-Bouira",
    "11-Tamanrasset",
    "12-Tébessa",
    "13-Tlemcen",
    "14-Tiaret",
    "15-Tizi Ouzou",
    "16-Alger",
    "17-Djelfa",
    "18-Jijel",
    "19-Sétif",
    "20-Saïda",
    "21-Skikda",
    "22-Sidi Bel Abbès",
    "23-Annaba",
    "24-Guelma",
    "25-Constantine",
    "26-Médéa",
    "27-Mostaganem",
    "28-M'Sila",
    "29-Mascara",
    "30-Ouargla",
    "31-Oran",
    "32-El Bayadh",
    "33-Illizi",
    "34-Bordj Bou Arréridj",
    "35-Boumerdès",
    "36-El Tarf",
    "37-Tindouf",
    "38-Tissemsilt",
    "39-El Oued",
    "40-Khenchela",
    "41-Souk Ahras",
    "42-Tipaza",
    "43-Mila",
    "44-Aïn Defla",
    "45-Naâma",
    "46-Aïn Témouchent",
    "47-Ghardaïa",
    "48-Relizane",
    "49-El M'Ghair",
    "50-El Meniaa",
    "51-Ouled Djellal",
    "52-Bordj Badji Mokhtar",
    "53-Béni Abbès",
    "54-Timimoun",
    "55-Touggourt",
    "56-Djanet",
    "57-In Salah",
    "58-In Guezzam",
)
