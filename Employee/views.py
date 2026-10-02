from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    Employee,
    Leave,
    Salary,
    Department,
    Attendance,
    SupportRequest,
    Performance,
    Document,
    Notification,
)

from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
from functools import wraps

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib.units import inch
from reportlab.lib import colors

from datetime import date


# ============================================================
# SESSION / ACCESS CONTROL
# ============================================================


def admin_required(view_func):
    """
    Allow only authenticated Django superusers to access admin pages.
    The @never_cache decorator prevents protected pages from being shown
    from the browser cache after logout.
    """
    @wraps(view_func)
    @never_cache
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("admin_login")

        if not request.user.is_superuser:
            django_logout(request)
            return redirect("admin_login")

        return view_func(request, *args, **kwargs)

    return wrapper


def employee_required(view_func):
    """
    Only logged-in employees can access employee pages.
    Uses session-based employee authentication.
    """

    @wraps(view_func)
    @never_cache
    def wrapper(request, *args, **kwargs):

        emp_id = request.session.get("emp_id")

        # No employee session
        if not emp_id:
            return redirect("employee_login")

        try:
            Employee.objects.get(id=emp_id)

        except Employee.DoesNotExist:
            request.session.flush()
            return redirect("employee_login")

        return view_func(request, *args, **kwargs)

    return wrapper


# ============================================================
# HOME
# ============================================================


def index(request):
    return render(request, "index.html")


# ============================================================
# ADMIN LOGIN
# ============================================================


@never_cache
def admin_login(request):

    # Already logged-in admin
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin_home")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_superuser:

            login(request, user)

            return redirect("admin_home")

        return render(
            request,
            "admin_login.html",
            {
                "error": "Invalid Username or Password"
            }
        )

    return render(request, "admin_login.html")


# ============================================================
# ADMIN DASHBOARD
# ============================================================


@admin_required
def admin_home(request):
    return render(request, "admin_home.html")


# ============================================================
# EMPLOYEE MANAGEMENT
# ============================================================


@admin_required
def employee_management(request):
    return render(request, "employee_management.html")


@admin_required
def view_employee(request):

    search = request.GET.get("search")

    employees = Employee.objects.all()

    if search:

        employees = employees.filter(
            Q(name__icontains=search)
            | Q(username__icontains=search)
            | Q(email__icontains=search)
            | Q(department__icontains=search)
        )

    return render(
        request,
        "view_employee.html",
        {
            "employees": employees
        }
    )


@admin_required
def delete_employee(request):
    return render(request, "delete_employee.html")


@admin_required
def edit_employee(request, id):

    employee = get_object_or_404(Employee, id=id)

    salary = get_object_or_404(
        Salary,
        employee=employee
    )

    if request.method == "POST":

        employee.name = request.POST.get("name")
        employee.email = request.POST.get("email")
        employee.username = request.POST.get("username")
        employee.department = request.POST.get("department")
        employee.joindate = request.POST.get("joindate")
        employee.phone = request.POST.get("phone")

        employee.save()

        salary.basic_salary = request.POST.get("salary")
        salary.total_salary = salary.basic_salary

        salary.save()

        return redirect("view_employee")

    return render(
        request,
        "edit_employee.html",
        {
            "employee": employee,
            "salary": salary
        }
    )


# ============================================================
# DEPARTMENT MANAGEMENT
# ============================================================


@admin_required
def department_management(request):

    departments = Department.objects.all()

    return render(
        request,
        "department_management.html",
        {
            "departments": departments
        }
    )


@admin_required
def add_department(request):

    if request.method == "POST":

        department_name = request.POST.get("department_name")
        department_code = request.POST.get("department_code")
        department_head = request.POST.get("department_head")
        description = request.POST.get("description")

        Department.objects.create(
            department_name=department_name,
            department_code=department_code,
            department_head=department_head,
            description=description
        )

        return redirect("view_department")

    return render(
        request,
        "add_department.html"
    )


@admin_required
def view_department(request):

    departments = Department.objects.all()

    return render(
        request,
        "view_department.html",
        {
            "departments": departments
        }
    )


@admin_required
def edit_department(request, id):

    department = get_object_or_404(
        Department,
        id=id
    )

    if request.method == "POST":

        department.department_name = request.POST.get(
            "department_name"
        )

        department.department_code = request.POST.get(
            "department_code"
        )

        department.department_head = request.POST.get(
            "department_head"
        )

        department.description = request.POST.get(
            "description"
        )

        department.save()

        return redirect("view_department")

    return render(
        request,
        "edit_department.html",
        {
            "department": department
        }
    )


