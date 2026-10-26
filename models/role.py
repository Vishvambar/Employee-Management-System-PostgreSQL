"""
Role Model - CRUD Operations for Roles Table.
"""

from typing import List, Dict, Any, Optional
from db_connection import execute_read, execute_write


class RoleModel:
    """Encapsulates CRUD operations for the roles table."""

    @staticmethod
    def create(title: str, min_salary: float, max_salary: float, description: str = "") -> int:
        """
        [C] Create: Inserts a new role.
        """
        if min_salary <= 0:
            raise ValueError("Minimum salary must be greater than 0.")
        if max_salary < min_salary:
            raise ValueError("Maximum salary cannot be less than minimum salary.")

        query = """
            INSERT INTO roles (role_title, min_salary, max_salary, description)
            VALUES (%s, %s, %s, %s)
            RETURNING role_id;
        """
        role_id = execute_write(query, (title.strip(), min_salary, max_salary, description.strip()), returning_id=True)
        return role_id

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """
        [R] Read: Retrieves all roles with count of assigned employees.
        """
        query = """
            SELECT 
                r.role_id,
                r.role_title,
                r.min_salary,
                r.max_salary,
                r.description,
                COUNT(e.employee_id) AS total_employees,
                COALESCE(ROUND(AVG(e.salary), 2), 0.0) AS avg_actual_salary
            FROM roles r
            LEFT JOIN employees e ON r.role_id = e.role_id
            GROUP BY r.role_id, r.role_title, r.min_salary, r.max_salary, r.description
            ORDER BY r.role_id ASC;
        """
        return execute_read(query)

    @staticmethod
    def get_by_id(role_id: int) -> Optional[Dict[str, Any]]:
        """
        [R] Read: Retrieves a single role by ID.
        """
        query = """
            SELECT role_id, role_title, min_salary, max_salary, description, created_at
            FROM roles
            WHERE role_id = %s;
        """
        rows = execute_read(query, (role_id,))
        return rows[0] if rows else None

    @staticmethod
    def update(role_id: int, title: Optional[str] = None, min_salary: Optional[float] = None,
               max_salary: Optional[float] = None, description: Optional[str] = None) -> bool:
        """
        [U] Update: Modifies role title, salary range, or description.
        """
        role = RoleModel.get_by_id(role_id)
        if not role:
            raise ValueError(f"Role ID {role_id} not found.")

        updated_title = title.strip() if title is not None else role["role_title"]
        updated_min = min_salary if min_salary is not None else float(role["min_salary"])
        updated_max = max_salary if max_salary is not None else float(role["max_salary"])
        updated_desc = description.strip() if description is not None else role["description"]

        if updated_max < updated_min:
            raise ValueError("Maximum salary cannot be less than minimum salary.")

        query = """
            UPDATE roles
            SET role_title = %s,
                min_salary = %s,
                max_salary = %s,
                description = %s
            WHERE role_id = %s;
        """
        execute_write(query, (updated_title, updated_min, updated_max, updated_desc, role_id))
        return True

    @staticmethod
    def delete(role_id: int) -> bool:
        """
        [D] Delete: Removes a role if no employees currently hold it.
        """
        check_query = "SELECT COUNT(*) AS count FROM employees WHERE role_id = %s;"
        res = execute_read(check_query, (role_id,))
        if res and res[0]["count"] > 0:
            raise ValueError(f"Cannot delete Role ID {role_id}: {res[0]['count']} employee(s) currently hold this role.")

        query = "DELETE FROM roles WHERE role_id = %s;"
        execute_write(query, (role_id,))
        return True
