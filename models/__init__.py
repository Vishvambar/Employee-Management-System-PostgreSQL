"""
Models Package for Employee Management System.
Contains CRUD operation modules for Departments, Roles, and Employees.
"""

from .department import DepartmentModel
from .role import RoleModel
from .employee import EmployeeModel

__all__ = ["DepartmentModel", "RoleModel", "EmployeeModel"]
