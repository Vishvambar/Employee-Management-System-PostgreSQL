"""
Department Model - CRUD Operations for Departments Table.
"""

from typing import List, Dict, Any, Optional
from db_connection import execute_read, execute_write


class DepartmentModel:
    """Encapsulates CRUD operations for the departments table."""

    @staticmethod
    def create(name: str, location: str, budget: float = 0.0) -> int:
        """
        [C] Create: Inserts a new department.
        Returns the generated department_id.
        """
        query = """
            INSERT INTO departments (department_name, location, budget)
            VALUES (%s, %s, %s)
            RETURNING department_id;
        """
        dept_id = execute_write(query, (name.strip(), location.strip(), budget), returning_id=True)
        return dept_id

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """
        [R] Read: Retrieves all departments ordered by ID.
        """
        query = """
            SELECT 
                d.department_id,
                d.department_name,
                d.location,
                d.budget,
                COUNT(e.employee_id) AS total_employees,
                COALESCE(SUM(e.salary), 0.0) AS total_payroll
            FROM departments d
            LEFT JOIN employees e ON d.department_id = e.department_id
            GROUP BY d.department_id, d.department_name, d.location, d.budget
            ORDER BY d.department_id ASC;
        """
        return execute_read(query)

    @staticmethod
    def get_by_id(department_id: int) -> Optional[Dict[str, Any]]:
        """
        [R] Read: Retrieves a single department by its primary key.
        """
        query = """
            SELECT department_id, department_name, location, budget, created_at
            FROM departments
            WHERE department_id = %s;
        """
        rows = execute_read(query, (department_id,))
        return rows[0] if rows else None

    @staticmethod
    def update(department_id: int, name: Optional[str] = None, location: Optional[str] = None, budget: Optional[float] = None) -> bool:
        """
        [U] Update: Modifies department information.
        """
        dept = DepartmentModel.get_by_id(department_id)
        if not dept:
            raise ValueError(f"Department ID {department_id} not found.")

        updated_name = name.strip() if name is not None else dept["department_name"]
        updated_location = location.strip() if location is not None else dept["location"]
        updated_budget = budget if budget is not None else dept["budget"]

        query = """
            UPDATE departments
            SET department_name = %s,
                location = %s,
                budget = %s
            WHERE department_id = %s;
        """
        execute_write(query, (updated_name, updated_location, updated_budget, department_id))
        return True

    @staticmethod
    def delete(department_id: int) -> bool:
        """
        [D] Delete: Removes a department if no employees are assigned to it.
        """
        # Safety check: Prevent deletion if foreign key constraint would fail
        check_query = "SELECT COUNT(*) AS count FROM employees WHERE department_id = %s;"
        res = execute_read(check_query, (department_id,))
        if res and res[0]["count"] > 0:
            raise ValueError(f"Cannot delete Department ID {department_id}: {res[0]['count']} employee(s) are currently assigned to it.")

        query = "DELETE FROM departments WHERE department_id = %s;"
        execute_write(query, (department_id,))
        return True
