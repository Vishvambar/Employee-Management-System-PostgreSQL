"""
Interactive Command Line Interface (CLI) for Employee Management System.
Provides a comprehensive menu system for performing CRUD operations,
running analytical queries, and generating data visualizations.
"""

import sys
from tabulate import tabulate
from db_connection import test_connection
from models import DepartmentModel, RoleModel, EmployeeModel
from analytics import AnalyticsService
from visualizer import generate_all_visualizations
from seed_data import seed_database
from init_db import initialize_database


def clear_screen():
    print("\n" + "-" * 75)


def get_input(prompt: str, default: str = None) -> str:
    val = input(f"{prompt} " + (f"[{default}]: " if default else ": ")).strip()
    return val if val else (default if default is not None else "")


def print_table(data, headers="keys", title=None):
    if title:
        print(f"\n--- {title} ---")
    if not data:
        print("[!] No records found.")
        return
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))


# ==============================================================================
# EMPLOYEE MENU & HANDLERS
# ==============================================================================
def handle_employees_menu():
    while True:
        clear_screen()
        print("                 === EMPLOYEE MANAGEMENT ===")
        print("  [1] List All Employees (with Department & Role)")
        print("  [2] View Employee Details by ID")
        print("  [3] Add New Employee (Create)")
        print("  [4] Update Employee Details (Update)")
        print("  [5] Delete Employee Record (Delete)")
        print("  [6] Search Employees (by Name / Email / Role / Dept)")
        print("  [7] Filter Employees (by Department / Role / Status)")
        print("  [0] Back to Main Menu")
        print("-" * 75)

        choice = get_input("Enter choice (0-7)")
        if choice == "0":
            break
        elif choice == "1":
            status = get_input("Filter by status? (Active/On Leave/Resigned/Terminated or Enter for All)", "")
            emps = EmployeeModel.get_all(status if status else None)
            display_data = [
                {
                    "ID": e["employee_id"],
                    "Name": e["full_name"],
                    "Email": e["email"],
                    "Department": e["department_name"],
                    "Role": e["role_title"],
                    "Salary (₹)": f"₹{float(e['salary']):,.2f}",
                    "Status": e["status"],
                    "Hired": str(e["hire_date"])
                }
                for e in emps
            ]
            print_table(display_data, title="EMPLOYEE DIRECTORY")
            input("\nPress Enter to continue...")

        elif choice == "2":
            try:
                emp_id = int(get_input("Enter Employee ID"))
                emp = EmployeeModel.get_by_id(emp_id)
                if not emp:
                    print(f"[!] Employee ID {emp_id} not found.")
                else:
                    print("\n--- EMPLOYEE PROFILE ---")
                    for k, v in emp.items():
                        print(f"  {k:<20}: {v}")
            except ValueError:
                print("[!] Invalid input. Must be an integer ID.")
            input("\nPress Enter to continue...")

        elif choice == "3":
            print("\n--- Add New Employee ---")
            try:
                fn = get_input("First Name")
                ln = get_input("Last Name")
                email = get_input("Email")
                phone = get_input("Phone Number")
                hdate = get_input("Hire Date (YYYY-MM-DD)", "2024-01-01")

                # Show departments
                depts = DepartmentModel.get_all()
                print("\nAvailable Departments:")
                for d in depts:
                    print(f"  [{d['department_id']}] {d['department_name']}")
                dept_id = int(get_input("Department ID"))

                # Show roles
                roles = RoleModel.get_all()
                print("\nAvailable Roles:")
                for r in roles:
                    print(f"  [{r['role_id']}] {r['role_title']} (₹{r['min_salary']:,.0f} - ₹{r['max_salary']:,.0f})")
                role_id = int(get_input("Role ID"))

                sal = float(get_input("Salary (₹)"))
                status = get_input("Status (Active/On Leave/Resigned/Terminated)", "Active")

                new_id = EmployeeModel.create(fn, ln, email, phone, hdate, dept_id, role_id, sal, status)
                print(f"[✓] Successfully added employee! Assigned ID: {new_id}")
            except Exception as e:
                print(f"[✗] Error creating employee: {e}")
            input("\nPress Enter to continue...")

        elif choice == "4":
            print("\n--- Update Employee Details ---")
            try:
                emp_id = int(get_input("Enter Employee ID to update"))
                emp = EmployeeModel.get_by_id(emp_id)
                if not emp:
                    print(f"[!] Employee ID {emp_id} not found.")
                else:
                    print(f"Updating details for {emp['full_name']} (leave blank to keep current):")
                    fn = get_input(f"First Name", emp["first_name"])
                    ln = get_input(f"Last Name", emp["last_name"])
                    email = get_input(f"Email", emp["email"])
                    phone = get_input(f"Phone", emp["phone"])
                    dept_id_in = get_input(f"Department ID", str(emp["department_id"]))
                    role_id_in = get_input(f"Role ID", str(emp["role_id"]))
                    salary_in = get_input(f"Salary", str(emp["salary"]))
                    status = get_input(f"Status", emp["status"])

                    EmployeeModel.update(
                        emp_id,
                        first_name=fn,
                        last_name=ln,
                        email=email,
                        phone=phone,
                        department_id=int(dept_id_in),
                        role_id=int(role_id_in),
                        salary=float(salary_in),
                        status=status
                    )
                    print(f"[✓] Employee ID {emp_id} updated successfully!")
            except Exception as e:
                print(f"[✗] Update failed: {e}")
            input("\nPress Enter to continue...")

        elif choice == "5":
            print("\n--- Delete Employee ---")
            try:
                emp_id = int(get_input("Enter Employee ID to delete"))
                emp = EmployeeModel.get_by_id(emp_id)
                if not emp:
                    print(f"[!] Employee ID {emp_id} not found.")
                else:
                    confirm = get_input(f"Are you sure you want to delete {emp['full_name']} (ID: {emp_id})? (y/N)", "N")
                    if confirm.lower() == 'y':
                        EmployeeModel.delete(emp_id)
                        print(f"[✓] Employee ID {emp_id} deleted successfully.")
                    else:
                        print("[-] Deletion cancelled.")
            except Exception as e:
                print(f"[✗] Delete failed: {e}")
            input("\nPress Enter to continue...")

        elif choice == "6":
            kw = get_input("Enter search keyword")
            results = EmployeeModel.search(kw)
            print_table(results, title=f"SEARCH RESULTS FOR '{kw}'")
            input("\nPress Enter to continue...")

        elif choice == "7":
            print("\n--- Filter Employees ---")
            d_id = get_input("Department ID (or leave blank)", "")
            r_id = get_input("Role ID (or leave blank)", "")
            st = get_input("Status (or leave blank)", "")
            results = EmployeeModel.filter(
                department_id=int(d_id) if d_id else None,
                role_id=int(r_id) if r_id else None,
                status=st if st else None
            )
            print_table(results, title="FILTERED EMPLOYEES")
            input("\nPress Enter to continue...")


