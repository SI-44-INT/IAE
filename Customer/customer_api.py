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


@app.route('/catalog', methods=['GET'])
def get_catalog():
    try:
        # Create a cursor to execute SQL queries
        cursor = cnx.cursor()

        # Execute the SQL query to retrieve all rows from the catalog table
        query = 'SELECT * FROM catalog'
        cursor.execute(query)

        # Fetch all the rows from the result set
        rows = cursor.fetchall()

        # Close the cursor and database connection
        cursor.close()
        cnx.close()

        # Convert the rows to a list of dictionaries
        catalog = []
        for row in rows:
            catalog.append({
                'id': row[0],
                'name': row[1],
                'price': row[2]
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

        # Create a cursor to execute SQL queries
        cursor = cnx.cursor()

        # Retrieve the customer_id and customer_address based on the provided customer name
        get_customer_query = "SELECT customer_id, address FROM customer WHERE name = %s"
        cursor.execute(get_customer_query, (name,))
        customer_data = cursor.fetchone()

        # Check if customer exists
        if not customer_data:
            return jsonify({'error': 'Customer not found'}), 404

        # Extract the customer_id and customer_address
        customer_id = customer_data[0]
        customer_address = customer_data[1]

        # Initialize variables for storing products and total prices
        products = []
        total_price = 0

        # Iterate over the product data
        for item in product_data:
            # Extract the product name and quantity
            product_name = item.get('name')
            quantity = item.get('quantity')

            # Retrieve the product price from the catalog table
            get_price_query = "SELECT price FROM catalog WHERE product_name = %s"
            cursor.execute(get_price_query, (product_name,))
            price_data = cursor.fetchone()

            # Check if product exists
            if not price_data:
                return jsonify({'error': f'Product "{product_name}" not found'}), 404

            # Calculate the total price for the current product
            price = price_data[0]
            total_product_price = price * quantity

            # Append the product name and quantity to the products list
            products.append(f'{product_name}({quantity})')

            # Add the total product price to the overall total price
            total_price += total_product_price

        # Insert the booking data into the bookinglist table
        insert_query = "INSERT INTO bookinglist (customer_id, customer_name, products, total_price, customer_address, customer_order) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (customer_id, name, ', '.join(products), total_price, customer_address, 'Waiting'))
        cnx.commit()

        # Close the cursor
        cursor.close()

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
