"""
Analytics Module - Advanced Relational Queries and Aggregations.
Provides analytical insights combining Employees, Departments, and Roles.
"""

from typing import List, Dict, Any
from db_connection import execute_read


class AnalyticsService:
    """Provides analytical aggregation queries for executive reports."""

    @staticmethod
    def get_department_analytics() -> List[Dict[str, Any]]:
        """
        Calculates department headcount, average salary, total payroll,
        and budget utilization percentage.
        """
        query = """
            SELECT 
                d.department_id,
                d.department_name,
                d.location,
                d.budget,
                COUNT(e.employee_id) AS total_employees,
                COALESCE(ROUND(AVG(e.salary), 2), 0.0) AS avg_salary,
                COALESCE(ROUND(MIN(e.salary), 2), 0.0) AS min_salary,
                COALESCE(ROUND(MAX(e.salary), 2), 0.0) AS max_salary,
                COALESCE(ROUND(SUM(e.salary), 2), 0.0) AS total_payroll,
                CASE 
                    WHEN d.budget > 0 THEN ROUND((COALESCE(SUM(e.salary), 0.0) / d.budget) * 100, 2)
                    ELSE 0.0
                END AS budget_utilization_pct
            FROM departments d
            LEFT JOIN employees e ON d.department_id = e.department_id
            GROUP BY d.department_id, d.department_name, d.location, d.budget
            ORDER BY total_payroll DESC;
        """
        return execute_read(query)

    @staticmethod
    def get_role_analytics() -> List[Dict[str, Any]]:
        """
        Calculates role-based salary bands vs. actual employee salaries.
        """
        query = """
            SELECT 
                r.role_id,
                r.role_title,
                r.min_salary,
                r.max_salary,
                COUNT(e.employee_id) AS headcount,
                COALESCE(ROUND(AVG(e.salary), 2), 0.0) AS avg_actual_salary,
                COALESCE(ROUND(MIN(e.salary), 2), 0.0) AS min_actual_salary,
                COALESCE(ROUND(MAX(e.salary), 2), 0.0) AS max_actual_salary
            FROM roles r
            LEFT JOIN employees e ON r.role_id = e.role_id
            GROUP BY r.role_id, r.role_title, r.min_salary, r.max_salary
            ORDER BY headcount DESC, r.role_id ASC;
        """
        return execute_read(query)

    @staticmethod
    def get_top_earners(limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves the top N highest-paid employees in the organization.
        """
        query = """
            SELECT 
                e.employee_id,
                e.first_name || ' ' || e.last_name AS employee_name,
                d.department_name,
                r.role_title,
                e.salary,
                e.status
            FROM employees e
            JOIN departments d ON e.department_id = d.department_id
            JOIN roles r ON e.role_id = r.role_id
            ORDER BY e.salary DESC
            LIMIT %s;
        """
        return execute_read(query, (limit,))

    @staticmethod
    def get_tenure_analysis() -> List[Dict[str, Any]]:
        """
        Calculates employee tenure and service years.
        """
        query = """
            SELECT 
                e.employee_id,
                e.first_name || ' ' || e.last_name AS employee_name,
                d.department_name,
                r.role_title,
                e.hire_date,
                ROUND((CURRENT_DATE - e.hire_date) / 365.25, 1) AS years_of_service,
                e.salary
            FROM employees e
            JOIN departments d ON e.department_id = d.department_id
            JOIN roles r ON e.role_id = r.role_id
            ORDER BY hire_date ASC;
        """
        return execute_read(query)
