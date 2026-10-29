import pytest
from daycare_fees import extra_hours_fee, enrolment_allowed, pickup_status


# ---------- extra_hours_fee ----------
def test_within_included_hours():
    assert extra_hours_fee("toddler", 20, False) == 0


def test_unknown_age_group():
    with pytest.raises(ValueError):
        extra_hours_fee("teen", 10, False)


def test_negative_hours():
    with pytest.raises(ValueError):
        extra_hours_fee("infant", -1, False)


def test_infant_extra_hours():
    assert extra_hours_fee("infant", 25, False) == 5 * 14


def test_toddler_sibling_extra_hours():
    # included = 25 + 5 = 30, extra = 5
    assert extra_hours_fee("toddler", 35, True) == 5 * 9


def test_infant_peak_rate():
    # extra = 25 > 20 -> rate = 14 + 5 + 3 = 22
    assert extra_hours_fee("infant", 45, False) == 25 * 22


# ---------- enrolment_allowed ----------
def test_enrolment_allowed():
    assert enrolment_allowed(24, 2, False) is True


def test_enrolment_too_young():
    assert enrolment_allowed(3, 2, False) is False


# ---------- pickup_status ----------
def test_pickup_on_time():
    assert pickup_status(15, False, False) == "on_time"


def test_pickup_late():
    assert pickup_status(5, False, False) == "late"


def test_pickup_overdue():
    assert pickup_status(-10, False, False) == "overdue"