# ==============================================================================
# DEPARTMENT MENU & HANDLERS
# ==============================================================================
def handle_departments_menu():
    while True:
        clear_screen()
        print("                 === DEPARTMENT MANAGEMENT ===")
        print("  [1] List All Departments (with Headcount & Payroll)")
        print("  [2] Add New Department (Create)")
        print("  [3] Update Department (Update)")
        print("  [4] Delete Department (Delete)")
        print("  [0] Back to Main Menu")
        print("-" * 75)

        choice = get_input("Enter choice (0-4)")
        if choice == "0":
            break
        elif choice == "1":
            depts = DepartmentModel.get_all()
            table_data = [
                {
                    "ID": d["department_id"],
                    "Department": d["department_name"],
                    "Location": d["location"],
                    "Budget (₹)": f"₹{float(d['budget']):,.2f}",
                    "Headcount": d["total_employees"],
                    "Payroll (₹)": f"₹{float(d['total_payroll']):,.2f}"
                }
                for d in depts
            ]
            print_table(table_data, title="DEPARTMENTS DIRECTORY")
            input("\nPress Enter to continue...")

        elif choice == "2":
            print("\n--- Add New Department ---")
            try:
                name = get_input("Department Name")
                loc = get_input("Location")
                budget = float(get_input("Budget (₹)", "0.0"))
                d_id = DepartmentModel.create(name, loc, budget)
                print(f"[✓] Department created with ID: {d_id}")
            except Exception as e:
                print(f"[✗] Error: {e}")
            input("\nPress Enter to continue...")

        elif choice == "3":
            print("\n--- Update Department ---")
            try:
                d_id = int(get_input("Enter Department ID to update"))
                dept = DepartmentModel.get_by_id(d_id)
                if not dept:
                    print("[!] Department not found.")
                else:
                    name = get_input("Department Name", dept["department_name"])
                    loc = get_input("Location", dept["location"])
                    budget = float(get_input("Budget (₹)", str(dept["budget"])))
                    DepartmentModel.update(d_id, name, loc, budget)
                    print(f"[✓] Department ID {d_id} updated successfully!")
            except Exception as e:
                print(f"[✗] Error: {e}")
            input("\nPress Enter to continue...")

        elif choice == "4":
            print("\n--- Delete Department ---")
            try:
                d_id = int(get_input("Enter Department ID to delete"))
                DepartmentModel.delete(d_id)
                print(f"[✓] Department ID {d_id} deleted successfully.")
            except Exception as e:
                print(f"[✗] Error: {e}")
            input("\nPress Enter to continue...")


