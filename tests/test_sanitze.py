"""Test functions for the _sanitize_file module."""
import pytest

from repobee_sanitizer import _sanitize

import repobee_plug as plug

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
    "inp", INVALID_TEST_CASE_ARGS, ids=INVALID_TEST_CASE_IDS
)
def test_sanitize_invalid(inp: str):
    with pytest.raises(plug.PlugError):
        _sanitize.sanitize(inp)


@pytest.mark.parametrize(
    "inp,expected", VALID_TEST_CASE_ARGS, ids=VALID_TEST_CASE_IDS
)
def test_sanitize_valid(inp: str, expected: str):
    """Test sanitizing valid cases with predefined expected outputs. Input
    for this test function is generated by the pytest_generate_tests
    hook.
    """
    assert _sanitize.sanitize(inp) == expected