@admin_required
def delete_department(request, id):

    department = get_object_or_404(
        Department,
        id=id
    )

    department.delete()

    return redirect("view_department")


@admin_required
def search_department(request):

    query = request.GET.get("q", "")

    departments = Department.objects.filter(
        department_name__icontains=query
    ) | Department.objects.filter(
        department_code__icontains=query
    ) | Department.objects.filter(
        department_head__icontains=query
    )

    return render(
        request,
        "view_department.html",
        {
            "departments": departments,
            "query": query
        }
    )


# ============================================================
# SALARY MANAGEMENT
# ============================================================


@admin_required
def salary_management(request):

    salaries = Salary.objects.all()

    return render(
        request,
        "salary_management.html",
        {
            "salaries": salaries
        }
    )


@admin_required
def add_salary(request):

    employees = Employee.objects.all()

    if request.method == "POST":

        employee_id = request.POST.get("employee")

        basic_salary = int(
            request.POST.get("basic_salary") or 0
        )

        bonus = int(
            request.POST.get("bonus") or 0
        )

        deduction = int(
            request.POST.get("deduction") or 0
        )

        total_salary = (
            basic_salary
            + bonus
            - deduction
        )

        employee = get_object_or_404(
            Employee,
            id=employee_id
        )

        Salary.objects.create(
            employee=employee,
            basic_salary=basic_salary,
            bonus=bonus,
            deduction=deduction,
            total_salary=total_salary
        )

        return redirect("view_salary")

    return render(
        request,
        "add_salary.html",
        {
            "employees": employees
        }
    )


@admin_required
def view_salary(request):

    salaries = Salary.objects.select_related(
        "employee"
    ).all()

    query = request.GET.get("q", "")

    if query:

        salaries = salaries.filter(
            Q(employee__name__icontains=query)
            | Q(employee__username__icontains=query)
        )

    return render(
        request,
        "view_salary.html",
        {
            "salaries": salaries,
            "query": query
        }
    )


@admin_required
def edit_salary(request, id):

    salary = get_object_or_404(
        Salary,
        id=id
    )

    if request.method == "POST":

        salary.basic_salary = int(
            request.POST.get("basic_salary") or 0
        )

        salary.bonus = int(
            request.POST.get("bonus") or 0
        )

        salary.deduction = int(
            request.POST.get("deduction") or 0
        )

        salary.total_salary = (
            salary.basic_salary
            + salary.bonus
            - salary.deduction
        )

        salary.save()

        return redirect("view_salary")

    return render(
        request,
        "edit_salary.html",
        {
            "salary": salary
        }
    )


@admin_required
def delete_salary(request, id):

    salary = get_object_or_404(
        Salary,
        id=id
    )

    if request.method == "POST":

        salary.delete()

        return redirect("view_salary")

    return render(
        request,
        "delete_salary.html",
        {
            "salary": salary
        }
    )


# ============================================================
# ATTENDANCE MANAGEMENT
# ============================================================


@admin_required
def attendance_management(request):

    attendances = Attendance.objects.all()

    return render(
        request,
        "attendance_management.html",
        {
            "attendances": attendances
        }
    )


@admin_required
def mark_attendance(request):

    employees = Employee.objects.all()

    today = timezone.localdate()

    if request.method == "POST":

        employee_id = request.POST.get("employee")
        submitted_date = request.POST.get("date")
        status = request.POST.get("status")
        remarks = request.POST.get("remarks")

        employee = get_object_or_404(
            Employee,
            id=employee_id
        )

        # Only today's attendance allowed
        if submitted_date != str(today):

            messages.error(
                request,
                "Attendance can only be marked for today."
            )

            return redirect("mark_attendance")

        # Check existing attendance
        already_marked = Attendance.objects.filter(
            employee=employee,
            date=today
        ).exists()

        if already_marked:

            messages.error(
                request,
                f"{employee.name} ki aaj ki attendance already marked hai."
            )

            return redirect("mark_attendance")

        Attendance.objects.create(
            employee=employee,
            date=today,
            status=status,
            remarks=remarks
        )

        messages.success(
            request,
            f"{employee.name} ki attendance successfully marked."
        )

        return redirect("view_attendance")

    return render(
        request,
        "mark_attendance.html",
        {
            "employees": employees,
            "today": today
        }
    )