# ==============================================================================
# ROLE MENU & HANDLERS
# ==============================================================================
def handle_roles_menu():
    while True:
        clear_screen()
        print("                 === ROLE & DESIGNATION MANAGEMENT ===")
        print("  [1] List All Roles (with Salary Bands & Headcount)")
        print("  [2] Add New Role (Create)")
        print("  [3] Update Role (Update)")
        print("  [4] Delete Role (Delete)")
        print("  [0] Back to Main Menu")
        print("-" * 75)

        choice = get_input("Enter choice (0-4)")
        if choice == "0":
            break
        elif choice == "1":
            roles = RoleModel.get_all()
            table_data = [
                {
                    "ID": r["role_id"],
                    "Title": r["role_title"],
                    "Min Salary (₹)": f"₹{float(r['min_salary']):,.2f}",
                    "Max Salary (₹)": f"₹{float(r['max_salary']):,.2f}",
                    "Assigned Employees": r["total_employees"],
                    "Avg Actual Salary (₹)": f"₹{float(r['avg_actual_salary']):,.2f}"
                }
                for r in roles
            ]
            print_table(table_data, title="ROLES DIRECTORY")
            input("\nPress Enter to continue...")

        elif choice == "2":
            print("\n--- Add New Role ---")
            try:
                title = get_input("Role Title")
                min_s = float(get_input("Minimum Salary (₹)"))
                max_s = float(get_input("Maximum Salary (₹)"))
                desc = get_input("Description", "")
                r_id = RoleModel.create(title, min_s, max_s, desc)
                print(f"[✓] Role created with ID: {r_id}")
            except Exception as e:
                print(f"[✗] Error: {e}")
            input("\nPress Enter to continue...")

        elif choice == "3":
            print("\n--- Update Role ---")
            try:
                r_id = int(get_input("Enter Role ID to update"))
                role = RoleModel.get_by_id(r_id)
                if not role:
                    print("[!] Role not found.")
                else:
                    title = get_input("Role Title", role["role_title"])
                    min_s = float(get_input("Min Salary", str(role["min_salary"])))
                    max_s = float(get_input("Max Salary", str(role["max_salary"])))
                    desc = get_input("Description", role["description"])
                    RoleModel.update(r_id, title, min_s, max_s, desc)
                    print(f"[✓] Role ID {r_id} updated successfully!")
            except Exception as e:
                print(f"[✗] Error: {e}")
            input("\nPress Enter to continue...")

        elif choice == "4":
            print("\n--- Delete Role ---")
            try:
                r_id = int(get_input("Enter Role ID to delete"))
                RoleModel.delete(r_id)
                print(f"[✓] Role ID {r_id} deleted successfully.")
            except Exception as e:
                print(f"[✗] Error: {e}")
            input("\nPress Enter to continue...")


