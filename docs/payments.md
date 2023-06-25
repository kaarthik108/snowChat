**Table 3: STREAM_HACKATHON.STREAMLIT.PAYMENTS** (Stores payment information)

This table contains information about payments made by customers for their orders, including the date and amount of each payment.

- PAYMENT_ID: Number (38,0) [Primary Key, Not Null] - Unique identifier for payments
- ORDER_ID: Number (38,0) [Foreign Key - ORDER_DETAILS(ORDER_ID)] - Associated order for the payment
- PAYMENT_DATE: Date - Date when the payment was made
- AMOUNT: Number (10,2) - Amount of the payment