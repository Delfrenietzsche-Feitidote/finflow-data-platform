select
    transaction_date,
    count(*) as transaction_count,
    sum(transaction_amount) as total_transaction_amount,
    sum(transaction_fee) as total_transaction_fee,
    avg(transaction_amount) as average_transaction_amount,
    avg(transaction_fee) as average_transaction_fee,
    sum(net_transaction_amount) as total_net_transaction_amount

from {{ ref('int_transactions_enriched') }}

group by transaction_date