@admin_required
def view_attendance(request):

    attendances = Attendance.objects.select_related(
        "employee"
    ).all()

    query = request.GET.get(
        "q",
        ""
    ).strip()

    if query:

        attendances = attendances.filter(
            Q(employee__name__icontains=query)
            | Q(status__icontains=query)
            | Q(date__icontains=query)
            | Q(remarks__icontains=query)
        )

    return render(
        request,
        "view_attendance.html",
        {
            "attendances": attendances,
            "query": query
        }
    )


@admin_required
def edit_attendance(request, id):

    attendance = get_object_or_404(
        Attendance,
        id=id
    )

    employees = Employee.objects.all()

    if request.method == "POST":

        employee_id = request.POST.get(
            "employee"
        )

        submitted_date = request.POST.get(
            "date"
        )

        status = request.POST.get(
            "status"
        )

        remarks = request.POST.get(
            "remarks"
        )

        employee = get_object_or_404(
            Employee,
            id=employee_id
        )

        attendance.employee = employee
        attendance.date = submitted_date
        attendance.status = status
        attendance.remarks = remarks

        attendance.save()

        return redirect(
            "view_attendance"
        )

    return render(
        request,
        "edit_attendance.html",
        {
            "attendance": attendance,
            "employees": employees
        }
    )


@admin_required
def delete_attendance(request, id):

    attendance = get_object_or_404(
        Attendance,
        id=id
    )

    if request.method == "POST":

        attendance.delete()

        return redirect(
            "view_attendance"
        )

    return render(
        request,
        "delete_attendance.html",
        {
            "attendance": attendance
        }
    )


# ============================================================
# EMPLOYEE REGISTRATION
# ============================================================


def register(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        username = request.POST.get("uname")
        password = request.POST.get("password")
        department = request.POST.get("department")
        salary = request.POST.get("salary")
        joindate = request.POST.get("joindate")
        phone = request.POST.get("phone")

        if Employee.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                "Email already exists!"
            )

            return redirect("register")

        if Employee.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists!"
            )

            return redirect("register")

        emp = Employee.objects.create(
            name=name,
            email=email,
            username=username,
            password=password,
            department=department,
            joindate=joindate,
            phone=phone
        )

        Salary.objects.create(
            employee=emp,
            basic_salary=salary,
            bonus=0,
            deduction=0,
            total_salary=salary
        )

        return redirect(
            "employee_login"
        )

    return render(
        request,
        "register.html"
    )


# ============================================================
# EMPLOYEE LOGIN
# ============================================================


@never_cache
def employee_login(request):

    # If already logged in
    if request.session.get("emp_id"):
        return redirect("employee_home")

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        try:

            emp = Employee.objects.get(
                username=username,
                password=password
            )

            # Clear old session data
            request.session.flush()

            # Create new employee session
            request.session["emp_id"] = emp.id

            return redirect(
                "employee_home"
            )

        except Employee.DoesNotExist:

            return render(
                request,
                "employee_login.html",
                {
                    "error": "Invalid Username or Password"
                }
            )

    return render(
        request,
        "employee_login.html"
    )


# ============================================================
# EMPLOYEE HOME
# ============================================================


@employee_required
def employee_home(request):

    return render(
        request,
        "employee_home.html"
    )


# ============================================================
# EMPLOYEE PROFILE
# ============================================================


@employee_required
def my_profile(request):

    emp = Employee.objects.get(
        id=request.session["emp_id"]
    )

    salary = Salary.objects.filter(
        employee=emp
    ).first()

    return render(
        request,
        "my_profile.html",
        {
            "employee": emp,
            "salary": salary
        }
    )


@employee_required
def edit_profile(request):

    emp = Employee.objects.get(
        id=request.session["emp_id"]
    )

    if request.method == "POST":

        emp.name = request.POST.get(
            "name"
        )

        emp.email = request.POST.get(
            "email"
        )

        emp.department = request.POST.get(
            "department"
        )

        emp.joindate = request.POST.get(
            "joindate"
        )

        emp.phone = request.POST.get(
            "phone"
        )

        emp.save()

        return redirect(
            "my_profile"
        )

    return render(
        request,
        "edit_profile.html",
        {
            "employee": emp
        }
    )


# ============================================================
# EMPLOYEE SALARY
# ============================================================


@employee_required
def salary(request):

    emp = Employee.objects.get(
        id=request.session["emp_id"]
    )

    salary_data = Salary.objects.filter(
        employee=emp
    ).first()

    return render(
        request,
        "salary.html",
        {
            "salary": salary_data
        }
    )


