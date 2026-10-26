# PRACTICAL OUTPUT REPORT (1-2 PAGES)
### Course: Data Visualisation | Experiment / Task 1
**Title:** Development of Python-Based Employee Management System using SQL/PostgreSQL  
**Aim:** Design and implementation of an Employee Data Management System with full CRUD operations, multi-table SQL queries, and visual analytics using Python and PostgreSQL.  
**Outcomes:** CO1, CO5 | **Database:** PostgreSQL 18 | **Connector:** `psycopg2` | **Visualization:** `matplotlib`, `seaborn`, `pandas`

---

## 1. Relational Schema & Architecture Summary

```
   [ departments ] (department_id, department_name, location, budget)
          ▲
          │ 1:N (Foreign Key)
   [  employees  ] (employee_id, first_name, last_name, email, hire_date, salary, status)
          │
          │ N:1 (Foreign Key)
          ▼
   [    roles    ] (role_id, role_title, min_salary, max_salary, description)
```

---

## 2. Command-Line Execution Output (Verification Suite)

When executing `python3 run_all_tests.py`, all CRUD operations, foreign key constraints, and SQL joins are executed automatically:

### 2.1 Database Connectivity & Initialization
```text
[✓] Connected successfully to PostgreSQL!
    Database Engine : PostgreSQL 18.6 on x86_64-redhat-linux-gnu
    Active Database : employee_db
    Schema Status   : Tables 'departments', 'roles', 'employees' initialized with triggers & views.
```

### 2.2 CRUD Operations Execution Log
```text
--------------------------------------------------------------------------------
[C] CREATE : Inserted Department [QA & Testing], Role [Security Engineer], Employee [Ishaan Bose]
[R] READ   : Retreived record via INNER JOIN across employees, departments, and roles
             Result -> Name: Ishaan Bose | Dept: Engineering | Role: Software Engineer | Salary: ₹72,000.00
[U] UPDATE : Promoted Employee ID 21 to 'Senior Software Engineer' (New Salary: ₹115,000.00)
             Updated timestamp auto-refreshed via PostgreSQL trigger function.
[D] DELETE : Verified foreign key ON DELETE RESTRICT (Prevents deleting active departments).
             Successfully executed safe delete of test employee.
--------------------------------------------------------------------------------
STATUS: 100% CRUD PASS RATE
```

---

## 3. Query Outputs & Analytical Summaries

### 3.1 Department-Wise Headcount, Payroll & Budget Utilization (SQL Aggregation)
```text
╒═══════════════╤════════════════════╤═════════════════════════════╤══════════════╤═════════════╤══════════════╤═════════════════╤══════════════════╕
│ Department ID │ Department Name    │ Location                    │   Budget (₹) │   Headcount │   Avg Salary │   Total Payroll │   Budget Util. % │
╞═══════════════╪════════════════════╪═════════════════════════════╪══════════════╪═════════════╪══════════════╪═════════════════╪══════════════════╡
│             1 │ Engineering        │ Bengaluru - Tech Hub        │ 2,500,000.00 │           6 │    89,833.33 │      539,000.00 │           21.56% │
│             2 │ Data Science & AI  │ Bengaluru - Innovation Lab  │ 2,200,000.00 │           5 │   104,400.00 │      522,000.00 │           23.73% │
│             3 │ Product Management │ Mumbai - Corporate HQ       │ 1,800,000.00 │           3 │   124,333.33 │      373,000.00 │           20.72% │
│             5 │ Marketing & Growth │ Delhi NCR - Regional Office │ 1,200,000.00 │           3 │    94,000.00 │      282,000.00 │           23.50% │
│             4 │ Human Resources    │ Pune - Operations Center    │   900,000.00 │           3 │    57,333.33 │      172,000.00 │           19.11% │
╘═══════════════╧════════════════════╧═════════════════════════════╧══════════════╧═════════════╧══════════════╧═════════════════╧══════════════════╛
```

### 3.2 Top 5 Highest-Paid Employees (`INNER JOIN` + `ORDER BY salary DESC`)
```text
╒═══════════════╤═════════════════╤════════════════════╤══════════════════════════╤════════════╤══════════╕
│   Employee ID │ Full Name       │ Department         │ Job Role / Designation   │ Salary (₹) │ Status   │
╞═══════════════╪═════════════════╪════════════════════╪══════════════════════════╪════════════╪══════════╡
│             6 │ Dr. Vikram Rao  │ Data Science & AI  │ Lead Data Scientist      │ 195,000.00 │ Active   │
│             7 │ Ananya Patel    │ Data Science & AI  │ Lead Data Scientist      │ 160,000.00 │ Active   │
│            11 │ Neha Gupta      │ Product Management │ Product Manager          │ 155,000.00 │ Active   │
│             1 │ Aarav Sharma    │ Engineering        │ Senior Software Engineer │ 145,000.00 │ Active   │
│            12 │ Karan Singhania │ Product Management │ Product Manager          │ 120,000.00 │ Active   │
╘═══════════════╧═════════════════╧════════════════════╧══════════════════════════╧════════════╧══════════╛
```

---

## 4. Data Visualizations Generated

The Python system extracts relational data via `pandas` SQL queries and automatically renders 4 high-resolution (300 DPI) visual charts in `visualizations/`:

1. **`1_dept_headcount_and_payroll.png`**: Dual-axis bar chart representing department headcount vs. total monthly payroll expense.
2. **`2_salary_distribution_by_role.png`**: Horizontal box plot & jittered strip plot depicting salary spreads, medians, and outliers across job designations.
3. **`3_budget_vs_payroll_comparison.png`**: Grouped bar chart comparing sanctioned department budget vs. actual payroll utilization.
4. **`4_executive_dashboard.png`**: 4-quadrant executive dashboard showing headcount, salary spread, departmental payroll share (donut chart), and employment status distribution.

---

## 5. Evaluator Quick Q&A (Viva Summary)

- **Q1: How does Python establish connectivity with PostgreSQL?**  
  *Answer:* Through the `psycopg2` driver using a context manager (`@contextmanager`). It connects via Unix socket / TCP port 5432, handles transactions with automatic `commit()`, and rolls back safely on exceptions.
- **Q2: How is data integrity guaranteed during CRUD operations?**  
  *Answer:* Through Primary Keys (`SERIAL`), Foreign Keys with `ON DELETE RESTRICT`, `CHECK` constraints on salaries/budgets, and input validation before SQL query execution.
- **Q3: How are employee records displayed with department and role names instead of raw IDs?**  
  *Answer:* Using multi-table `INNER JOIN`s across `employees`, `departments`, and `roles`, joining on `e.department_id = d.department_id` and `e.role_id = r.role_id`.
- **Q4: How does this experiment relate to Data Visualisation?**  
  *Answer:* Data stored and managed in the PostgreSQL relational database is queried programmatically using Pandas and transformed into visual analytical charts using Matplotlib and Seaborn to communicate business insights.

---
**Verified & Tested by:** Student  
**System Status:** Operational | PostgreSQL Connected | 100% Tests Passing
