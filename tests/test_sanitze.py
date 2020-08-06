"""Test functions for the _sanitize_file module."""
import pytest

from repobee_sanitizer import _sanitize, _syntax

import testhelpers

(
    VALID_TEST_CASE_ARGS,
    VALID_TEST_CASE_IDS,
) = testhelpers.generate_valid_test_cases()
(
    INVALID_TEST_CASE_ARGS,
    INVALID_TEST_CASE_IDS,
) = testhelpers.generate_invalid_test_cases()


@pytest.mark.parametrize(
    "text", INVALID_TEST_CASE_ARGS, ids=INVALID_TEST_CASE_IDS
)
def test_sanitize_invalid(text: str):
    assert _syntax.check_syntax(text)


@pytest.mark.parametrize("data", VALID_TEST_CASE_ARGS, ids=VALID_TEST_CASE_IDS)
def test_sanitize_valid(data: testhelpers.TestData):
    """Test sanitizing valid cases with predefined expected outputs. Input
    for this test function is generated by the pytest_generate_tests
    hook.
    """
    assert _sanitize.sanitize_text(data.inp) == data.out
    assert _sanitize.sanitize_text(data.inp, strip=True) == data.inverse
