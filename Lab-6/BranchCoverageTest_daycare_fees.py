import pytest
from daycare_fees import extra_hours_fee, enrolment_allowed, pickup_status


# ---------- extra_hours_fee ----------
def test_within_included_hours():
    assert extra_hours_fee("toddler", 20, False) == 0


def test_exactly_included_hours_no_fee():
    assert extra_hours_fee("preschool", 30, False) == 0


def test_unknown_age_group():
    with pytest.raises(ValueError):
        extra_hours_fee("teen", 10, False)


def test_negative_hours():
    with pytest.raises(ValueError):
        extra_hours_fee("infant", -1, False)


def test_infant_extra_hours():
    assert extra_hours_fee("infant", 25, False) == 5 * 14


def test_infant_sibling_gets_no_extra_allowance():
    # sibling + infant -> included stays 20
    assert extra_hours_fee("infant", 25, True) == 5 * 14


def test_toddler_sibling_extra_hours():
    # included = 25 + 5 = 30, extra = 5
    assert extra_hours_fee("toddler", 35, True) == 5 * 9


def test_toddler_no_sibling_extra_hours():
    assert extra_hours_fee("toddler", 35, False) == 10 * 9


def test_extra_exactly_20_not_peak():
    # extra = 20 -> not > 20, base rate applies
    assert extra_hours_fee("toddler", 45, False) == 20 * 9


def test_extra_21_peak_non_infant():
    # extra = 21 > 20 -> rate = 9 + 5 = 14
    assert extra_hours_fee("toddler", 46, False) == 21 * 14


def test_infant_peak_rate():
    # extra = 25 > 20 -> rate = 14 + 5 + 3 = 22
    assert extra_hours_fee("infant", 45, False) == 25 * 22


def test_preschool_peak_rate():
    assert extra_hours_fee("preschool", 55, False) == 25 * 14


# ---------- enrolment_allowed ----------
def test_enrolment_allowed():
    assert enrolment_allowed(24, 2, False) is True


def test_enrolment_too_young():
    assert enrolment_allowed(3, 2, False) is False


def test_enrolment_exactly_six_months_with_vacancy():
    assert enrolment_allowed(6, 1, False) is True


def test_enrolment_no_vacancies():
    assert enrolment_allowed(24, 0, False) is False


def test_enrolment_immunisation_pending_old_enough():
    assert enrolment_allowed(12, 0, True) is True


def test_enrolment_immunisation_pending_too_young():
    assert enrolment_allowed(11, 5, True) is False


# ---------- pickup_status ----------
def test_pickup_on_time():
    assert pickup_status(15, False, False) == "on_time"


def test_pickup_on_time_boundary():
    assert pickup_status(10, False, False) == "on_time"


def test_pickup_late():
    assert pickup_status(5, False, False) == "late"


def test_pickup_late_boundary():
    # cutoff 10 -> late when minutes_left >= -5
    assert pickup_status(-5, False, False) == "late"


def test_pickup_overdue():
    assert pickup_status(-10, False, False) == "overdue"


def test_pickup_aftercare_on_time():
    assert pickup_status(20, True, False) == "on_time"


def test_pickup_aftercare_late():
    assert pickup_status(10, True, False) == "late"


def test_pickup_friday_on_time():
    assert pickup_status(20, False, True) == "on_time"


def test_pickup_aftercare_friday():
    # cutoff = 20 + 10 = 30
    assert pickup_status(30, True, True) == "on_time"
    assert pickup_status(-10, True, True) == "overdue"
