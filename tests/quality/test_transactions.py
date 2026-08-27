from datetime import date
from decimal import Decimal

import pytest

from finflow.database.connection import get_connection
from finflow.quality.transactions import (
    DataQualityError,
    validate_staging_transactions,
)


TEST_DATE = date(2026, 8, 25)


def _insert_quality_test_transaction(
    transaction_id: str = "TXQUALITY001",
    transaction_amount: Decimal = Decimal("100.00"),
    transaction_fee: Decimal = Decimal("2.50"),
    exchange_rate: Decimal = Decimal("0.029"),
    currency_code: str = "THB",
):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO staging.stg_transactions (
                    transaction_id,
                    customer_id,
                    account_id,
                    merchant_id,
                    currency_code,
                    payment_method_code,
                    transaction_timestamp,
                    transaction_amount,
                    transaction_fee,
                    exchange_rate
                )
                VALUES (
                    %s,
                    'CQTEST001',
                    'AQTEST001',
                    'MQTEST001',
                    %s,
                    'QUALITY_CARD',
                    '2026-08-25 12:00:00',
                    %s,
                    %s,
                    %s
                )
                ON CONFLICT (transaction_id) DO UPDATE
                SET
                    currency_code = EXCLUDED.currency_code,
                    transaction_amount = EXCLUDED.transaction_amount,
                    transaction_fee = EXCLUDED.transaction_fee,
                    exchange_rate = EXCLUDED.exchange_rate;
                """,
                (
                    transaction_id,
                    currency_code,
                    transaction_amount,
                    transaction_fee,
                    exchange_rate,
                ),
            )

        conn.commit()


def _cleanup_quality_test_data():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM staging.stg_transactions
                WHERE transaction_id = 'TXQUALITY001';
                """
            )

        conn.commit()


def test_staging_transactions_pass_quality_checks():
    count = validate_staging_transactions(
        transaction_date=TEST_DATE,
    )

    assert count == 10


def test_quality_check_fails_when_no_transactions_exist():
    with pytest.raises(DataQualityError, match="No staging transactions"):
        validate_staging_transactions(
            transaction_date=date(2099, 1, 1),
        )


def test_quality_check_fails_for_negative_transaction_amount():
    _insert_quality_test_transaction(
        transaction_amount=Decimal("-100.00"),
    )

    try:
        with pytest.raises(
            DataQualityError,
            match="negative transaction_amount",
        ):
            validate_staging_transactions(
                transaction_date=TEST_DATE,
            )
    finally:
        _cleanup_quality_test_data()


def test_quality_check_fails_for_negative_transaction_fee():
    _insert_quality_test_transaction(
        transaction_fee=Decimal("-2.50"),
    )

    try:
        with pytest.raises(
            DataQualityError,
            match="negative transaction_fee",
        ):
            validate_staging_transactions(
                transaction_date=TEST_DATE,
            )
    finally:
        _cleanup_quality_test_data()


def test_quality_check_fails_for_invalid_exchange_rate():
    _insert_quality_test_transaction(
        exchange_rate=Decimal("0"),
    )

    try:
        with pytest.raises(
            DataQualityError,
            match="exchange_rate <= 0",
        ):
            validate_staging_transactions(
                transaction_date=TEST_DATE,
            )
    finally:
        _cleanup_quality_test_data()


def test_quality_check_fails_for_invalid_currency_code():
    _insert_quality_test_transaction(
        currency_code="thai",
    )

    try:
        with pytest.raises(
            DataQualityError,
            match="invalid currency_code",
        ):
            validate_staging_transactions(
                transaction_date=TEST_DATE,
            )
    finally:
        _cleanup_quality_test_data()

def test_quality_check_reports_multiple_failures():
    _insert_quality_test_transaction(
        transaction_amount=Decimal("-100.00"),
        transaction_fee=Decimal("-2.50"),
        exchange_rate=Decimal("0"),
        currency_code="thai",
    )

    try:
        with pytest.raises(DataQualityError) as exc_info:
            validate_staging_transactions(
                transaction_date=TEST_DATE,
            )

        message = str(exc_info.value)

        assert "negative transaction_amount" in message
        assert "negative transaction_fee" in message
        assert "exchange_rate <= 0" in message
        assert "invalid currency_code" in message

    finally:
        _cleanup_quality_test_data()