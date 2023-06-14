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

# Endpoint to select all notifications from the notify table  --> combination of inventory and sales
@app.route('/notify', methods=['GET'])
def get_notifications():
    try:
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

            # Retrieve the stock from the product table in the inventory database
            inventory_cursor = inventory_cnx.cursor()
            select_stock_query = "SELECT stock FROM product WHERE product_id = %s"
            inventory_cursor.execute(select_stock_query, (row[1],))
            stock_row = inventory_cursor.fetchone()
            inventory_cursor.close()

            # Add the stock information to the notification
            notification['stock'] = stock_row[0] if stock_row else None

            notifications.append(notification)

        return jsonify(notifications)

    except mysql.connector.Error as err:
        # Handle any errors that occur during the database operation
        return jsonify({'error': f"An error occurred: {err}"}), 500


# Endpoint to select all request tasks with status 'waiting' from the request_task table --> AMAN  --> ini udah digabung antar inventory sama employee
@app.route('/request_task', methods=['GET'])
def get_requests():
    cursor = inventory_cnx.cursor()
    select_query = "SELECT request_id, employee_id, detail, status FROM request_task WHERE status = 'Waiting'"
    cursor.execute(select_query)
    rows = cursor.fetchall()
    cursor.close()

    requests = []
    for row in rows:
        employee_id = row[1]
        employee_cursor = employee_cnx.cursor()
        select_employee_query = "SELECT name FROM employee_list WHERE employee_id = %s"
        employee_cursor.execute(select_employee_query, (employee_id,))
        employee_row = employee_cursor.fetchone()
        employee_cursor.close()

        request = {
            'request_id': row[0],
            'employee_id': employee_id,
            'employee_name': employee_row[0],
            'detail': row[2],
            'status': row[3]
        }
        requests.append(request)

    return jsonify(requests)

# Endpoint to update the status in the request_task table  --> HAHA AMAN  --> ini juga gabung antar inventory sama employee, employee add malah
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

        if status == 'Confirmed':
            select_query = "SELECT employee_id, detail FROM request_task WHERE request_id = %s"
            cursor.execute(select_query, (request_id,))
            row = cursor.fetchone()

            if row:
                employee_id = row[0]
                task = row[1]

                employee_cursor = employee_cnx.cursor()
                insert_query = "INSERT INTO task (employee_id, task, task_status) VALUES (%s, %s, 'On Progress')"
                employee_cursor.execute(insert_query, (employee_id, task))
                employee_cnx.commit()
                employee_cursor.close()

        cursor.close()

        return jsonify({'message': 'Request status updated successfully'})

    except mysql.connector.Error as err:
        # Handle any errors that occur during the database operation
        return jsonify({'error': f"An error occurred: {err}"}), 500
    
    
# Endpoint to update the detail in the notify table  --> ini juga aman tapi kayaknya lupa ss
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



# API gabungan 
# GET --> cek request --> select all dari request table inventory gabungin sama nama employee dari employee database
# PUT --> accept request --> update di request table di inventory, add new row of task di table sales
# GET --> cek catalog --> gabungin catalog sama stock
# POST --> booking --> pas di post langsung masuk ke bookinglist sama shipping, dan juga langsung ngurangin stock
# GET --> cek notify --> select all dari notify table sales, digabung dengan stock untuk memastikan