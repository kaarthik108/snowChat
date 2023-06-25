**Table 5: STREAM_HACKATHON.STREAMLIT.TRANSACTIONS** (Stores transaction information)

This table contains information about individual transactions that occur when customers purchase products, including the associated order, product, quantity, and price.

- TRANSACTION_ID: Number (38,0) [Primary Key, Not Null] - Unique identifier for transactions
- ORDER_ID: Number (38,0) [Foreign Key - ORDER_DETAILS(ORDER_ID)] - Associated order for the transaction
- PRODUCT_ID: Number (38,0) - Product involved in the transaction
- QUANTITY: Number (38,0) - Quantity of the product in the transaction
- PRICE: Number (10,2) - Price of the product in the transaction
