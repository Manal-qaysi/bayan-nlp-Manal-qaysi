"""My golden tests for the Arabic search profile (cases taken from Bayan data).

The same cases run inside notebooks/05_arabic_nlp.ipynb with CAMeL Tools; here
they run with the dependency-light stdlib backend, and with CAMeL Tools too
when it is installed, so the two backends are checked against one contract.
"""
import importlib.util

import pytest

from bayan.arabic_profiles import normalize_arabic_profile

GOLDEN = [
    ("إِدَارَةُ الحِساب", "search", "ادارة الحساب"),
    ("على  الطـريق", "search", "علي الطريق"),
    ("مستشفى الولادة", "search", "مستشفي الولادة"),
    ("أُريد تجديد الوصفة", "search", "اريد تجديد الوصفة"),
    ("الخـدمة متأخرة مرررة اليوم", "search", "الخدمة متاخرة مرررة اليوم"),
    ("حالة الطلبة", "search", "حالة الطلبة"),  # teh marbuta is preserved on purpose
    ("إدارةُ الحساب", "conservative", "إدارةُ الحساب"),
    ("اتصل على 0551234567", "conservative", "اتصل على [PHONE]"),
]

BACKENDS = ["stdlib"] + (["camel"] if importlib.util.find_spec("camel_tools") else [])


@pytest.mark.parametrize("backend", BACKENDS)
def test_golden_cases(backend):
    for text, profile, expected in GOLDEN:
        record = normalize_arabic_profile(text, profile=profile, backend=backend)
        assert record.model_text == expected, (backend, text, record.model_text)
        assert record.display_text == text
