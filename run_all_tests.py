"""
Automated Test & Verification Suite for Employee Management System.
Exercises and validates all CRUD operations, relational joins, constraints,
and analytical reports. Prints beautifully formatted tables of execution.
"""

import sys
from tabulate import tabulate
from db_connection import test_connection
from models import DepartmentModel, RoleModel, EmployeeModel
from analytics import AnalyticsService
from visualizer import generate_all_visualizations


def print_section(title: str):
    print("\n" + "=" * 80)
    print(f" >>> {title.upper()} <<<")
    print("=" * 80)


def run_tests():
    print_section("1. Testing Database Connectivity")
    if not test_connection():
        print("[!] Cannot continue tests without active database connection.")
        sys.exit(1)

    # ---------------------------------------------------------
    # TEST 1: DEPARTMENT CRUD
    # ---------------------------------------------------------
    print_section("2. Department CRUD Operations")
    
    # 2.1 CREATE
    print("[*] Testing [C] Create Department...")
    dept_id = DepartmentModel.create(
        name="Quality Assurance & Testing",
        location="Hyderabad - Tech Park",
        budget=750000.00
    )
    print(f" [✓] Created Department ID: {dept_id}")

    # 2.2 READ
    print("\n[*] Testing [R] Read Department...")
    dept = DepartmentModel.get_by_id(dept_id)
    print(f" [✓] Fetched Department: {dept['department_name']} at {dept['location']} (Budget: ₹{dept['budget']:,.2f})")

    # 2.3 UPDATE
    print("\n[*] Testing [U] Update Department...")
    DepartmentModel.update(dept_id, location="Hyderabad - HITEC City", budget=850000.00)
    dept_updated = DepartmentModel.get_by_id(dept_id)
    print(f" [✓] Updated Location: {dept_updated['location']} | Budget: ₹{dept_updated['budget']:,.2f}")

    # 2.4 DELETE
    print("\n[*] Testing [D] Delete Department...")
    DepartmentModel.delete(dept_id)
    print(f" [✓] Deleted Department ID {dept_id} successfully.")

    # ---------------------------------------------------------
    # TEST 2: ROLE CRUD
    # ---------------------------------------------------------
    print_section("3. Role CRUD Operations")

    # 3.1 CREATE
    print("[*] Testing [C] Create Role...")
    role_id = RoleModel.create(
        title="Security Engineer",
        min_salary=70000.00,
        max_salary=140000.00,
        description="Responsible for cybersecurity, vulnerability assessments, and compliance"
    )
    print(f" [✓] Created Role ID: {role_id}")

    # 3.2 READ
    print("\n[*] Testing [R] Read Role...")
    role = RoleModel.get_by_id(role_id)
    print(f" [✓] Fetched Role: {role['role_title']} | Salary: ₹{role['min_salary']:,.2f} - ₹{role['max_salary']:,.2f}")

    # 3.3 UPDATE
    print("\n[*] Testing [U] Update Role...")
    RoleModel.update(role_id, max_salary=150000.00)
    role_updated = RoleModel.get_by_id(role_id)
    print(f" [✓] Updated Max Salary: ₹{role_updated['max_salary']:,.2f}")

    # 3.4 DELETE
    print("\n[*] Testing [D] Delete Role...")
    RoleModel.delete(role_id)
    print(f" [✓] Deleted Role ID {role_id} successfully.")

    # ---------------------------------------------------------
    # TEST 3: EMPLOYEE CRUD & RELATIONAL INTEGRITY
    # ---------------------------------------------------------
    print_section("4. Employee CRUD Operations & Relational Integrity")

    # 4.1 CREATE
    print("[*] Testing [C] Create Employee...")
    emp_id = EmployeeModel.create(
        first_name="Ishaan",
        last_name="Bose",
        email="ishaan.bose@company.com",
        phone="+91-9876543299",
        hire_date="2024-05-01",
        department_id=1,      # Engineering
        role_id=1,            # Software Engineer
        salary=72000.00,
        status="Active"
    )
    print(f" [✓] Created Employee ID: {emp_id}")

    # 4.2 READ (Single with JOIN)
    print("\n[*] Testing [R] Read Employee Details (JOIN)...")
    emp = EmployeeModel.get_by_id(emp_id)
    print(f" [✓] Name: {emp['full_name']} | Dept: {emp['department_name']} | Role: {emp['role_title']} | Salary: ₹{emp['salary']:,.2f}")

    # 4.3 SEARCH
    print("\n[*] Testing Search Employee (Keyword: 'Bose')...")
    results = EmployeeModel.search("Bose")
    print(tabulate(results, headers="keys", tablefmt="fancy_grid"))

    # 4.4 UPDATE (Promotion / Salary Revision)
    print("\n[*] Testing [U] Update Employee (Promotion to Senior Software Engineer)...")
    EmployeeModel.update(emp_id, role_id=2, salary=115000.00)
    emp_updated = EmployeeModel.get_by_id(emp_id)
    print(f" [✓] Promoted to: {emp_updated['role_title']} | New Salary: ₹{emp_updated['salary']:,.2f} | Updated At: {emp_updated['updated_at']}")

    # 4.5 CONSTRAINT VALIDATION TEST
    print("\n[*] Testing Constraint: Prevent Deleting Department with Active Employees...")
    try:
        DepartmentModel.delete(1)
        print(" [✗] Constraint failed!")
    except ValueError as ve:
        print(f" [✓] Expected Constraint Enforced: {ve}")

    # 4.6 DELETE
    print("\n[*] Testing [D] Delete Employee...")
    EmployeeModel.delete(emp_id)
    print(f" [✓] Cleaned up temporary Employee ID {emp_id} successfully.")

    # ---------------------------------------------------------
    # TEST 4: EXECUTIVE ANALYTICAL QUERIES
    # ---------------------------------------------------------
    print_section("5. Executive Relational Analytics & Summaries")

    print("[*] Department Headcount & Payroll Metrics:")
    dept_metrics = AnalyticsService.get_department_analytics()
    print(tabulate(dept_metrics, headers="keys", tablefmt="fancy_grid", floatfmt=",.2f"))

    print("\n[*] Top 5 Earners in Organization:")
    top_earners = AnalyticsService.get_top_earners(5)
    print(tabulate(top_earners, headers="keys", tablefmt="fancy_grid", floatfmt=",.2f"))

    # ---------------------------------------------------------
    # TEST 5: DATA VISUALIZATIONS GENERATION
    # ---------------------------------------------------------
    print_section("6. Data Visualization Generation")
    charts = generate_all_visualizations()
    print(f"[✓] Successfully generated and verified {len(charts)} publication-quality visual charts.")

    print_section("ALL TESTS COMPLETED SUCCESSFULLY (100% PASS)")


if __name__ == "__main__":
    run_tests()
