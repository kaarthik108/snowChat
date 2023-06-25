**Table 2: STREAM_HACKATHON.STREAMLIT.ORDER_DETAILS** (Stores order information)

This table contains information about orders placed by customers, including the date and total amount of each order.

- ORDER_ID: Number (38,0) [Primary Key, Not Null] - Unique identifier for orders
- CUSTOMER_ID: Number (38,0) [Foreign Key - CUSTOMER_DETAILS(CUSTOMER_ID)] - Customer who made the order
- ORDER_DATE: Date - Date when the order was made
- TOTAL_AMOUNT: Number (10,2) - Total amount of the order