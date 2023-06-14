def run_sales():

    import mysql.connector
    import pandas as pd

    # Connect to the MySQL database
    cnx = mysql.connector.connect(
        host='db4free.net',
        user='si44_ecommerce',
        password='si44sales',
        database='si44_sales'
    )

    # Function to display the table in the terminal using Pandas
    def display_table(table_name):
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, cnx)
        print(df)

    # Function to insert a new product into the Catalog table
    def insert_product(product_id, product_name, price):
        insert_query = "INSERT INTO Catalog (product_id, product_name, price) VALUES (%s, %s, %s)"
        values = (product_id, product_name, price)

        cursor = cnx.cursor()
        cursor.execute(insert_query, values)
        cnx.commit()

        print("Product inserted successfully")

    # Function to update a product's price and name in the Catalog table
    def update_product_details(product_id, new_price=None, new_name=None):
        if new_price is None and new_name is None:
            print("No updates provided. Please provide either a new price or a new name.")
            return

        update_query = "UPDATE Catalog SET"
        values = ()
        
        if new_price is not None:
            update_query += " price = %s,"
            values += (new_price,)
        
        if new_name is not None:
            update_query += " product_name = %s,"
            values += (new_name,)
        
        # Remove the trailing comma and complete the query
        update_query = update_query.rstrip(",") + " WHERE product_id = %s"
        values += (product_id,)

        cursor = cnx.cursor()
        cursor.execute(update_query, values)
        cnx.commit()

        print("Product details updated successfully")

    # Function to delete a product from the Catalog table
    def delete_product(product_id):
        delete_query = "DELETE FROM catalog WHERE product_id = %s"
        values = (product_id,)

        cursor = cnx.cursor()
        cursor.execute(delete_query, values)
        cnx.commit()

        print("Product deleted successfully")

    # Function to update the booking status in the BookingList table
    def update_booking_status(booking_id):
        new_status = "Completed"

        update_query = "UPDATE bookinglist SET booking_status = %s WHERE booking_id = %s"
        values = (new_status, booking_id)

        cursor = cnx.cursor()
        cursor.execute(update_query, values)
        cnx.commit()

        print("Booking status updated successfully")

    # Function to update the customer order status in the BookingList table
    def update_customer_order(order_id):
        new_status = "Confirmed"

        update_query = "UPDATE bookinglist SET customer_order = %s WHERE booking_id = %s"
        values = (new_status, order_id)

        cursor = cnx.cursor()
        cursor.execute(update_query, values)
        cnx.commit()

        print("Customer order updated successfully")

    # Function to add a new discount
    def add_discount(product_id, discount):
        cursor = cnx.cursor()

        # Convert the percentage input to a decimal value
        discount_decimal = float(discount) / 100.0

        # Check if the product already has a discount
        cursor.execute("SELECT product_id FROM discount WHERE product_id = %s", (product_id,))
        result = cursor.fetchone()

        if result:
            print("A discount for this product already exists.")
        else:
            # Insert the new discount into the Discount table
            cursor.execute("INSERT INTO discount (product_id, discount) VALUES (%s, %s)", (product_id, discount_decimal))
            cnx.commit()

            print("New discount added successfully.")

    # Function to apply discount to a product
    def apply_discount(product_id):
        # Check if the product already has a discount applied
        cursor = cnx.cursor()
        cursor.execute("SELECT detail FROM catalog WHERE product_id = %s", (product_id,))
        result = cursor.fetchone()
        
        if result and result[0] == "discount applied":
            print("Discount already applied to this product.")
        else:
            # Retrieve the discount for the product from the Discount table
            cursor.execute("SELECT discount FROM discount WHERE product_id = %s", (product_id,))
            discount_result = cursor.fetchone()

            if discount_result:
                discount = discount_result[0]

                # Retrieve the price of the product from the Catalog table
                cursor.execute("SELECT price FROM catalog WHERE product_id = %s", (product_id,))
                price_result = cursor.fetchone()

                if price_result:
                    price = price_result[0]

                    # Calculate the discounted price
                    discounted_price = price * (1 - discount)

                    # Update the Catalog table with the discounted price and mark the product as having a discount applied
                    cursor.execute("UPDATE catalog SET price = %s, detail = 'discount applied' WHERE product_id = %s", (discounted_price, product_id))
                    cnx.commit()

                    print("Discount applied successfully. The new price is:", discounted_price)
                else:
                    print("Product not found in the catalog.")
            else:
                print("No discount available for this product.")


    # Function to add a new notification in the notify table
    def add_notification(product_id, message):
        insert_query = "INSERT INTO notify (product_id, message, detail) VALUES (%s, %s, 'On Progress')"
        values = (product_id, message)

        cursor = cnx.cursor()
        cursor.execute(insert_query, values)
        cnx.commit()

        print("Notification added successfully")



    while True:
            print("""Display:
            1. Catalog
            2. Discount
            3. Booking List
            4. Notice
            
            0. Exit""")

            choice = int(input("Welcome to Sales: "))
            if choice == 1:
                while True:
                    print("""
                    1. Display Catalog
                    2. Add Catalog
                    3. Update Catalog
                    4. Delete Catalog
                    
                    0. Exit""")

                    catalog = int(input("Welcome to Catalog: "))
                    if catalog == 1:
                        display_table("catalog")

                    elif catalog == 2:
                        product_id = input("Product ID: ")
                        product_name = input("Product Name: ")
                        price = float(input("Product's price: "))
                        insert_product(product_id, product_name, price)

                    elif catalog == 3:
                        product_id = input("Product ID: ")
                        print("""What do you want to updated?
                        1. Product Name
                        2. Product Price
                        3. Both""")
                        ask = int(input("Choose: "))
                        if ask == 1:
                            name = input("Product's name: ")
                            update_product_details(product_id, new_name = name)
                        elif ask == 2:
                            price = float(input("Product's price: "))
                            update_product_details(product_id, new_price = price)
                        elif ask == 3: 
                            name = input("Product's name: ")
                            price = float(input("Product's price: "))
                            update_product_details(product_id, new_price=price, new_name=name)
                        else:
                            print("Please make a choice between provided number")

                    elif catalog == 4:
                        product_id = input("Product ID: ")
                        delete_product(product_id)

                    elif catalog == 0:
                        break

                    else:
                        print("Please make a choice between provided number")
                        

            elif choice == 2:
                while True:
                    print("""
                    1. Display Dicount
                    2. Add Dicount
                    3. Apply Discount
                    
                    0. Exit""")
                    discount = int(input("Welcome to Discount: "))

                    if discount == 1:
                        display_table("discount")
                    
                    elif discount == 2:
                        id = int(input("Input product ID: "))
                        diskon = input("Input the new discount value: ") #contoh: 10%
                        add_discount(id, diskon)

                    elif discount == 3:
                        id = int(input("Input product ID: "))
                        apply_discount(id)

                    elif discount == 0:
                        break

                    else:
                        print("Please make a choice between provided number")
                        

            elif choice == 3:
                while True:
                    print("""
                    1. Display Booking List
                    2. Confirmed Customer Order
                    3. Update Booking Status
                    
                    0. Exit""")
                    
                    booking = int(input("Welcome to Booking List: "))
                    if booking == 1:
                        display_table("bookinglist")

                    elif booking == 2:
                        booking_id = int(input("Booking ID: "))
                        confirm = input("Do you want to confirm the booking? (y/n)")
                        if confirm == "y":
                            update_customer_order(booking_id)

                    elif booking == 3:
                        booking_id = int(input("Booking ID: "))
                        update_booking_status(booking_id)
                    
                    elif booking == 0:
                        break

                    else:
                        print("Please make a choice between provided number")

            
            elif choice == 4:
                print("""
                1. Display Notify List
                2. Add New Notification""")
                notif = int(input("Welcome to Notify: "))
                if notif == 1:
                    display_table("Notify")
                elif notif == 2:
                    id = int(input("Please input the product id: "))
                    message = input("What's the problem? ") #example: product empty
                    add_notification(id, message)


            elif choice == 0:
                break

            else:
                print("Please make a choice between provided number")


    # Close the MySQL connection
    cnx.close()



