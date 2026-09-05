select
    merchant_id,
    count(*) as transaction_count,
    sum(transaction_amount) as total_transaction_amount,
    sum(transaction_fee) as total_transaction_fee,
    avg(transaction_amount) as average_transaction_amount,
    sum(net_transaction_amount) as total_net_transaction_amount
from {{ ref('fct_transactions') }}
group by merchant_id
order by total_transaction_amount desc
