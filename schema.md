**Table 1: STREAM_HACKATHON.STREAMLIT.CUSTOMER_DETAILS** (Stores customer information)

This table contains the personal information of customers who have made purchases on the platform.

- CUSTOMER_ID: Number (38,0) [Primary Key, Not Null] - Unique identifier for customers
- FIRST_NAME: Varchar (255) - First name of the customer
- LAST_NAME: Varchar (255) - Last name of the customer
- EMAIL: Varchar (255) - Email address of the customer
- PHONE: Varchar (20) - Phone number of the customer
- ADDRESS: Varchar (255) - Physical address of the customer

**Table 2: STREAM_HACKATHON.STREAMLIT.ORDER_DETAILS** (Stores order information)

This table contains information about orders placed by customers, including the date and total amount of each order.

- ORDER_ID: Number (38,0) [Primary Key, Not Null] - Unique identifier for orders
- CUSTOMER_ID: Number (38,0) [Foreign Key - CUSTOMER_DETAILS(CUSTOMER_ID)] - Customer who made the order
- ORDER_DATE: Date - Date when the order was made
- TOTAL_AMOUNT: Number (10,2) - Total amount of the order

**Table 3: STREAM_HACKATHON.STREAMLIT.PAYMENTS** (Stores payment information)

This table contains information about payments made by customers for their orders, including the date and amount of each payment.

- PAYMENT_ID: Number (38,0) [Primary Key, Not Null] - Unique identifier for payments
- ORDER_ID: Number (38,0) [Foreign Key - ORDER_DETAILS(ORDER_ID)] - Associated order for the payment
- PAYMENT_DATE: Date - Date when the payment was made
- AMOUNT: Number (10,2) - Amount of the payment

**Table 4: STREAM_HACKATHON.STREAMLIT.PRODUCTS** (Stores product information)

This table contains information about the products available for purchase on the platform, including their name, category, and price.

- PRODUCT_ID: Number (38,0) [Primary Key, Not Null] - Unique identifier for products
- PRODUCT_NAME: Varchar (255) - Name of the product
- CATEGORY: Varchar (255) - Category of the product
- PRICE: Number (10,2) - Price of the product

**Table 5: STREAM_HACKATHON.STREAMLIT.TRANSACTIONS** (Stores transaction information)

This table contains information about individual transactions that occur when customers purchase products, including the associated order, product, quantity, and price.

- TRANSACTION_ID: Number (38,0) [Primary Key, Not Null] - Unique identifier for transactions
- ORDER_ID: Number (38,0) [Foreign Key - ORDER_DETAILS(ORDER_ID)] - Associated order for the transaction
- PRODUCT_ID: Number (38,0) - Product involved in the transaction
- QUANTITY: Number (38,0) - Quantity of the product in the transaction
- PRICE: Number (10,2) - Price of the product in the transaction
