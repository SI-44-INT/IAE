print("""Welcome to ecommerce
1. Sales
2. Inventory
3. Employee""")
choice = int(input("Enter your choice: "))

if choice == 1:
    from Sales import Sales
    Sales.run_sales()
elif choice == 2:
    from Inventory import Inventory
    Inventory.run_inventory()
elif choice == 3:
    from Employee import Employee
    Employee.run_employee()
else:
    print("Invalid choice. Please enter a valid option.")
