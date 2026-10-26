"""
Seed Data Script.
Populates PostgreSQL with realistic sample Departments, Roles, and Employees
for demonstration, testing, and data visualization.
"""

from db_connection import get_connection
from models import DepartmentModel, RoleModel, EmployeeModel


def seed_database():
    """Seeds departments, roles, and employees into the database."""
    print("\n" + "="*70)
    print("      SEEDING DATABASE: EMPLOYEE MANAGEMENT SYSTEM")
    print("="*70)

    # 1. Departments Seed Data
    departments_data = [
        ("Engineering", "Bengaluru - Tech Hub", 2500000.00),
        ("Data Science & AI", "Bengaluru - Innovation Lab", 2200000.00),
        ("Product Management", "Mumbai - Corporate HQ", 1800000.00),
        ("Human Resources", "Pune - Operations Center", 900000.00),
        ("Marketing & Growth", "Delhi NCR - Regional Office", 1200000.00),
    ]

    dept_ids = {}
    print("\n[*] Seeding Departments...")
    for name, loc, budget in departments_data:
        try:
            d_id = DepartmentModel.create(name, loc, budget)
            dept_ids[name] = d_id
            print(f"  [+] Inserted Department [{d_id}]: {name} (Budget: ₹{budget:,.2f})")
        except Exception as e:
            # If already exists, retrieve existing id
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT department_id FROM departments WHERE department_name = %s", (name,))
                    row = cur.fetchone()
                    if row:
                        dept_ids[name] = row[0]
                        print(f"  [~] Department already exists [{row[0]}]: {name}")

    # 2. Roles Seed Data
    roles_data = [
        ("Software Engineer", 50000.00, 100000.00, "Develops and maintains core backend and frontend applications"),
        ("Senior Software Engineer", 90000.00, 180000.00, "Architects distributed systems and mentors engineering teams"),
        ("Lead Data Scientist", 110000.00, 220000.00, "Builds predictive ML models and oversees data strategy"),
        ("Data Analyst", 45000.00, 85000.00, "Analyzes datasets, creates dashboards, and extracts actionable business insights"),
        ("DevOps Engineer", 60000.00, 120000.00, "Manages CI/CD pipelines, containerization, and cloud infrastructure"),
        ("Product Manager", 85000.00, 175000.00, "Guides product lifecycle from ideation to launch and user analytics"),
        ("HR Specialist", 40000.00, 75000.00, "Handles talent acquisition, employee relations, and HR policies"),
        ("Marketing Manager", 65000.00, 130000.00, "Drives digital brand campaigns, user acquisition, and media outreach"),
    ]

    role_ids = {}
    print("\n[*] Seeding Roles...")
    for title, min_sal, max_sal, desc in roles_data:
        try:
            r_id = RoleModel.create(title, min_sal, max_sal, desc)
            role_ids[title] = r_id
            print(f"  [+] Inserted Role [{r_id}]: {title} (Band: ₹{min_sal:,.0f} - ₹{max_sal:,.0f})")
        except Exception as e:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT role_id FROM roles WHERE role_title = %s", (title,))
                    row = cur.fetchone()
                    if row:
                        role_ids[title] = row[0]
                        print(f"  [~] Role already exists [{row[0]}]: {title}")

    # 3. Employees Seed Data
    employees_data = [
        # Engineering
        ("Aarav", "Sharma", "aarav.sharma@company.com", "+91-9876543210", "2021-03-15", "Engineering", "Senior Software Engineer", 145000.00, "Active"),
        ("Priya", "Nair", "priya.nair@company.com", "+91-9876543211", "2022-06-01", "Engineering", "Software Engineer", 78000.00, "Active"),
        ("Rohan", "Mehta", "rohan.mehta@company.com", "+91-9876543212", "2023-01-10", "Engineering", "Software Engineer", 65000.00, "Active"),
        ("Kavya", "Iyer", "kavya.iyer@company.com", "+91-9876543213", "2020-11-20", "Engineering", "DevOps Engineer", 105000.00, "Active"),
        ("Aditya", "Verma", "aditya.verma@company.com", "+91-9876543214", "2022-09-18", "Engineering", "DevOps Engineer", 88000.00, "Active"),

        # Data Science & AI
        ("Dr. Vikram", "Rao", "vikram.rao@company.com", "+91-9876543215", "2019-08-01", "Data Science & AI", "Lead Data Scientist", 195000.00, "Active"),
        ("Ananya", "Patel", "ananya.patel@company.com", "+91-9876543216", "2021-04-12", "Data Science & AI", "Lead Data Scientist", 160000.00, "Active"),
        ("Siddharth", "Joshi", "siddharth.joshi@company.com", "+91-9876543217", "2023-03-01", "Data Science & AI", "Data Analyst", 62000.00, "Active"),
        ("Sneha", "Kulkarni", "sneha.kulkarni@company.com", "+91-9876543218", "2023-07-15", "Data Science & AI", "Data Analyst", 55000.00, "Active"),
        ("Rahul", "Deshmukh", "rahul.deshmukh@company.com", "+91-9876543219", "2024-01-05", "Data Science & AI", "Data Analyst", 50000.00, "Active"),

        # Product Management
        ("Neha", "Gupta", "neha.gupta@company.com", "+91-9876543220", "2020-02-14", "Product Management", "Product Manager", 155000.00, "Active"),
        ("Karan", "Singhania", "karan.singhania@company.com", "+91-9876543221", "2022-11-01", "Product Management", "Product Manager", 120000.00, "Active"),
        ("Tanvi", "Bhatia", "tanvi.bhatia@company.com", "+91-9876543222", "2023-05-20", "Product Management", "Product Manager", 98000.00, "On Leave"),

        # Human Resources
        ("Sunita", "Menon", "sunita.menon@company.com", "+91-9876543223", "2018-09-01", "Human Resources", "HR Specialist", 72000.00, "Active"),
        ("Deepak", "Chopra", "deepak.chopra@company.com", "+91-9876543224", "2022-08-15", "Human Resources", "HR Specialist", 52000.00, "Active"),
        ("Pooja", "Reddy", "pooja.reddy@company.com", "+91-9876543225", "2023-10-01", "Human Resources", "HR Specialist", 48000.00, "Active"),

        # Marketing & Growth
        ("Arjun", "Kapoor", "arjun.kapoor@company.com", "+91-9876543226", "2020-07-01", "Marketing & Growth", "Marketing Manager", 115000.00, "Active"),
        ("Meera", "Saxena", "meera.saxena@company.com", "+91-9876543227", "2022-04-18", "Marketing & Growth", "Marketing Manager", 92000.00, "Active"),
        ("Varun", "Malhotra", "varun.malhotra@company.com", "+91-9876543228", "2023-09-05", "Marketing & Growth", "Marketing Manager", 75000.00, "Active"),
        ("Divya", "Sen", "divya.sen@company.com", "+91-9876543229", "2024-02-01", "Engineering", "Software Engineer", 58000.00, "Active"),
    ]

    print("\n[*] Seeding Employees...")
    emp_count = 0
    for fn, ln, email, phone, hdate, dname, rtitle, sal, status in employees_data:
        try:
            d_id = dept_ids[dname]
            r_id = role_ids[rtitle]
            e_id = EmployeeModel.create(fn, ln, email, phone, hdate, d_id, r_id, sal, status)
            emp_count += 1
            print(f"  [+] Inserted Employee [{e_id:02d}]: {fn} {ln:<10} | {rtitle:<25} | ₹{sal:,.2f} | Dept: {dname}")
        except Exception as e:
            print(f"  [!] Skipped {fn} {ln}: {e}")

    print("\n" + "="*70)
    print(f"[✓] Seeding Complete! {len(dept_ids)} Departments, {len(role_ids)} Roles, and {emp_count} Employees.")
    print("="*70 + "\n")


if __name__ == "__main__":
    from init_db import initialize_database
    initialize_database()
    seed_database()
