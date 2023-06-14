# Sales
# cek product stok dari inventory
# cek package status dari inventory -- shipping


# inventory
# cek bookingn dari sales
# cek employee dari inventory -- buat shipping sama inspect goods
# cek notif dari sales -- notify


# employee
# cek request employee dari inventory 



from flask import Flask, jsonify, request
import mysql.connector

# Create a Flask app
app = Flask(__name__)


# Configure MySQL connections for each database
inventory_cnx = mysql.connector.connect(
    host='db4free.net',
    user='si44_iae',
    password='si44inventory',
    database='si44_inventory'
)

sales_cnx = mysql.connector.connect(
    host='db4free.net',
    user='si44_ecommerce',
    password='si44sales',
    database='si44_sales'
)

employee_cnx = mysql.connector.connect(
    host="db4free.net",
    user="si44int_iae",
    password="si44employee",
    database="si44_employee"
)

# Endpoint to select all products from the product table sorted by stock
@app.route('/product', methods=['GET'])
def get_products():
    cursor = inventory_cnx.cursor()
    select_query = "SELECT * FROM product ORDER BY stock"
    cursor.execute(select_query)
    rows = cursor.fetchall()
    cursor.close()
    inventory_cnx.close()

    products = []
    for row in rows:
        products.append({
            'product_id': row[0],
            'product_name': row[1],
            'stock': row[2]
        })

    return jsonify(products)

# Endpoint to select all shipments based on booking id
@app.route('/shipping/<booking_id>', methods=['GET'])
def get_shipments(booking_id):
    cursor = inventory_cnx.cursor()
    select_query = "SELECT shipping_id, booking_id, products, person_in_charge, package_status FROM shipping WHERE booking_id = %s"
    cursor.execute(select_query, (booking_id,))
    rows = cursor.fetchall()
    cursor.close()

    shipments = []
    for row in rows:
        shipment = {
            'shipping_id': row[0],
            'booking_id': row[1],
            'products': row[2],
            'person_in_charge': row[3],
            'package_status': row[4]
        }
        shipments.append(shipment)

    return jsonify(shipments)

# Endpoint to select all confirmed bookings from the bookinglist table
@app.route('/bookinglist', methods=['GET'])
def get_bookings():
    cursor = sales_cnx.cursor()
    select_query = "SELECT booking_id, customer_id, customer_name, products, total_price, customer_address, customer_order, booking_status FROM bookinglist WHERE booking_status = 'On Progress' and customer_order = 'Confirmed'"
    cursor.execute(select_query)
    rows = cursor.fetchall()
    cursor.close()

    bookings = []
    for row in rows:
        booking = {
            'booking_id': row[0],
            'customer_id': row[1],
            'customer_name': row[2],
            'products': row[3],
            'total_price': row[4],
            'customer_address': row[5],
            'customer_order': row[6],
            'booking_status': row[7]
        }
        bookings.append(booking)

    return jsonify(bookings)

# Endpoint to select all employees with the position 'Inventory' from the employee_list table
@app.route('/employee_list', methods=['GET'])
def get_employees():
    cursor = employee_cnx.cursor()
    select_query = "SELECT employee_id, name, position, status FROM employee_list WHERE position = 'Inventory'"
    cursor.execute(select_query)
    rows = cursor.fetchall()
    cursor.close()

    employees = []
    for row in rows:
        employee = {
            'employee_id': row[0],
            'name': row[1],
            'position': row[2],
            'status': row[3]
        }
        employees.append(employee)

    return jsonify(employees)

# Endpoint to select all notifications from the notify table
@app.route('/notify', methods=['GET'])
def get_notifications():
    cursor = sales_cnx.cursor()
    select_query = "SELECT id, product_id, message, detail FROM notify"
    cursor.execute(select_query)
    rows = cursor.fetchall()
    cursor.close()

    notifications = []
    for row in rows:
        notification = {
            'id': row[0],
            'product_id': row[1],
            'message': row[2],
            'detail': row[3]
        }
        notifications.append(notification)

    return jsonify(notifications)

# Endpoint to select all request tasks with status 'waiting' from the request_task table
@app.route('/request_task', methods=['GET'])
def get_requests():
    cursor = inventory_cnx.cursor()
    select_query = "SELECT request_id, employee_id, detail, status FROM request_task WHERE status = 'waiting'"
    cursor.execute(select_query)
    rows = cursor.fetchall()
    cursor.close()

    requests = []
    for row in rows:
        request = {
            'request_id': row[0],
            'employee_id': row[1],
            'detail': row[2],
            'status': row[3]
        }
        requests.append(request)

    return jsonify(requests)

# Endpoint to update the status in the request_task table
@app.route('/request_task', methods=['PUT'])
def update_request_status():
    data = request.json
    request_id = data.get('request_id')
    status = data.get('status')

    if not request_id or not status:
        return jsonify({'error': 'Request ID or status is missing.'}), 400

    try:
        cursor = inventory_cnx.cursor()
        update_query = "UPDATE request_task SET status = %s WHERE request_id = %s"
        cursor.execute(update_query, (status, request_id))
        inventory_cnx.commit()
        cursor.close()

        return jsonify({'message': 'Request status updated successfully'})

    except mysql.connector.Error as err:
        # Handle any errors that occur during the database operation
        return jsonify({'error': f"An error occurred: {err}"}), 500
    
    
# Endpoint to update the detail in the notify table
@app.route('/notify/<notification_id>', methods=['PUT'])
def update_notification_detail(notification_id):
    detail = request.json.get('detail')
    cursor = sales_cnx.cursor()
    update_query = "UPDATE notify SET detail = %s WHERE id = %s"
    cursor.execute(update_query, (detail, notification_id))
    sales_cnx.commit()
    cursor.close()

    return jsonify({'message': 'Notification detail updated successfully'})

# Run the Flask app
if __name__ == '__main__':
    app.run()

