"""
URL configuration for Employee_Managemnt_System project.

The `urlpatterns` list routes URLs to views.
"""

from django.contrib import admin
from django.urls import path
from Employee.views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # =========================================================
    # Django Admin
    # =========================================================
    path("admin/", admin.site.urls),

    # =========================================================
    # Public Pages
    # =========================================================
    path("", index, name="home"),
    path("contact", contact, name="contact"),
    path("register", register, name="register"),

    # =========================================================
    # Admin Authentication
    # =========================================================
    path("admin_login", admin_login, name="admin_login"),
    path("admin_home", admin_home, name="admin_home"),
    path("logout_admin", logout_admin, name="logout_admin"),

    # =========================================================
    # Employee Authentication
    # =========================================================
    path("employee_login", employee_login, name="employee_login"),
    path("employee_home", employee_home, name="employee_home"),
    path("logout", logout_employee, name="logout"),

    # =========================================================
    # Employee Management
    # =========================================================
    path(
        "employee_management",
        employee_management,
        name="employee_management"
    ),
    path(
        "edit_employee/<int:id>/",
        edit_employee,
        name="edit_employee"
    ),
    path(
        "view_employee",
        view_employee,
        name="view_employee"
    ),
    path(
        "delete_employee/<int:id>/",
        delete_employee,
        name="delete_employee"
    ),

    # =========================================================
    # Department Management
    # =========================================================
    path(
        "department_management",
        department_management,
        name="department_management"
    ),
    path(
        "add_department",
        add_department,
        name="add_department"
    ),
    path(
        "view_department",
        view_department,
        name="view_department"
    ),
    path(
        "edit_department/<int:id>/",
        edit_department,
        name="edit_department"
    ),
    path(
        "delete_department/<int:id>/",
        delete_department,
        name="delete_department"
    ),
    path(
        "search_department",
        search_department,
        name="search_department"
    ),

    # =========================================================
    # Salary Management
    # =========================================================
    path(
        "salary_management",
        salary_management,
        name="salary_management"
    ),
    path(
        "add_salary",
        add_salary,
        name="add_salary"
    ),
    path(
        "view_salary",
        view_salary,
        name="view_salary"
    ),
    path(
        "edit_salary/<int:id>/",
        edit_salary,
        name="edit_salary"
    ),
    path(
        "delete_salary/<int:id>/",
        delete_salary,
        name="delete_salary"
    ),

    # =========================================================
    # Attendance Management - Admin
    # =========================================================
    path(
        "attendance_management/",
        attendance_management,
        name="attendance_management"
    ),
    path(
        "mark_attendance/",
        mark_attendance,
        name="mark_attendance"
    ),
    path(
        "view_attendance/",
        view_attendance,
        name="view_attendance"
    ),
    path(
        "edit_attendance/<int:id>/",
        edit_attendance,
        name="edit_attendance"
    ),
    path(
        "delete_attendance/<int:id>/",
        delete_attendance,
        name="delete_attendance"
    ),

    # =========================================================
    # Leave Management
    # =========================================================
    path(
        "leave_management",
        leave_management,
        name="leave_management"
    ),
    path(
        "add_leave",
        add_leave,
        name="add_leave"
    ),
    path(
        "view_leave",
        view_leave,
        name="view_leave"
    ),
    path(
        "edit_leave/<int:id>/",
        edit_leave,
        name="edit_leave"
    ),
    path(
        "delete_leave/<int:id>/",
        delete_leave,
        name="delete_leave"
    ),
    path(
        "approve_leave/<int:id>/",
        approve_leave,
        name="approve_leave"
    ),
    path(
        "reject_leave/<int:id>/",
        reject_leave,
        name="reject_leave"
    ),

    # =========================================================
    # Reports
    # =========================================================
    path(
        "reports",
        reports,
        name="reports"
    ),

    # =========================================================
    # Admin Profile & Settings
    # =========================================================
    path(
        "admin_profile/",
        admin_profile,
        name="admin_profile"
    ),
    path(
        "edit_admin_profile/",
        edit_admin_profile,
        name="edit_admin_profile"
    ),
    path(
        "change_admin_password/",
        change_admin_password,
        name="change_admin_password"
    ),
    path(
        "admin_settings/",
        admin_settings,
        name="admin_settings"
    ),

    # =========================================================
    # Admin Support
    # =========================================================
    path(
        "admin_support/",
        admin_support,
        name="admin_support"
    ),
    path(
        "support_requests/",
        support_requests,
        name="support_requests"
    ),
    path(
        "resolve_support/<int:id>/",
        resolve_support,
        name="resolve_support"
    ),
    path(
        "delete_support/<int:id>/",
        delete_support,
        name="delete_support"
    ),

    # =========================================================
    # Employee Pages
    # =========================================================
    path(
        "employee-attendance/",
        employee_attendance,
        name="employee_attendance"
    ),
    path(
        "employee-leave/",
        employee_leave,
        name="employee_leave"
    ),
    path(
        "employee-documents/",
        employee_documents,
        name="employee_documents"
    ),
    path(
        "employee-notifications/",
        employee_notifications,
        name="employee_notifications"
    ),
    path(
        "employee-support/",
        employee_support,
        name="employee_support"
    ),
    path(
        "employee-change-password/",
        employee_change_password,
        name="employee_change_password"
    ),

    # =========================================================
    # Admin Documents & Notifications
    # =========================================================
    path(
        "admin-documents/",
        admin_documents,
        name="admin_documents"
    ),
    path(
        "admin-notifications/",
        admin_notifications,
        name="admin_notifications"
    ),

    # =========================================================
    # Performance Management
    # =========================================================
    path(
        "performance-management/",
        performance_management,
        name="performance_management"
    ),
    path(
        "add-performance/",
        add_performance,
        name="add_performance"
    ),
    path(
        "edit-performance/<int:id>/",
        edit_performance,
        name="edit_performance"
    ),
    path(
        "delete-performance/<int:id>/",
        delete_performance,
        name="delete_performance"
    ),

    # =========================================================
    # Employee Profile
    # =========================================================
    path(
        "my_profile",
        my_profile,
        name="my_profile"
    ),
    path(
        "edit_profile",
        edit_profile,
        name="edit_profile"
    ),

    # =========================================================
    # Employee Salary & Payslip
    # =========================================================
    path(
        "salary",
        salary,
        name="salary"
    ),
    path(
        "download_payslip",
        download_payslip,
        name="download_payslip"
    ),
]


# =============================================================
# Media Files
# =============================================================
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