# ============================================================
# DOWNLOAD PAYSLIP
# ============================================================


@employee_required
def download_payslip(request):

    emp = Employee.objects.get(
        id=request.session["emp_id"]
    )

    sal = Salary.objects.get(
        employee=emp
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="Payslip.pdf"'

    doc = SimpleDocTemplate(
        response
    )

    styles = getSampleStyleSheet()

    title = styles["Heading1"]

    title.alignment = TA_CENTER
    title.textColor = HexColor(
        "#0d6efd"
    )

    elements = []

    elements.append(
        Paragraph(
            "<b>EMPLOYEE MANAGEMENT SYSTEM</b>",
            title
        )
    )

    elements.append(
        Paragraph(
            "<b>MONTHLY PAYSLIP</b>",
            title
        )
    )

    elements.append(
        Spacer(1, 20)
    )

    company = Table(
        [
            [
                "Company",
                "ABC Technologies Pvt. Ltd."
            ],
            [
                "Address",
                "Lucknow, Uttar Pradesh"
            ],
            [
                "Date",
                str(date.today())
            ],
            [
                "Status",
                "PAID"
            ]
        ]
    )

    company.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.lightblue
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ]
        )
    )

    elements.append(company)

    elements.append(
        Spacer(1, 20)
    )

    employee_table = Table(
        [
            [
                "Employee Name",
                emp.name
            ],
            [
                "Email",
                emp.email
            ],
            [
                "Department",
                emp.department
            ],
            [
                "Joining Date",
                str(emp.joindate)
            ],
        ]
    )

    employee_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.beige
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black
                )
            ]
        )
    )

    elements.append(
        employee_table
    )

    elements.append(
        Spacer(1, 20)
    )

    salary_table = Table(
        [
            [
                "Salary Head",
                "Amount"
            ],
            [
                "Basic Salary",
                f"₹ {sal.basic_salary}"
            ],
            [
                "Bonus",
                f"₹ {sal.bonus}"
            ],
            [
                "Deduction",
                f"₹ {sal.deduction}"
            ],
            [
                "Net Salary",
                f"₹ {sal.total_salary}"
            ],
        ]
    )

    salary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.darkblue
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "BACKGROUND",
                    (0, 4),
                    (-1, 4),
                    colors.green
                ),
                (
                    "TEXTCOLOR",
                    (0, 4),
                    (-1, 4),
                    colors.white
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ]
        )
    )

    elements.append(
        salary_table
    )

    elements.append(
        Spacer(1, 25)
    )

    footer = Paragraph(
        "<b>This is a computer generated payslip.</b><br/>"
        "No signature is required.<br/><br/>"
        "Employee Management System",
        styles["Normal"]
    )

    elements.append(
        footer
    )

    doc.build(elements)

    return response


# ============================================================
# CONTACT / SUPPORT
# ============================================================


def contact(request):

    message_sent = False

    emp_id = request.session.get(
        "emp_id"
    )

    employee = None

    if emp_id:

        try:

            employee = Employee.objects.get(
                id=emp_id
            )

        except Employee.DoesNotExist:

            request.session.flush()

    if request.method == "POST":

        name = request.POST.get(
            "name"
        )

        email = request.POST.get(
            "email"
        )

        message = request.POST.get(
            "message"
        )

        SupportRequest.objects.create(
            name=name,
            email=email,
            message=message
        )

        message_sent = True

    return render(
        request,
        "contact.html",
        {
            "employee": employee,
            "message_sent": message_sent
        }
    )


# ============================================================
# ADMIN LOGOUT
# ============================================================


@never_cache
def logout_admin(request):

    # Django authentication logout
    django_logout(request)

    # Completely clear session
    request.session.flush()

    return redirect(
        "admin_login"
    )


# ============================================================
# EMPLOYEE LOGOUT
# ============================================================


@never_cache
def logout_employee(request):

    # Clear employee session
    request.session.flush()

    return redirect(
        "employee_login"
    )


# ============================================================
# LEAVE MANAGEMENT
# ============================================================


@admin_required
def leave_management(request):

    leaves = Leave.objects.all()

    return render(
        request,
        "leave_management.html",
        {
            "leaves": leaves
        }
    )


@admin_required
def add_leave(request):

    employees = Employee.objects.all()

    if request.method == "POST":

        # Yahan tum apne existing
        # leave creation logic ko continue kar sakte ho.

        pass

    return render(
        request,
        "add_leave.html",
        {
            "employees": employees
        }
    )
