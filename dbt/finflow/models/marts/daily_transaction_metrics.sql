select
    transaction_date,
    transaction_count,
    total_transaction_amount,
    total_transaction_fee,
    average_transaction_amount,
    average_transaction_fee,
    total_net_transaction_amount

from {{ ref('int_daily_transaction_summary') }}
