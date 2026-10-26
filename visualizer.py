"""
Data Visualizer Module for Employee Management System.
Generates publication-quality charts and analytical visual dashboards
using Matplotlib, Seaborn, and Pandas from PostgreSQL data.
"""

import os
import warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
import matplotlib
matplotlib.use('Agg')  # Headless backend for server/command-line execution
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from db_connection import get_connection

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "visualizations")


def ensure_output_dir():
    """Creates the visualization output folder if it doesn't exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_data_from_db():
    """Queries PostgreSQL database and returns DataFrames for visualization."""
    with get_connection() as conn:
        emp_query = """
            SELECT 
                e.employee_id,
                e.first_name || ' ' || e.last_name AS full_name,
                e.email,
                e.hire_date,
                d.department_name,
                d.location,
                d.budget AS dept_budget,
                r.role_title,
                r.min_salary,
                r.max_salary,
                e.salary,
                e.status
            FROM employees e
            JOIN departments d ON e.department_id = d.department_id
            JOIN roles r ON e.role_id = r.role_id;
        """
        dept_query = """
            SELECT 
                d.department_name,
                d.budget,
                COUNT(e.employee_id) AS headcount,
                COALESCE(SUM(e.salary), 0) AS total_payroll,
                COALESCE(AVG(e.salary), 0) AS avg_salary
            FROM departments d
            LEFT JOIN employees e ON d.department_id = e.department_id
            GROUP BY d.department_id, d.department_name, d.budget
            ORDER BY headcount DESC;
        """
        emp_df = pd.read_sql_query(emp_query, conn)
        dept_df = pd.read_sql_query(dept_query, conn)

    return emp_df, dept_df


def plot_department_headcount_payroll(dept_df: pd.DataFrame) -> str:
    """Generates dual-axis chart showing Headcount and Payroll by Department."""
    ensure_output_dir()
    filepath = os.path.join(OUTPUT_DIR, "1_dept_headcount_and_payroll.png")

    fig, ax1 = plt.subplots(figsize=(10, 6), dpi=300)
    plt.title("Department Headcount & Total Payroll Expenditure", fontsize=15, fontweight='bold', pad=15)

    x = range(len(dept_df))
    width = 0.35

    color_headcount = '#3b82f6'
    color_payroll = '#10b981'

    # Primary axis: Headcount
    bars1 = ax1.bar([i - width/2 for i in x], dept_df['headcount'], width=width, label='Headcount', color=color_headcount, alpha=0.85)
    ax1.set_xlabel('Department', fontsize=12, fontweight='semibold', labelpad=10)
    ax1.set_ylabel('Number of Employees', color=color_headcount, fontsize=12, fontweight='semibold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(dept_df['department_name'], rotation=20, ha='right', fontsize=10)
    ax1.tick_params(axis='y', labelcolor=color_headcount)
    ax1.grid(axis='y', linestyle='--', alpha=0.3)

    # Annotate headcount
    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(f'{int(height)}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Secondary axis: Total Payroll (in Lakhs or Thousands)
    ax2 = ax1.twinx()
    payroll_in_k = dept_df['total_payroll'] / 1000.0
    bars2 = ax2.bar([i + width/2 for i in x], payroll_in_k, width=width, label='Payroll (₹ in Thousands)', color=color_payroll, alpha=0.85)
    ax2.set_ylabel('Total Payroll (₹ in Thousands)', color=color_payroll, fontsize=12, fontweight='semibold')
    ax2.tick_params(axis='y', labelcolor=color_payroll)

    for bar in bars2:
        height = bar.get_height()
        ax2.annotate(f'₹{height:,.0f}k',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=8, color='#047857')

    plt.tight_layout()
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()
    return filepath


def plot_salary_distribution_by_role(emp_df: pd.DataFrame) -> str:
    """Generates box plot showing salary ranges by role."""
    ensure_output_dir()
    filepath = os.path.join(OUTPUT_DIR, "2_salary_distribution_by_role.png")

    plt.figure(figsize=(11, 6), dpi=300)
    sns.set_theme(style="whitegrid")

    palette = sns.color_palette("mako", n_colors=emp_df['role_title'].nunique())
    ax = sns.boxplot(
        data=emp_df,
        x="salary",
        y="role_title",
        palette=palette,
        orient="h",
        boxprops=dict(alpha=0.8)
    )
    # Overlay individual data points
    sns.stripplot(data=emp_df, x="salary", y="role_title", color="black", alpha=0.6, jitter=0.2, size=5)

    plt.title("Employee Salary Distribution Across Roles (with Data Points)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Monthly Salary (₹)", fontsize=11, fontweight='semibold')
    plt.ylabel("Job Role / Designation", fontsize=11, fontweight='semibold')
    plt.tight_layout()
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()
    return filepath


def plot_budget_vs_payroll(dept_df: pd.DataFrame) -> str:
    """Compares allocated budget versus actual payroll per department."""
    ensure_output_dir()
    filepath = os.path.join(OUTPUT_DIR, "3_budget_vs_payroll_comparison.png")

    plt.figure(figsize=(10, 6), dpi=300)
    x = range(len(dept_df))
    width = 0.35

    plt.bar([i - width/2 for i in x], dept_df['budget'], width=width, label='Allocated Budget (₹)', color='#6366f1', alpha=0.85)
    plt.bar([i + width/2 for i in x], dept_df['total_payroll'], width=width, label='Actual Payroll (₹)', color='#f59e0b', alpha=0.85)

    plt.title("Department Budget Allocation vs. Actual Payroll", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Department", fontsize=11, fontweight='semibold')
    plt.ylabel("Amount in ₹", fontsize=11, fontweight='semibold')
    plt.xticks(x, dept_df['department_name'], rotation=20, ha='right', fontsize=10)
    plt.legend(frameon=True, shadow=True)
    plt.grid(axis='y', linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()
    return filepath


def plot_executive_dashboard(emp_df: pd.DataFrame, dept_df: pd.DataFrame) -> str:
    """Generates an all-in-one 4-panel visual analytics dashboard."""
    ensure_output_dir()
    filepath = os.path.join(OUTPUT_DIR, "4_executive_dashboard.png")

    fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=300)
    fig.suptitle("Employee Management System - Visual Analytics Dashboard", fontsize=18, fontweight='bold', y=0.98)

    # 1. Department Headcount (Top Left)
    ax1 = axes[0, 0]
    sns.barplot(data=dept_df, x="department_name", y="headcount", ax=ax1, palette="Blues_r")
    ax1.set_title("1. Headcount by Department", fontsize=12, fontweight='bold')
    ax1.set_xlabel("")
    ax1.set_ylabel("Number of Employees")
    ax1.tick_params(axis='x', rotation=25)
    for p in ax1.patches:
        ax1.annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='baseline', fontsize=10, xytext=(0, 4), textcoords='offset points')

    # 2. Salary Distribution by Department (Top Right)
    ax2 = axes[0, 1]
    sns.boxplot(data=emp_df, x="department_name", y="salary", ax=ax2, palette="Purples")
    ax2.set_title("2. Salary Spread by Department", fontsize=12, fontweight='bold')
    ax2.set_xlabel("")
    ax2.set_ylabel("Salary (₹)")
    ax2.tick_params(axis='x', rotation=25)

    # 3. Payroll Distribution (Donut Chart - Bottom Left)
    ax3 = axes[1, 0]
    active_depts = dept_df[dept_df['total_payroll'] > 0]
    colors = sns.color_palette("Set2", len(active_depts))
    wedges, texts, autotexts = ax3.pie(
        active_depts['total_payroll'],
        labels=active_depts['department_name'],
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
    )
    plt.setp(autotexts, size=9, weight="bold")
    ax3.set_title("3. Department Share of Total Payroll", fontsize=12, fontweight='bold')

    # 4. Employee Employment Status Distribution (Bottom Right)
    ax4 = axes[1, 1]
    status_counts = emp_df['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    sns.barplot(data=status_counts, x="Status", y="Count", ax=ax4, palette="crest")
    ax4.set_title("4. Employee Status Overview", fontsize=12, fontweight='bold')
    ax4.set_xlabel("Employment Status")
    ax4.set_ylabel("Employee Count")
    for p in ax4.patches:
        ax4.annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='baseline', fontsize=10, xytext=(0, 4), textcoords='offset points')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()
    return filepath


def generate_all_visualizations():
    """Generates all 4 visual reports from PostgreSQL data."""
    print("[*] Fetching records from PostgreSQL for Data Visualization...")
    emp_df, dept_df = load_data_from_db()
    if emp_df.empty:
        print("[!] No employee records found in database. Please seed data first.")
        return []

    print("[*] Generating Data Visualizations with Matplotlib & Seaborn...")
    chart1 = plot_department_headcount_payroll(dept_df)
    print(f" [✓] Created: {os.path.basename(chart1)}")

    chart2 = plot_salary_distribution_by_role(emp_df)
    print(f" [✓] Created: {os.path.basename(chart2)}")

    chart3 = plot_budget_vs_payroll(dept_df)
    print(f" [✓] Created: {os.path.basename(chart3)}")

    chart4 = plot_executive_dashboard(emp_df, dept_df)
    print(f" [✓] Created: {os.path.basename(chart4)}")

    print(f"[✓] All visual charts successfully saved to: {OUTPUT_DIR}")
    return [chart1, chart2, chart3, chart4]


if __name__ == "__main__":
    generate_all_visualizations()
