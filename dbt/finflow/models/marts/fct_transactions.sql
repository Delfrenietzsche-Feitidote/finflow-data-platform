select
    transaction_id,
    customer_id,
    account_id,
    merchant_id,
    payment_method_code,
    currency_code,

    transaction_timestamp,
    transaction_date,
    transaction_month,
    transaction_year,

    transaction_amount,
    transaction_fee,
    fee_rate,
    net_transaction_amount,
    exchange_rate,

    created_at

from {{ ref('int_transactions_enriched') }}