# update catalog baru bisa update harga --> update nama bisa ditambahkan --> prioritas kecil --> completed
# bagian diskon ditambahkan add new diskon --> prioritas kecil --> completed
# lebih baik setelah show discount table ditambahkan pilihan apply discount ke product --> prioritas tinggi --> completed
# belum ada booking API buat customer --> prioritas tinggi
## perlu ada platform untuk login as customer --> prioritas tinggi
## customer table --> prioritas tinggi --> completed
# setelah customer isi booking, sales liat dulu sebelum confirm --> prioritas sedang --> completed
# bikin table product notice --> ngasih tau ada product kosong --> prioritas sedang --> completed


# prosbis 1 product management
## open product stock dari inventory (API) --> open catalog table (sales) --> remove product dari catalog kalau stock kosong 
## --> open table diskon --> update harga di catalog
### tinggal API


# prosbis 2 order processing
## customer order --> masuk ke booking list table --> sales confirm dulu customer order --> update customer order to confirmed
## --> booking status baru bisa diconfirm setelah inventory shipping complete (API)
### belum buat dashboardnya --> completed
### harus update table booking list ditambahkan customer id
### tinggal API


# prosbis 3 customer management
## dasboard login/sign in --> customer sign in --> customer input data --> perlu ada try except disini --> jika salah return ke customer
## --> jika sudah login bisa menampilkan dashboard catalog --> berlanjut ke prosbis 2
### belum buat dashboardnya --> dashboard menggunakan API
### perlu buat table customer data --> completed




#TINGGAL CUSTOOOMMEERRRR SAMA APIIII SIALAANANISHUIQUIQ2DWVJ