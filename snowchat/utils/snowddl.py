class Snowddl:
    """
    Snowddl class loads DDL files for various tables in a database.

    Attributes:
        ddl_dict (dict): dictionary of DDL files for various tables in a database.

    Methods:
        load_ddls: loads DDL files for various tables in a database.
    """

    def __init__(self):
        self.ddl_dict = self.load_ddls()

    @staticmethod
    def load_ddls():
        ddl_files = {
            "TRANSACTIONS": "sql/ddl_transactions.sql",
            "ORDER_DETAILS": "sql/ddl_orders.sql",
            "PAYMENTS": "sql/ddl_payments.sql",
            "PRODUCTS": "sql/ddl_products.sql",
            "CUSTOMER_DETAILS": "sql/ddl_customer.sql",
        }

        ddl_dict = {}
        for table_name, file_name in ddl_files.items():
            with open(file_name, "r") as f:
                ddl_dict[table_name] = f.read()
        return ddl_dict
