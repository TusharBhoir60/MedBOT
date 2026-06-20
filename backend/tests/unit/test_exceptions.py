"""
Unit tests for domain exceptions — no database required.

Validates:
  - Exception hierarchy (all inherit from AarogyaBaseException)
  - error_code fields are set correctly
  - details dict propagates
  - timestamp is an ISO format string
"""
import pytest
from datetime import datetime

from core.exceptions import (
    AarogyaBaseException,
    DatabaseException,
    NotFoundException,
    ServiceException,
    ValidationException,
)


class TestExceptionHierarchy:
    def test_database_exception_is_base(self) -> None:
        exc = DatabaseException("db failed")
        assert isinstance(exc, AarogyaBaseException)

    def test_service_exception_is_base(self) -> None:
        exc = ServiceException("logic failed")
        assert isinstance(exc, AarogyaBaseException)

    def test_not_found_exception_is_base(self) -> None:
        exc = NotFoundException("not found")
        assert isinstance(exc, AarogyaBaseException)

    def test_validation_exception_is_base(self) -> None:
        exc = ValidationException("bad input")
        assert isinstance(exc, AarogyaBaseException)


class TestErrorCodes:
    def test_database_exception_error_code(self) -> None:
        exc = DatabaseException()
        assert exc.error_code == "DATABASE_ERROR"

    def test_not_found_exception_error_code(self) -> None:
        exc = NotFoundException()
        assert exc.error_code == "NOT_FOUND"

    def test_service_exception_error_code(self) -> None:
        exc = ServiceException()
        assert exc.error_code == "SERVICE_ERROR"

    def test_validation_exception_error_code(self) -> None:
        exc = ValidationException()
        assert exc.error_code == "VALIDATION_ERROR"


class TestExceptionDetails:
    def test_details_dict_propagates(self) -> None:
        details = {"field": "patient_id", "reason": "uuid invalid"}
        exc = ValidationException("bad uuid", details=details)
        assert exc.details == details

    def test_details_defaults_to_empty_dict(self) -> None:
        exc = NotFoundException()
        assert exc.details == {}

    def test_message_set_correctly(self) -> None:
        exc = DatabaseException("connection timeout")
        assert exc.message == "connection timeout"
        assert str(exc) == "connection timeout"

    def test_timestamp_is_iso_format(self) -> None:
        exc = AarogyaBaseException("test")
        # Should be parseable as ISO datetime
        parsed = datetime.fromisoformat(exc.timestamp)
        assert parsed is not None
