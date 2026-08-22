from datetime import date

from finflow.database.connection import get_connection


def build_daily_transaction_metrics(
    transaction_date: date | None = None,
) -> int:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            if transaction_date is None:
                cursor.execute(
                    """
                    SELECT DISTINCT transaction_date
                    FROM analytics.fact_transactions
                    ORDER BY transaction_date;
                    """
                )
                dates = [row[0] for row in cursor.fetchall()]
            else:
                dates = [transaction_date]

            affected_count = 0

            for metric_date in dates:
                cursor.execute(
                    """
                    INSERT INTO analytics.daily_transaction_metrics (
                        transaction_date,
                        transaction_count,
                        total_transaction_amount,
                        total_transaction_fee,
                        average_transaction_amount,
                        average_transaction_fee
                    )
                    SELECT
                        transaction_date,
                        COUNT(*),
                        SUM(transaction_amount),
                        SUM(transaction_fee),
                        AVG(transaction_amount),
                        AVG(transaction_fee)
                    FROM analytics.fact_transactions
                    WHERE transaction_date = %s
                    GROUP BY transaction_date
                    ON CONFLICT (transaction_date) DO UPDATE
                    SET
                        transaction_count = EXCLUDED.transaction_count,
                        total_transaction_amount = EXCLUDED.total_transaction_amount,
                        total_transaction_fee = EXCLUDED.total_transaction_fee,
                        average_transaction_amount =
                            EXCLUDED.average_transaction_amount,
                        average_transaction_fee =
                            EXCLUDED.average_transaction_fee
                    WHERE
                        analytics.daily_transaction_metrics.transaction_count
                            IS DISTINCT FROM EXCLUDED.transaction_count
                        OR analytics.daily_transaction_metrics.total_transaction_amount
                            IS DISTINCT FROM EXCLUDED.total_transaction_amount
                        OR analytics.daily_transaction_metrics.total_transaction_fee
                            IS DISTINCT FROM EXCLUDED.total_transaction_fee
                        OR analytics.daily_transaction_metrics.average_transaction_amount
                            IS DISTINCT FROM EXCLUDED.average_transaction_amount
                        OR analytics.daily_transaction_metrics.average_transaction_fee
                            IS DISTINCT FROM EXCLUDED.average_transaction_fee
                    RETURNING transaction_date;
                    """,
                    (metric_date,),
                )

                if cursor.fetchone() is not None:
                    affected_count += 1

        conn.commit()

    return affected_count