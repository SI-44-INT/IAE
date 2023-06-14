def run_employee():

    import mysql.connector
    import pandas as pd

    # Database connection configuration
    db_config = {
        'host': 'db4free.net',
        'user': 'si44int_iae', #sesuain punya sendiri
        'password': 'si44employee', #password mysql
        'database': 'si44_employee'
    }

    # Establish database connection
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    def show_employee_list():
        query = "SELECT * FROM employee_list"
        cursor.execute(query)
        result = cursor.fetchall()

        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(result, columns=columns)
        print(df)

    def update_employee_status(employee_id, new_status):
        query = "UPDATE employee_list SET status = %s WHERE employee_id = %s"
        values = (new_status, employee_id)
        cursor.execute(query, values)
        cnx.commit()
        print("Employee status updated successfully!")

    def add_absence(employee_id, month, absence, paid_leave):
        insert_query = "INSERT INTO absence (employee_id, month, absence, paid_leave) VALUES (%s, %s, %s, %s)"
        insert_values = (employee_id, month, absence, paid_leave)
        cursor.execute(insert_query, insert_values)
        cnx.commit()
        print("Absence added successfully!")

    def update_absence(employee_id, month, absence, paid_leave):
        update_query = "UPDATE absence SET absence = %s, paid_leave = %s WHERE employee_id = %s AND month = %s"
        update_values = (absence, paid_leave, employee_id, month)
        cursor.execute(update_query, update_values)
        cnx.commit()
        print("Absence updated successfully!")

    def add_task(employee_id, task):
        insert_query = "INSERT INTO task (employee_id, task, task_status) VALUES (%s, %s, 'On Progress')"
        insert_values = (employee_id, task)
        cursor.execute(insert_query, insert_values)
        cnx.commit()
        print("Task added successfully!")

    def update_task(task_id, task):
        update_query = "UPDATE task SET task_status = %s WHERE task_id = %s"
        update_values = (task, task_id)
        cursor.execute(update_query, update_values)
        cnx.commit()
        print("Task updated successfully!")

    def delete_task(task_id):
        delete_query = "DELETE FROM task WHERE task_id = %s"
        values = (task_id,)
        cursor.execute(delete_query, values)
        cnx.commit()
        print("Task deleted successfully!")

    def show_all_task():
        # SQL query to select data from task table and join with employee_list table
        query = """
        SELECT task.task_id, employee_list.employee_id, employee_list.name, task.task, task.task_status
        FROM task
        JOIN employee_list ON task.employee_id = employee_list.employee_id
        ORDER BY task.task_status DESC
        """

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the result
        result = cursor.fetchall()

        # Get the column names from the cursor description
        columns = [desc[0] for desc in cursor.description]

        # Create a DataFrame from the result
        df = pd.DataFrame(result, columns=columns)

        # Print the table using Pandas
        print("Combined Task and Employee List:")
        print(df)

    def show_tasks_id(employee_id):
        query = """
            SELECT task.task_id, employee_list.employee_id, employee_list.name, task.task, task.task_status
            FROM task
            JOIN employee_list ON task.employee_id = employee_list.employee_id
            WHERE employee_list.employee_id = %s
            ORDER BY task.task_status DESC
        """
        values = (employee_id,)

        # Execute the query
        cursor.execute(query, values)

        # Fetch all rows
        result = cursor.fetchall()

        # Create a pandas DataFrame from the query result
        df = pd.DataFrame(result, columns=["Task ID", "Employee ID", "Name", "Task", "Task Status"])

        # Display the DataFrame
        print(df)

    def show_absence():
        # SQL query to select all columns from absence table and add the name from employee_list table
        query = """
        SELECT absence.employee_id, employee_list.name, absence.month, absence.absence_days, absence.paid_leave_days
        FROM absence
        JOIN employee_list ON absence.employee_id = employee_list.employee_id
        """

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the result
        result = cursor.fetchall()

        # Get the column names from the cursor description
        columns = [desc[0] for desc in cursor.description]

        # Create a DataFrame from the result
        df = pd.DataFrame(result, columns=columns)

        # Print the table using Pandas
        print("Combined Absence and Employee List:")
        print(df)

    def add_absence(employee_id, month, days):
        # Check if absence record already exists for the employee and month
        check_query = "SELECT * FROM absence WHERE employee_id = %s AND month = %s"
        cursor.execute(check_query, (employee_id, month))
        record = cursor.fetchone()

        if record:
            # Update existing absence record
            current_absence = record[2]
            new_absence = current_absence + days

            update_query = "UPDATE absence SET absence = %s WHERE employee_id = %s AND month = %s"
            cursor.execute(update_query, (new_absence, employee_id, month))
            cnx.commit()

            print(f"Successfully added {days} days of absence for employee {employee_id}.")
            print(f"New total absence for {month}: {new_absence} days.")
        else:
            # Insert new absence record
            insert_query = "INSERT INTO absence (employee_id, month, absence) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (employee_id, month, days))
            cnx.commit()

            print(f"Successfully added {days} days of absence for employee {employee_id} in {month}.")

    def add_payroll(employee_id, gross_salary, payroll_date):
            try:
                # Calculate taxes
                tax = 0.15
                taxes = gross_salary * 0.15

                # Calculate net salary
                net_salary = gross_salary - taxes

                # Set default payroll status
                payroll_status = 'Waiting'

                # Create a cursor to execute SQL queries
                cursor = cnx.cursor()

                # Prepare the SQL query to insert a new payroll entry
                insert_query = "INSERT INTO payment (employee_id, gross_salary, taxes, net_salary, payroll_date, payroll_status) VALUES (%s, %s, %s, %s, %s, %s)"
                values = (employee_id, gross_salary, tax, net_salary, payroll_date, payroll_status)

                # Execute the query with the provided values
                cursor.execute(insert_query, values)

                # Commit the changes to the database
                cnx.commit()

                # Close the cursor and database connection
                cursor.close()
                cnx.close()

                print("New payroll added successfully.")

            except mysql.connector.Error as err:
                # Handle any errors that occur during the database operation
                print(f"An error occurred: {err}")

    def display_payments():
        query = "SELECT * FROM payment"
        cursor.execute(query)
        result = cursor.fetchall()

        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(result, columns=columns)
        print(df)

    def process_payment(payment_id, payment_date):
        try:
            # Create a cursor to execute SQL queries
            cursor = cnx.cursor()

            # Update the payroll status and payment status
            update_query = "UPDATE payment SET payroll_status = %s, payment_date = %s, payment_status = %s WHERE id = %s"

            payroll_status = "Confirmed"
            payment_status = "Completed"

            # Execute the query with the provided values
            cursor.execute(update_query, (payroll_status, payment_date, payment_status, payment_id))

            # Commit the changes to the database
            cnx.commit()

            # Close the cursor (no need to close the database connection here)
            cursor.close()

            print("Payment processed successfully.")

        except mysql.connector.Error as err:
            # Handle any errors that occur during the database operation
            print(f"An error occurred: {err}")


    while True:
        print("""Display:
        1. Employee List
        2. Absence
        3. Task
        4. Payment
        
        0. Exit""")
        employee = int(input("Welcome to Employee: "))
        if employee == 1:
            while True:
                print("""Display:
                1. Employee List
                2. Change Employee Status
                
                0. Exit""")
                choice = int(input("What do you seek in employee list? "))
                if choice == 1:
                    show_employee_list()
                elif choice == 2:
                    id = int(input("Insert employee id: "))
                    status = input("Change employee status to: ") #misal Warning
                    update_employee_status(id, status)

                elif choice == 0:
                    break

        elif employee == 2:
            while True:
                print("""Display:
                1. Absence list
                2. Add Absence
                
                0. Exit""")
                absence = int(input("What do you seek in absence? "))

                if absence == 1:
                    show_absence()

                elif absence == 2:
                    id = int(input("Insert employee id: "))
                    month = input("Insert the month: ")
                    days = int(input("Insert how many days he/she absence: "))
                    add_absence(id, month, days)

                elif absence == 0:
                    break

        elif employee == 3:
            while True:
                print("""Display:
                1. Employee Task
                2. Add Task
                3. Update Task
                
                0. Exit""")
                task = int(input("What do you seek in employee task? "))

                if task == 1:
                    ask = input("do you want to seek specific employee? (y/n) ") 
                    if ask == "y":
                        employee_id = int(input("Please input the employee ID: "))
                        show_tasks_id(employee_id)
                    
                    elif ask == "n":
                        show_all_task()

                elif task == 2:
                    id = int(input("Insert employee ID: "))
                    add = input("Add new task: ")
                    add_task(id, add)

                elif task == 3:
                    id = int(input("Insert employee ID: "))
                    update = input("Update task status: ")
                    update_task(id, update)

                elif task == 0:
                    break

        elif employee == 4:
            while True:
                print(""""Display:
                1. Payment List
                2. Add Payroll
                3. Payment""")
                pay = int(input("What do you seek in Payment? "))
                if pay == 1:
                    display_payments()

                elif pay == 2:
                    employee = int(input("Please input the employee's ID: "))
                    salary = int(input("Please input the gross salary: "))
                    date = input("Please input the date: ")
                    add_payroll(employee, salary, date)

                elif pay == 3: 
                    id = int(input("Please input the payment's ID: "))
                    date = input("Please input the date: ")
                    process_payment(id, date)


        elif employee == 0:
            break



# prosbis 1 task assignment and responsibilities
## check if there are task request for specific employee (cuman bisa dari inventory)(API) --> if the employee already has too many task 
## --> update the task to rejected (API) --> if diterima --> masuk ke table task
## bisa add new task sendiri juga
### belum bikin API


# prosbis 2 payroll and compensation management
## belom ini


# prosbis 3 attendance and warning process
## cek table absence --> employee absen <5 di bulan itu --> udah biarin aja --> employee absen >=5 --> cek cuti --> ada cuti --> aman
## g ada cuti --> kena status warning
## belum ada update paid leave