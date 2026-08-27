from datetime import date

from finflow.database.connection import get_connection


class DataQualityError(Exception):
    """Raised when staging transaction data fails data-quality checks."""


def validate_staging_transactions(
    transaction_date: date | None = None,
) -> int:
    """
    Validate transactions in staging before loading them into core.

    Returns:
        Number of transactions validated.

    Raises:
        DataQualityError: If any data-quality check fails.
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            date_filter = """
                %s IS NULL
                OR transaction_timestamp::date = %s
            """

            # 1. Check that there are transactions to process.
            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM staging.stg_transactions
                WHERE {date_filter};
                """,
                (transaction_date, transaction_date),
            )

            row_count = cursor.fetchone()[0]

            if row_count == 0:
                raise DataQualityError(
                    "No staging transactions found for the processing date."
                )

            failures = []

            # 2. Check required fields.
            required_columns = [
                "transaction_id",
                "customer_id",
                "merchant_id",
                "account_id",
                "currency_code",
                "payment_method_code",
                "transaction_timestamp",
                "transaction_amount",
                "transaction_fee",
                "exchange_rate",
            ]

            for column in required_columns:
                cursor.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM staging.stg_transactions
                    WHERE ({date_filter})
                      AND {column} IS NULL;
                    """,
                    (transaction_date, transaction_date),
                )

                null_count = cursor.fetchone()[0]

                if null_count > 0:
                    failures.append(
                        f"{column} contains {null_count} NULL value(s)."
                    )

            # 3. Duplicate transaction IDs.
            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM (
                    SELECT transaction_id
                    FROM staging.stg_transactions
                    WHERE {date_filter}
                    GROUP BY transaction_id
                    HAVING COUNT(*) > 1
                ) duplicates;
                """,
                (transaction_date, transaction_date),
            )

            duplicate_count = cursor.fetchone()[0]

            if duplicate_count > 0:
                failures.append(
                    f"{duplicate_count} duplicate transaction ID(s) found."
                )

            # 4. Transaction amount must not be negative.
            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM staging.stg_transactions
                WHERE ({date_filter})
                  AND transaction_amount < 0;
                """,
                (transaction_date, transaction_date),
            )

            invalid_amount_count = cursor.fetchone()[0]

            if invalid_amount_count > 0:
                failures.append(
                    f"{invalid_amount_count} transaction(s) have "
                    "a negative transaction_amount."
                )

            # 5. Transaction fee must not be negative.
            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM staging.stg_transactions
                WHERE ({date_filter})
                  AND transaction_fee < 0;
                """,
                (transaction_date, transaction_date),
            )

            invalid_fee_count = cursor.fetchone()[0]

            if invalid_fee_count > 0:
                failures.append(
                    f"{invalid_fee_count} transaction(s) have "
                    "a negative transaction_fee."
                )

            # 6. Exchange rate must be positive.
            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM staging.stg_transactions
                WHERE ({date_filter})
                  AND exchange_rate <= 0;
                """,
                (transaction_date, transaction_date),
            )

            invalid_exchange_rate_count = cursor.fetchone()[0]

            if invalid_exchange_rate_count > 0:
                failures.append(
                    f"{invalid_exchange_rate_count} transaction(s) have "
                    "an exchange_rate <= 0."
                )

            # 7. Currency code must not be empty.
            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM staging.stg_transactions
                WHERE ({date_filter})
                  AND TRIM(currency_code) = '';
                """,
                (transaction_date, transaction_date),
            )

            empty_currency_count = cursor.fetchone()[0]

            if empty_currency_count > 0:
                failures.append(
                    f"{empty_currency_count} transaction(s) have "
                    "an empty currency_code."
                )

            # 8. Currency code must be a valid 3-letter uppercase code.
            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM staging.stg_transactions
                WHERE ({date_filter})
                  AND (
                      LENGTH(TRIM(currency_code)) != 3
                      OR TRIM(currency_code) !~ '^[A-Z]{{3}}$'
                  );
                """,
                (transaction_date, transaction_date),
            )

            invalid_currency_count = cursor.fetchone()[0]

            if invalid_currency_count > 0:
                failures.append(
                    f"{invalid_currency_count} transaction(s) have "
                    "an invalid currency_code."
                )

            if failures:
                message = "Data quality validation failed:\n" + "\n".join(
                    f"- {failure}"
                    for failure in failures
                )

                raise DataQualityError(message)

        conn.commit()

    return row_count