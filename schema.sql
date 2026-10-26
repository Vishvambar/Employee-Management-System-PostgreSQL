-- Database Schema: Employee Management System (PostgreSQL)
-- Enterprise Relational Schema for Departments, Roles, and Employees
-- ============================================================================

-- Drop views & tables in reverse order of foreign key dependency if exists
DROP VIEW IF EXISTS v_employee_details;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS roles CASCADE;
DROP TABLE IF EXISTS departments CASCADE;

-- 1. Departments Table
CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(100) NOT NULL,
    budget NUMERIC(12, 2) DEFAULT 0.00 CHECK (budget >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Roles Table
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role_title VARCHAR(100) NOT NULL UNIQUE,
    min_salary NUMERIC(10, 2) NOT NULL CHECK (min_salary > 0),
    max_salary NUMERIC(10, 2) NOT NULL CHECK (max_salary >= min_salary),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Employees Table
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    hire_date DATE NOT NULL DEFAULT CURRENT_DATE,
    department_id INT NOT NULL REFERENCES departments(department_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    role_id INT NOT NULL REFERENCES roles(role_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    salary NUMERIC(10, 2) NOT NULL CHECK (salary > 0),
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'On Leave', 'Resigned', 'Terminated')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Indexes for performance on frequently queried Foreign Keys & Emails
CREATE INDEX idx_employees_dept ON employees(department_id);
CREATE INDEX idx_employees_role ON employees(role_id);
CREATE INDEX idx_employees_email ON employees(email);

-- Trigger function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_employee_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_employee_timestamp
BEFORE UPDATE ON employees
FOR EACH ROW
EXECUTE FUNCTION update_employee_timestamp();

-- Unified View for Employee Details with JOINs
CREATE VIEW v_employee_details AS
SELECT 
    e.employee_id,
    e.first_name || ' ' || e.last_name AS full_name,
    e.email,
    e.phone,
    e.hire_date,
    d.department_name,
    d.location AS department_location,
    r.role_title,
    e.salary,
    e.status,
    e.created_at,
    e.updated_at
FROM employees e
INNER JOIN departments d ON e.department_id = d.department_id
INNER JOIN roles r ON e.role_id = r.role_id;
