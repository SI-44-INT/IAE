def run_inventory():

    import mysql.connector
    import pandas as pd

    # Connect to the MySQL database
    cnx = mysql.connector.connect(
        host='db4free.net',
        user='si44_iae',
        password='si44inventory',
        database='si44_inventory'
    )

    # Function to update the stock of a product
    def update_product_stock(product_id, new_stock):
        update_query = "UPDATE product SET stock = %s WHERE product_id = %s"
        values = (new_stock, product_id)

        cursor = cnx.cursor()
        cursor.execute(update_query, values)
        cnx.commit()

        print("Product stock updated successfully")

    # Function to add a new order
    def add_shipping(product_id, quantity):
        # Check if the product exists and has sufficient stock
        check_query = "SELECT stock FROM product WHERE product_id = %s"
        values = (product_id,)

        cursor = cnx.cursor()
        cursor.execute(check_query, values)
        result = cursor.fetchone()

        if result is None:
            print("Product not found")
            return

        current_stock = result[0]

        if quantity > current_stock:
            print("Insufficient stock")
            return

        # Update the stock and add the order
        new_stock = current_stock - quantity
        update_product_stock(product_id, new_stock)

        # Add the order to the database
        insert_query = "INSERT INTO shipping (product_id, quantity, package_status) VALUES (%s, %s, %s)"
        status = "Prepared"
        values = (product_id, quantity, status)

        cursor.execute(insert_query, values)
        cnx.commit()

        print("Order added successfully")

    # Function to display the product list
    def display_product_list():
        query = "SELECT * FROM product"
        cursor = cnx.cursor()
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            print("No products found")
            return

        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(result, columns=columns)
        print(df)

    # Function to display the product list based on product ID
    def display_product_list_id(product_id):
        cursor = cnx.cursor()

        query = "SELECT * FROM product WHERE product_id = %s"
        values = (product_id,)

        cursor.execute(query, values)
        result = cursor.fetchall()

        if not result:
            print("No product found")
            cursor.close()
            cnx.close()
            return

        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(result, columns=columns)
        print(df)

    # Function to add a new product
    def add_product(product_name, stock):
        cursor = cnx.cursor()

        # Insert new product into the database
        query = "INSERT INTO product (product_name, stock) VALUES (%s, %s)"
        values = (product_name, stock)

        cursor.execute(query, values)
        cnx.commit()

        print("Product added successfully")

    # Function to update a product
    def update_product(product_id, product_name=None, stock=None):
        cursor = cnx.cursor()

        # Construct the UPDATE query based on the provided values
        query = "UPDATE product SET"
        update_values = []

        if product_name is not None:
            query += " product_name = %s,"
            update_values.append(product_name)

        if stock is not None:
            query += " stock = %s,"
            update_values.append(stock)

        # Remove the trailing comma from the query
        query = query.rstrip(',')

        # Add the WHERE clause to update the specific product
        query += " WHERE product_id = %s"
        update_values.append(product_id)

        # Execute the update query
        cursor.execute(query, update_values)
        cnx.commit()

        print("Product updated successfully")


    # Function to delete a product
    def delete_product(product_id):
        cursor = cnx.cursor()

        # Delete product from the database
        query = "DELETE FROM product WHERE product_id = %s"
        values = (product_id,)

        cursor.execute(query, values)
        cnx.commit()

        print("Product deleted successfully")

    # Function to show all orders
    def select_all_orders():
        query = "SELECT * FROM orders"
        cursor = cnx.cursor()
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            print("No orders found")
            return

        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(result, columns=columns)
        print(df)

    # function to add a new batch or product
    def add_order(booking_id, quantity):
        # Create a cursor object
        cursor = cnx.cursor()

        # Prepare the SQL query to insert a new row
        insert_query = "INSERT INTO orders (product_id, quantity, status) VALUES (%s, %s, %s)"

        # Define the values for the new row
        status = 'On Progress'
        values = (booking_id, quantity, status)

        # Execute the query with the provided values
        cursor.execute(insert_query, values)

        # Commit the changes to the database
        cnx.commit()

        # Close the cursor (no need to close the database connection here)

        print("New order added to the orders table.")

    # change order status to complete
    def update_order_status(order_id):
        # Create a cursor object
        cursor = cnx.cursor()

        # Prepare the SQL query to update the status of the order
        update_query = "UPDATE orders SET status = %s WHERE order_id = %s"

        new_status = "Completed"
        # Execute the query with the provided values
        cursor.execute(update_query, (new_status, order_id))

        # Commit the changes to the database
        cnx.commit()

        product_id_query = "SELECT product_id FROM orders WHERE order_id = %s"
        cursor.execute(product_id_query, (order_id,))
        product_id = cursor.fetchone()[0]

        quantity_query = "SELECT quantity FROM orders WHERE order_id = %s"
        cursor.execute(quantity_query, (order_id,))
        quantity = cursor.fetchone()[0]

        add_stock_query = "UPDATE product SET stock = stock + %s WHERE product_id = %s"
        cursor.execute(add_stock_query, (quantity, product_id))
        
        # Commit the changes to the database
        cnx.commit()

        # Close the cursor (no need to close the database connection here)

        print("Order status updated successfully.")

    # show all receipt
    def select_all_receipt():
        query = "SELECT * FROM receipt"
        cursor = cnx.cursor()
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            print("No receipt found")
            return

        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(result, columns=columns)
        print(df)

    def add_receipt(order_id, received_quantity):
        # Create a cursor object
        cursor = cnx.cursor()

        # Prepare the SQL query to insert a new row
        insert_query = "INSERT INTO receipt (order_id, received_quantity, status) VALUES (%s, %s, %s)"

        # Define the values for the new row
        status = 'Received'
        values = (order_id, received_quantity, status)

        # Execute the query with the provided values
        cursor.execute(insert_query, values)

        # Commit the changes to the database
        cnx.commit()

        # Close the cursor (no need to close the database connection here)

        print("New receipt added to the receipt table.")

    def change_receipt_status(receipt_id, new_status):
        # Create a cursor object
        cursor = cnx.cursor()

        # Prepare the SQL query to retrieve the person in charge for the given receipt ID
        select_query = "SELECT person_in_charge FROM receipt WHERE receipt_id = %s"

        # Execute the query with the provided receipt ID
        cursor.execute(select_query, (receipt_id,))
        
        # Fetch the person in charge from the query result
        person_in_charge = cursor.fetchone()[0]
        
        # Check if the person in charge is not empty
        if person_in_charge:
            # Validate the new_status
            accepted_statuses = ['Discrepancy', 'Returned', 'Warning', 'Completed']
            if new_status in accepted_statuses:
                # Prepare the SQL query to update the status of the receipt
                update_query = "UPDATE receipt SET status = %s WHERE receipt_id = %s"

                # Execute the query with the provided values
                cursor.execute(update_query, (new_status, receipt_id))

                # If the new_status is 'Completed', update the request_task table
                if new_status == 'Completed':
                    # Retrieve the request_id from the receipt table
                    select_request_id_query = "SELECT request_id FROM receipt WHERE receipt_id = %s"
                    cursor.execute(select_request_id_query, (receipt_id,))
                    request_id = cursor.fetchone()[0]
                    
                    # Update the status in the request_task table
                    update_request_status_query = "UPDATE request_task SET status = 'Completed' WHERE request_id = %s"
                    cursor.execute(update_request_status_query, (request_id,))
                    
                    print(f"Receipt {receipt_id} status updated to {new_status}. Request {request_id} status also updated to 'Completed'.")
                else:
                    print(f"Receipt {receipt_id} status updated to {new_status}.")
                
                # Commit the changes to the database
                cnx.commit()
            else:
                print("Invalid new status. Only 'Discrepancy', 'Returned', 'Warning', or 'Completed' are accepted.")
        else:
            print(f"Cannot update receipt status. Person in charge for receipt {receipt_id} is empty.")

        # Close the cursor (no need to close the database connection here)

    def assign_employee_to_receipt(receipt_id, request_id, person_in_charge):
        # Create a cursor object
        cursor = cnx.cursor()

        # Check if the request exists in the request_task table
        select_request_query = "SELECT status FROM request_task WHERE request_id = %s AND employee_id = %s"
        cursor.execute(select_request_query, (request_id, person_in_charge))
        request_result = cursor.fetchone()

        if request_result:
            request_status = request_result[0]
            if request_status == 'Rejected':
                print("Cannot assign employee to receipt. The request is rejected.")
            else:
                # Update the person_in_charge and request_id in the receipt table
                update_receipt_query = "UPDATE receipt SET person_in_charge = %s, request_id = %s WHERE receipt_id = %s"
                cursor.execute(update_receipt_query, (person_in_charge, request_id, receipt_id))
                cnx.commit()
                print(f"Employee {person_in_charge} assigned to receipt {receipt_id}.")
        else:
            print("Cannot assign employee to receipt. Request not found in the request_task table.")

        # Close the cursor (no need to close the database connection here)

    def select_all_shipping():
        # Create a cursor object
        cursor = cnx.cursor()

        # Prepare the SQL query to select all rows from the shipping table
        select_query = "SELECT * FROM shipping"

        # Execute the query
        cursor.execute(select_query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Close the cursor (no need to close the database connection here)

        # Create a DataFrame from the fetched rows
        df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])

        # Display the DataFrame
        print(df)

    def add_items_to_shipping(booking_id, items):
        # Create a cursor object
        cursor = cnx.cursor()

        for item in items:
            product, quantity = item.split(" (")
            quantity = int(quantity[:-1])  # Remove the closing parenthesis and convert to int

            # Check if the product exists in the product table
            select_query = "SELECT * FROM product WHERE product_name = %s"
            cursor.execute(select_query, (product,))
            result = cursor.fetchone()

            if result is not None:
                # Extract the current stock from the result
                current_stock = result[2]

                # Check if the quantity is not more than the stock
                if quantity <= current_stock:
                     # Join the items list using a comma separator
                    products = ', '.join(items)

                    # Insert a new row in the shipping table
                    insert_query = "INSERT INTO shipping (booking_id, products, package_status) VALUES (%s, %s, %s)"
                    status = "Preparing"
                    cursor.execute(insert_query, (booking_id, products, status))

                    # Update the stock in the product table
                    updated_stock = current_stock - quantity
                    update_query = "UPDATE product SET stock = %s WHERE product_name = %s"
                    cursor.execute(update_query, (updated_stock, product))

                    print(f"{item} added to the shipping table.")

                else:
                    print(f"Insufficient stock for {item}.")
            else:
                print(f"{product} does not exist in the product table.")

        # Commit the changes to the database
        cnx.commit()

        # Close the cursor (no need to close the database connection here)
        cursor.close()

    def assign_employee_to_shipping(shipping_id, request_id, person_in_charge):
        # Create a cursor object
        cursor = cnx.cursor()

        # Check if the request exists in the request_task table
        select_request_query = "SELECT status FROM request_task WHERE request_id = %s AND employee_id = %s"
        cursor.execute(select_request_query, (request_id, person_in_charge))
        request_result = cursor.fetchone()

        if request_result:
            request_status = request_result[0]
            if request_status == 'Rejected':
                print("Cannot assign employee to receipt. The request is rejected.")
            else:
                # Update the person_in_charge and request_id in the receipt table
                update_receipt_query = "UPDATE shipping SET person_in_charge = %s, request_id = %s WHERE shipping_id = %s"
                cursor.execute(update_receipt_query, (person_in_charge, request_id, shipping_id))
                cnx.commit()
                print(f"Employee {person_in_charge} assigned to receipt {shipping_id}.")
        else:
            print("Cannot assign employee to receipt. Request not found in the request_task table.")

        # Close the cursor (no need to close the database connection here)

    def change_package_status(booking_id, new_status):
        # Create a cursor object
        cursor = cnx.cursor()

        # Update the package status in the shipping table
        update_query = "UPDATE shipping SET package_status = %s WHERE booking_id = %s"
        cursor.execute(update_query, (new_status, booking_id))

        # Commit the changes to the database
        cnx.commit()

        # Close the cursor (no need to close the database connection here)
        cursor.close()

        print(f"Package status updated to {new_status} for booking ID {booking_id}.")

    def select_all_request():
        # Create a cursor object
        cursor = cnx.cursor()

        # Prepare the SQL query to select all rows from the shipping table
        select_query = "SELECT * FROM request_task"

        # Execute the query
        cursor.execute(select_query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Close the cursor (no need to close the database connection here)

        # Create a DataFrame from the fetched rows
        df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])

        print(df)

    def add_request(employee_id, detail):
        # Create a cursor object
        cursor = cnx.cursor()

        # Prepare the SQL query to insert a new row
        insert_query = "INSERT INTO request_task (employee_id, detail, status) VALUES (%s, %s, 'Waiting')"

        # Execute the query with the provided values
        cursor.execute(insert_query, (employee_id, detail))

        # Commit the changes to the database
        cnx.commit()

        # Close the cursor (no need to close the database connection here)
        cursor.close()

        print("New request added to the request task table.")



    while True:
        print("""Display:
        1. Products
        2. Orders
        3. Receipt
        4. Shipping
        5. Request Task
        
        0. Exit""")
        inventory = int(input("Welcome to Inventory: "))

        if inventory == 1:
            while True:
                print("""
                1. Products List Detail
                2. Add Product
                3. Update Product
                4. Delete Product
                
                0. Exit""")
                choice = int(input("Please input your choice: "))

                if choice == 1:
                    ask = input("Do you want to seek specific product? (y/n) ")
                    if ask == "y":
                        id = int(input("Please input the product ID: "))
                        display_product_list_id(id)
                    elif ask == "n":
                        display_product_list()

                elif choice == 2:
                    name = input("Please input the product's name: ")
                    stock = int(input("Please input the product's stock: "))
                    add_product(name, stock)

                elif choice == 3:
                    id = int(input("Please input the product's ID: "))
                    print("""What do you want to update?
                    1. Product Name
                    2. Stock
                    3. Both""")
                    ask = int(input("What do you want to change? "))
                    if ask == 1: 
                        name = input("Please input the name: ")
                        update_product(id, product_name=name, stock=None)

                    elif ask == 2:
                        stock = int(input("Please input the stock: "))
                        update_product(id, product_name=None, stock=stock)

                    elif ask == 3:
                        name = input("Please input the name: ")
                        stock = int(input("Please input the stock: "))
                        update_product(id, name, stock)

                elif choice == 4:
                    id = int(input("Please input the product's ID: "))
                    delete_product(id)

                elif choice == 0:
                    break


        elif inventory == 2:
            while True:
                print("""
                1. Order history
                2. Add new batch of product
                3. Change order status
                
                0. Exit""")
                choice = int(input("Please input your choice: "))
                if choice == 1:
                    select_all_orders()

                elif choice == 2:
                    id = int(input("Please input the product's ID: "))
                    quantity = int(input("Please input the desired quantity: "))
                    add_order(id, quantity)

                elif choice == 3:
                    id = int(input("Please input the order's ID: "))
                    change = input("Change order status to Completed? (y/n) ")
                    if change == "y":
                        update_order_status(id)

                elif choice == 0:
                    break


        elif inventory == 3:
            while True:
                print("""
                1. Receipts list
                2. Add new receipt
                3. Assign person in charge for the receipt
                4. Change receipt status
                
                0. Exit""")
                receipt = int(input("Please input your choice: "))
                if receipt == 1:
                    select_all_receipt()

                elif receipt == 2:
                    id = int(input("Please input the order's ID: "))
                    quantity = int(input("Please input the quantity received"))
                    add_receipt(id, quantity)

                elif receipt == 3:
                    id = int(input("Please input the receipt's ID: "))
                    id_request = int(input("Please input the request's ID: "))
                    employee = int(input("Please input the person in charge's employee iD: "))
                    assign_employee_to_receipt(id, id_request, employee)

                elif receipt == 4:
                    id = int(input("Please input the receipt's ID: "))
                    print("""
                    Received    = goods arrived but not yet to be inspected
                    Discrepancy = goods quantity not match with the order
                    Returned    = goods are not appropriated (damaged)
                    Warning     = goods not appropriated and wrong quantity
                    Completed   = goods approriated and ready to sell""")
                    status = input("Change status to: ")
                    change_receipt_status(id, status)

                elif receipt == 0: 
                    break

                
        elif inventory == 4:
            while True:
                print("""
                1. Shipping history
                2. Add new shipping order
                3. Assign person in charge for the package
                4. Change shipping status
                
                0. Exit""")
                shipping = int(input("Please input your choice: "))
                if shipping == 1:
                    select_all_shipping()

                elif shipping == 2:
                    id = int(input("Please input the booking's ID: "))
                    products = int(input("How many item? "))
                    items = []
                    for i in range(products):
                        product = input("Input the product name: ")
                        quantity = int(input("Input the quantity: "))
                        item = f"{product} ({quantity})"
                        items.append(item)

                    add_items_to_shipping(id, items)

                elif shipping == 3:
                    id = int(input("Please input the order's ID: "))
                    id_request = int(input("Please input the request's ID: "))
                    employee = int(input("Please input the person in charge's employee iD: "))
                    assign_employee_to_shipping(id, id_request, employee)

                elif shipping == 4:
                    id = int(input("Please input the order's ID: "))
                    status = input("Change the package status to: ")
                    change_package_status(id, status)

                elif shipping == 0:
                    break



        elif inventory == 5:
            while True:
                print("""
                1. Request list
                2. Add new request
                
                0. Exit""")
                request = int(input("Please input your choice"))
                if request == 1:
                    select_all_request()

                elif request == 2:
                    id = int(input("Please input the employee's ID: "))
                    print("""Detail example:
                    Shipping ID 7
                    Receipt ID 3""")
                    detail = input("Please input the detail: ")
                    add_request(id, detail)

                elif request == 0:
                    break


        elif inventory == 0:
            break
