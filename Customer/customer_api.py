from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

# Connect to the MySQL database
cnx = mysql.connector.connect(
    host='db4free.net',
    user='si44_ecommerce',
    password='si44sales',
    database='si44_sales'
)

inventory_cnx = mysql.connector.connect(
    host='db4free.net',
    user='si44_iae',
    password='si44inventory',
    database='si44_inventory'
)

# endpoint the get catalog and stock
@app.route('/catalog', methods=['GET'])
def get_catalog():
    try:
        # Create a cursor to execute SQL queries
        cursor_sales = cnx.cursor()
        cursor_inventory = inventory_cnx.cursor()

        # Execute the SQL query to retrieve all rows from the catalog table in the sales database
        query_sales = 'SELECT * FROM catalog'
        cursor_sales.execute(query_sales)
        rows_sales = cursor_sales.fetchall()

        # Fetch the product IDs from the catalog rows
        product_ids = [row[0] for row in rows_sales]

        # Execute the SQL query to retrieve the stock for the product IDs in the inventory database
        query_inventory = 'SELECT product_id, stock FROM product WHERE product_id IN ({})'.format(','.join(['%s'] * len(product_ids)))
        cursor_inventory.execute(query_inventory, product_ids)
        rows_inventory = cursor_inventory.fetchall()

        # Close the cursors (no need to close the database connections here)

        # Create a dictionary to store the stock values by product ID
        stock_dict = {row[0]: row[1] for row in rows_inventory}

        # Combine the results from both databases
        catalog = []
        for row_sales in rows_sales:
            product_id = row_sales[0]
            stock = stock_dict.get(product_id, 0)  # Get the stock value from the dictionary or default to 0 if not found
            catalog.append({
                'id': product_id,
                'name': row_sales[1],
                'price': row_sales[2],
                'stock': stock
                # Add more columns if necessary
            })

        # Return the catalog as a JSON response
        return jsonify(catalog)

    except mysql.connector.Error as err:
        # Handle any errors that occur during the database operation
        return f"An error occurred: {err}", 500


# Endpoint to insert customer data into the customer table
@app.route('/customer', methods=['POST'])
def create_customer():
    try:
        # Get the data from the request
        data = request.get_json()

        # Check if all required fields are provided
        if 'name' not in data or 'email' not in data or 'phone' not in data or 'address' not in data:
            return jsonify({'message': 'Data is deficient'}), 400

        # Extract the data from the request
        name = data['name']
        email = data['email']
        phone = data['phone']
        address = data['address']

        # Create a cursor to execute SQL queries
        cursor = cnx.cursor()

        # Execute the SQL query to insert data into the customer table
        insert_query = "INSERT INTO customer (name, email, phone, address) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (name, email, phone, address))
        cnx.commit()

        # Close the cursor
        cursor.close()

        return jsonify({'message': 'Customer data inserted successfully'}), 200

    except mysql.connector.Error as err:
        # Handle any errors that occur during the database operation
        return f"An error occurred: {err}", 500
    
# Endpoint for customer to add booking
@app.route('/bookinglist', methods=['POST'])
def create_booking():
    try:
        # Get the request data
        data = request.json

        # Extract the customer name, products, and quantity from the request data
        name = data.get('name')
        product_data = data.get('products')

        # Create a cursor for sales database connection
        sales_cursor = cnx.cursor()

        # Retrieve the customer_id and customer_address based on the provided customer name
        get_customer_query = "SELECT customer_id, address FROM customer WHERE name = %s"
        sales_cursor.execute(get_customer_query, (name,))
        customer_data = sales_cursor.fetchone()

        # Check if customer exists
        if not customer_data:
            return jsonify({'error': 'Customer not found'}), 404

        # Extract the customer_id and customer_address
        customer_id = customer_data[0]
        customer_address = customer_data[1]

        # Initialize variables for storing products and total prices
        products = []
        total_price = 0

        # Create a cursor for inventory database connection
        inventory_cursor = inventory_cnx.cursor()

        # Iterate over the product data
        for item in product_data:
            # Extract the product name and quantity
            product_name = item.get('name')
            quantity = item.get('quantity')

            # Retrieve the price from the catalog table in sales database
            get_price_query = "SELECT price FROM catalog WHERE product_name = %s"
            sales_cursor.execute(get_price_query, (product_name,))
            price_data = sales_cursor.fetchone()

            # Check if product exists
            if not price_data:
                return jsonify({'error': f'Product "{product_name}" not found'}), 404

            # Calculate the total price for the current product
            price = price_data[0]
            total_product_price = price * quantity

            # Retrieve the stock from the product table in inventory database
            get_stock_query = "SELECT stock FROM product WHERE product_name = %s"
            inventory_cursor.execute(get_stock_query, (product_name,))
            stock_data = inventory_cursor.fetchone()

            # Check if product exists
            if not stock_data:
                return jsonify({'error': f'Product "{product_name}" not found in inventory'}), 404

            # Extract the stock quantity
            stock = stock_data[0]

            # Check if the quantity exceeds the stock
            if quantity > stock:
                return jsonify({'error': f'Product "{product_name}" has limited stock'}), 400

            # Calculate the total price for the current product
            total_product_price = price * quantity

            # Reduce the stock quantity
            new_stock = stock - quantity
            update_stock_query = "UPDATE product SET stock = %s WHERE product_name = %s"
            inventory_cursor.execute(update_stock_query, (new_stock, product_name))
            inventory_cnx.commit()

            # Append the product name and quantity to the products list
            products.append(f'{product_name}({quantity})')

            # Add the total product price to the overall total price
            total_price += total_product_price

        # Insert the booking data into the bookinglist table in sales database
        insert_query = "INSERT INTO bookinglist (customer_id, customer_name, products, total_price, customer_address) VALUES (%s, %s, %s, %s, %s)"
        sales_cursor.execute(insert_query, (customer_id, name, ', '.join(products), total_price, customer_address))
        cnx.commit()

        # Get the newly generated booking_id
        booking_id = sales_cursor.lastrowid

        # Insert the shipping data into the shipping table in inventory database
        insert_shipping_query = "INSERT INTO shipping (booking_id, products, package_status) VALUES (%s, %s, %s)"
        inventory_cursor.execute(insert_shipping_query, (booking_id, ', '.join(products), 'On Progress'))
        inventory_cnx.commit()

        # Close the cursors
        sales_cursor.close()
        inventory_cursor.close()

        # Return a success response
        return jsonify({
            'message': 'Booking added successfully',
            'total_price': total_price
        })

    except mysql.connector.Error as err:
        # Handle any errors that occur during the database operation
        return jsonify({'error': f"An error occurred: {err}"}), 500


if __name__ == '__main__':
    app.run()
