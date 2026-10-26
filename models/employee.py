"""
Employee Model - CRUD Operations for Employees Table.
Implements relational queries, foreign key validations, and JOIN operations.
"""

from typing import List, Dict, Any, Optional
from datetime import date
from db_connection import execute_read, execute_write
from .department import DepartmentModel
from .role import RoleModel


class EmployeeModel:
    """Encapsulates CRUD operations and relational queries for employees."""

    @staticmethod
    def create(
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        hire_date: str,
        department_id: int,
        role_id: int,
        salary: float,
        status: str = "Active"
    ) -> int:
        """
        [C] Create: Adds a new employee record with relational integrity checks.
        """
        # 1. Verify department exists
        dept = DepartmentModel.get_by_id(department_id)
        if not dept:
            raise ValueError(f"Department ID {department_id} does not exist.")

        # 2. Verify role exists
        role = RoleModel.get_by_id(role_id)
        if not role:
            raise ValueError(f"Role ID {role_id} does not exist.")

        # 3. Validate salary within role limits (optional soft warning or strict validation)
        min_sal = float(role["min_salary"])
        max_sal = float(role["max_salary"])
        if salary < min_sal or salary > max_sal:
            raise ValueError(f"Salary ₹{salary:,.2f} is outside the allowed range for '{role['role_title']}' [₹{min_sal:,.2f} - ₹{max_sal:,.2f}].")

        # 4. Validate status
        valid_statuses = ("Active", "On Leave", "Resigned", "Terminated")
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}")

        query = """
            INSERT INTO employees (
                first_name, last_name, email, phone, hire_date,
                department_id, role_id, salary, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING employee_id;
        """
        params = (
            first_name.strip(),
            last_name.strip(),
            email.strip().lower(),
            phone.strip(),
            hire_date,
            department_id,
            role_id,
            salary,
            status
        )
        emp_id = execute_write(query, params, returning_id=True)
        return emp_id

    @staticmethod
    def get_all(status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        [R] Read: Retrieves all employees with department and role names using INNER JOIN.
        """
        base_query = """
            SELECT 
                e.employee_id,
                e.first_name,
                e.last_name,
                e.first_name || ' ' || e.last_name AS full_name,
                e.email,
                e.phone,
                e.hire_date,
                e.department_id,
                d.department_name,
                d.location AS department_location,
                e.role_id,
                r.role_title,
                e.salary,
                e.status,
                e.created_at,
                e.updated_at
            FROM employees e
            INNER JOIN departments d ON e.department_id = d.department_id
            INNER JOIN roles r ON e.role_id = r.role_id
        """
        if status:
            query = base_query + " WHERE e.status = %s ORDER BY e.employee_id ASC;"
            return execute_read(query, (status,))
        else:
            query = base_query + " ORDER BY e.employee_id ASC;"
            return execute_read(query)

    @staticmethod
    def get_by_id(employee_id: int) -> Optional[Dict[str, Any]]:
        """
        [R] Read: Retrieves complete details of an employee by ID.
        """
        query = """
            SELECT 
                e.employee_id,
                e.first_name,
                e.last_name,
                e.first_name || ' ' || e.last_name AS full_name,
                e.email,
                e.phone,
                e.hire_date,
                e.department_id,
                d.department_name,
                d.location AS department_location,
                e.role_id,
                r.role_title,
                e.salary,
                e.status,
                e.created_at,
                e.updated_at
            FROM employees e
            INNER JOIN departments d ON e.department_id = d.department_id
            INNER JOIN roles r ON e.role_id = r.role_id
            WHERE e.employee_id = %s;
        """
        rows = execute_read(query, (employee_id,))
        return rows[0] if rows else None

    @staticmethod
    def search(keyword: str) -> List[Dict[str, Any]]:
        """
        [R] Read/Search: Case-insensitive search across name, email, department, or role.
        """
        pattern = f"%{keyword.strip()}%"
        query = """
            SELECT 
                e.employee_id,
                e.first_name || ' ' || e.last_name AS full_name,
                e.email,
                e.phone,
                d.department_name,
                r.role_title,
                e.salary,
                e.status
            FROM employees e
            INNER JOIN departments d ON e.department_id = d.department_id
            INNER JOIN roles r ON e.role_id = r.role_id
            WHERE 
                e.first_name ILIKE %s OR
                e.last_name ILIKE %s OR
                e.email ILIKE %s OR
                d.department_name ILIKE %s OR
                r.role_title ILIKE %s
            ORDER BY e.employee_id ASC;
        """
        return execute_read(query, (pattern, pattern, pattern, pattern, pattern))

    @staticmethod
    def filter(
        department_id: Optional[int] = None,
        role_id: Optional[int] = None,
        status: Optional[str] = None,
        min_salary: Optional[float] = None,
        max_salary: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        [R] Read/Filter: Filter employees by department, role, status, and salary range.
        """
        conditions = []
        params = []

        if department_id:
            conditions.append("e.department_id = %s")
            params.append(department_id)
        if role_id:
            conditions.append("e.role_id = %s")
            params.append(role_id)
        if status:
            conditions.append("e.status = %s")
            params.append(status)
        if min_salary is not None:
            conditions.append("e.salary >= %s")
            params.append(min_salary)
        if max_salary is not None:
            conditions.append("e.salary <= %s")
            params.append(max_salary)

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"""
            SELECT 
                e.employee_id,
                e.first_name || ' ' || e.last_name AS full_name,
                e.email,
                d.department_name,
                r.role_title,
                e.salary,
                e.status
            FROM employees e
            INNER JOIN departments d ON e.department_id = d.department_id
            INNER JOIN roles r ON e.role_id = r.role_id
            {where_clause}
            ORDER BY e.employee_id ASC;
        """
        return execute_read(query, tuple(params))

    @staticmethod
    def update(employee_id: int, **kwargs) -> bool:
        """
        [U] Update: Modifies specific attributes of an employee record.
        Accepted kwargs: first_name, last_name, email, phone, hire_date,
                         department_id, role_id, salary, status.
        """
        existing = EmployeeModel.get_by_id(employee_id)
        if not existing:
            raise ValueError(f"Employee ID {employee_id} not found.")

        # Determine effective department, role, and salary for validations
        effective_role_id = kwargs.get("role_id", existing["role_id"])
        effective_salary = kwargs.get("salary", float(existing["salary"]))
        effective_dept_id = kwargs.get("department_id", existing["department_id"])

        if "department_id" in kwargs:
            if not DepartmentModel.get_by_id(effective_dept_id):
                raise ValueError(f"Department ID {effective_dept_id} does not exist.")

        if "role_id" in kwargs or "salary" in kwargs:
            role = RoleModel.get_by_id(effective_role_id)
            if not role:
                raise ValueError(f"Role ID {effective_role_id} does not exist.")
            min_sal = float(role["min_salary"])
            max_sal = float(role["max_salary"])
            if effective_salary < min_sal or effective_salary > max_sal:
                raise ValueError(f"Salary ₹{effective_salary:,.2f} is outside range for role '{role['role_title']}' [₹{min_sal:,.2f} - ₹{max_sal:,.2f}].")

        allowed_fields = [
            "first_name", "last_name", "email", "phone",
            "hire_date", "department_id", "role_id", "salary", "status"
        ]

        set_clauses = []
        params = []
        for key in allowed_fields:
            if key in kwargs and kwargs[key] is not None:
                set_clauses.append(f"{key} = %s")
                val = kwargs[key]
                if isinstance(val, str):
                    val = val.strip()
                    if key == "email":
                        val = val.lower()
                params.append(val)

        if not set_clauses:
            return False

        params.append(employee_id)
        query = f"UPDATE employees SET {', '.join(set_clauses)} WHERE employee_id = %s;"
        execute_write(query, tuple(params))
        return True

    @staticmethod
    def delete(employee_id: int) -> bool:
        """
        [D] Delete: Permanently deletes an employee record.
        """
        existing = EmployeeModel.get_by_id(employee_id)
        if not existing:
            raise ValueError(f"Employee ID {employee_id} does not exist.")

        query = "DELETE FROM employees WHERE employee_id = %s;"
        execute_write(query, (employee_id,))
        return True
