class SnowChat:
    def __init__(self):
        self.ddl_dict = self.load_ddls()

    @staticmethod
    def load_ddls():
        ddl_files = {
            "TRANSACTIONS": "sql/ddl_transactions.sql",
            "ORDER_DETAILS": "sql/ddl_orders.sql",
            "PAYMENTS": "sql/ddl_payments.sql",
            "PRODUCTS": "sql/ddl_products.sql",
            "CUSTOMER_DETAILS": "sql/ddl_customer.sql"
        }

        ddl_dict = {}
        for table_name, file_name in ddl_files.items():
            with open(file_name, "r") as f:
                ddl_dict[table_name] = f.read()
        return ddl_dict
