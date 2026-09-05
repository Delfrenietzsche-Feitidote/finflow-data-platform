with ranked as (
    select
        transaction_id,
        customer_id,
        account_id,
        merchant_id,
        currency_code,
        payment_method_code,
        transaction_timestamp,
        transaction_amount,
        transaction_fee,
        exchange_rate,
        created_at,
        row_number() over (
            partition by transaction_id
            order by created_at desc
        ) as rn
    from {{ source('raw', 'transactions') }}
)

select
    transaction_id,
    customer_id,
    account_id,
    merchant_id,
    currency_code,
    payment_method_code,
    transaction_timestamp,
    date(transaction_timestamp) as transaction_date,
    transaction_amount,
    transaction_fee,
    exchange_rate,
    created_at
from ranked
where rn = 1
