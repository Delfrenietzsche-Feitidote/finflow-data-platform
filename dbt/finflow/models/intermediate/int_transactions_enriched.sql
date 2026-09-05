with transactions as (

    select
        transaction_id,
        customer_id,
        account_id,
        merchant_id,
        payment_method_code,
        currency_code,
        transaction_timestamp,
        transaction_date,
        transaction_amount,
        transaction_fee,
        exchange_rate,
        created_at
    from {{ ref('stg_transactions') }}

)

select
    transaction_id,
    customer_id,
    account_id,
    merchant_id,
    payment_method_code,
    currency_code,

    transaction_timestamp,
    transaction_date,
    date_trunc(transaction_date, month) as transaction_month,
    extract(year from transaction_date) as transaction_year,

    transaction_amount,
    transaction_fee,
    exchange_rate,

    safe_divide(transaction_fee, transaction_amount) as fee_rate,
    transaction_amount - transaction_fee as net_transaction_amount,

    created_at

from transactions
