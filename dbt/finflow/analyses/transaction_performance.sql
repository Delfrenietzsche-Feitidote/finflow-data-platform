select
    transaction_date,
    transaction_count,
    total_transaction_amount,
    total_transaction_fee,
    total_net_transaction_amount,
    average_transaction_amount,
    average_transaction_fee
from {{ ref('daily_transaction_metrics') }}
order by transaction_date desc