# ==============================================================================
# ANALYTICS & REPORTS MENU
# ==============================================================================
def handle_analytics_menu():
    while True:
        clear_screen()
        print("                 === EXECUTIVE ANALYTICS & REPORTS ===")
        print("  [1] Department Summary & Budget Utilization Analysis")
        print("  [2] Role Salary Bands vs. Actual Compensation Analysis")
        print("  [3] Top Highest Paid Employees")
        print("  [4] Employee Tenure & Service Years Analysis")
        print("  [0] Back to Main Menu")
        print("-" * 75)

        choice = get_input("Enter choice (0-4)")
        if choice == "0":
            break
        elif choice == "1":
            data = AnalyticsService.get_department_analytics()
            print_table(data, title="DEPARTMENT BUDGET & PAYROLL UTILIZATION")
            input("\nPress Enter to continue...")
        elif choice == "2":
            data = AnalyticsService.get_role_analytics()
            print_table(data, title="ROLE SALARY ANALYSIS")
            input("\nPress Enter to continue...")
        elif choice == "3":
            limit = int(get_input("How many top earners?", "5"))
            data = AnalyticsService.get_top_earners(limit)
            print_table(data, title=f"TOP {limit} HIGHEST PAID EMPLOYEES")
            input("\nPress Enter to continue...")
        elif choice == "4":
            data = AnalyticsService.get_tenure_analysis()
            print_table(data, title="EMPLOYEE TENURE & SERVICE YEARS")
            input("\nPress Enter to continue...")


# ==============================================================================
# MAIN APPLICATION LOOP
# ==============================================================================
def main():
    clear_screen()
    print("=" * 75)
    print("  PYTHON-BASED EMPLOYEE DATA MANAGEMENT SYSTEM (POSTGRESQL)")
    print("  Practical Task 1: Relational Schema, CRUD, Analytics & Visualization")
    print("=" * 75)

    if not test_connection():
        print("[!] Could not connect to PostgreSQL. Please check your credentials or server.")
        sys.exit(1)

    while True:
        clear_screen()
        print("                     === MAIN DASHBOARD ===")
        print("  [1] Employee Management       (Create, Read, Update, Delete, Search)")
        print("  [2] Department Management     (Departments, Budgets, Locations)")
        print("  [3] Role & Designation System (Job Roles, Salary Ranges)")
        print("  [4] Executive Analytics       (Headcount, Payroll, Top Earners)")
        print("  [5] Generate Visualizations   (Matplotlib & Seaborn Charts)")
        print("  [6] Reset & Seed Database     (Re-initialize schema and sample data)")
        print("  [7] Run Automated Test Suite  (Verify 100% of CRUD operations)")
        print("  [0] Exit")
        print("-" * 75)

        choice = get_input("Select an option (0-7)")
        if choice == "0":
            print("\nExiting Employee Management System. Goodbye!\n")
            break
        elif choice == "1":
            handle_employees_menu()
        elif choice == "2":
            handle_departments_menu()
        elif choice == "3":
            handle_roles_menu()
        elif choice == "4":
            handle_analytics_menu()
        elif choice == "5":
            charts = generate_all_visualizations()
            print(f"\n[✓] Generated {len(charts)} chart figures in visualizations/ folder.")
            input("\nPress Enter to continue...")
        elif choice == "6":
            confirm = get_input("Are you sure you want to re-initialize and seed the DB? (y/N)", "N")
            if confirm.lower() == 'y':
                initialize_database()
                seed_database()
            input("\nPress Enter to continue...")
        elif choice == "7":
            from run_all_tests import run_tests
            run_tests()
            input("\nPress Enter to continue...")
        else:
            print("[!] Invalid option. Please choose between 0 and 7.")


if __name__ == "__main__":
    main()
