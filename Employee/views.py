from django.shortcuts import render, redirect , get_object_or_404
from .models import Employee, Leave, Salary, Department, Attendance, SupportRequest, Performance, Document, Notification
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import date
from django.db import models
from django.contrib.auth.models import User

# Create your views here.

def index(request):
    return render(request,"index.html")


def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect("admin_home")   # apne admin dashboard ka URL

        return render(request, "admin_login.html", {
            "error": "Invalid Username or Password"
        })

    return render(request, "admin_login.html")

def admin_home(request):
    return render(request,"admin_home.html")

def employee_management(request):
    return render(request,"employee_management.html")


# DEPARTMENT MANAGEMENT


def department_management(request):
    departments = Department.objects.all()

    return render(
        request,
        "department_management.html",
        {"departments": departments}
    )


# =========================
# ADD DEPARTMENT
# =========================

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

    return render(request, "add_department.html")


# =========================
# VIEW DEPARTMENT
# =========================

def view_department(request):

    departments = Department.objects.all()

    return render(
        request,
        "view_department.html",
        {"departments": departments}
    )


# =========================
# EDIT / UPDATE DEPARTMENT
# =========================

def edit_department(request, id):

    department = get_object_or_404(Department, id=id)

    if request.method == "POST":

        department.department_name = request.POST.get("department_name")
        department.department_code = request.POST.get("department_code")
        department.department_head = request.POST.get("department_head")
        department.description = request.POST.get("description")

        department.save()

        return redirect("view_department")

    return render(
        request,
        "edit_department.html",
        {"department": department}
    )


# =========================
# DELETE DEPARTMENT
# =========================

def delete_department(request, id):

    department = get_object_or_404(Department, id=id)

    department.delete()

    return redirect("view_department")


# =========================
# SEARCH DEPARTMENT
# =========================

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

def salary_management(request):
    salaries = Salary.objects.all()

    return render(request, "salary_management.html", {
        "salaries": salaries
    })

def add_salary(request):

    employees = Employee.objects.all()

    if request.method == "POST":

        employee_id = request.POST.get("employee")
        basic_salary = int(request.POST.get("basic_salary") or 0)
        bonus = int(request.POST.get("bonus") or 0)
        deduction = int(request.POST.get("deduction") or 0)

        total_salary = basic_salary + bonus - deduction

        employee = get_object_or_404(Employee, id=employee_id)

        Salary.objects.create(
            employee=employee,
            basic_salary=basic_salary,
            bonus=bonus,
            deduction=deduction,
            total_salary=total_salary
        )

        return redirect("view_salary")

    return render(request, "add_salary.html", {
        "employees": employees
    })

def view_salary(request):
    salaries = Salary.objects.select_related("employee").all()

    query = request.GET.get("q", "")

    if query:
        salaries = salaries.filter(
            employee__name__icontains=query
        ) | salaries.filter(
            employee__username__icontains=query
        )

    return render(request, "view_salary.html", {
        "salaries": salaries,
        "query": query
    })

def edit_salary(request, id):

    salary = get_object_or_404(Salary, id=id)

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

def delete_salary(request, id):
    salary = get_object_or_404(Salary, id=id)

    if request.method == "POST":
        salary.delete()
        return redirect("view_salary")

    return render(
        request,
        "delete_salary.html",
        {"salary": salary}
    )




def view_employee(request):
    search = request.GET.get("search")

    employees = Employee.objects.all()

    if search:
        employees = employees.filter(
            Q(name__icontains=search) |
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(department__icontains=search)
        )

    return render(request, "view_employee.html", {
        "employees": employees
    })

def attendance_management(request):

    attendances = Attendance.objects.all()

    return render(
        request,
        "attendance_management.html",
        {
            "attendances": attendances
        }
    )


def mark_attendance(request):

    employees = Employee.objects.all()

    today = timezone.localdate()

    if request.method == "POST":

        employee_id = request.POST.get("employee")
        date = request.POST.get("date")
        status = request.POST.get("status")
        remarks = request.POST.get("remarks")

        employee = get_object_or_404(
            Employee,
            id=employee_id
        )

        # Sirf aaj ki attendance allow hogi
        if date != str(today):

            messages.error(
                request,
                "Attendance can only be marked for today."
            )

            return redirect("mark_attendance")

        # Check: aaj already attendance lagi hai ya nahi
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


def view_attendance(request):

    attendances = Attendance.objects.select_related("employee").all()

    query = request.GET.get("q", "").strip()

    if query:
        attendances = attendances.filter(
            Q(employee__name__icontains=query) |
            Q(status__icontains=query) |
            Q(date__icontains=query) |
            Q(remarks__icontains=query)
        )

    return render(
        request,
        "view_attendance.html",
        {
            "attendances": attendances,
            "query": query
        }
    )

def edit_attendance(request, id):

    attendance = get_object_or_404(Attendance, id=id)

    employees = Employee.objects.all()

    if request.method == "POST":

        employee_id = request.POST.get("employee")
        date = request.POST.get("date")
        status = request.POST.get("status")
        remarks = request.POST.get("remarks")

        employee = get_object_or_404(
            Employee,
            id=employee_id
        )

        attendance.employee = employee
        attendance.date = date
        attendance.status = status
        attendance.remarks = remarks

        attendance.save()

        return redirect("view_attendance")

    return render(
        request,
        "edit_attendance.html",
        {
            "attendance": attendance,
            "employees": employees
        }
    )

def delete_attendance(request, id):

    attendance = get_object_or_404(
        Attendance,
        id=id
    )

    if request.method == "POST":
        attendance.delete()
        return redirect("view_attendance")

    return render(
        request,
        "delete_attendance.html",
        {
            "attendance": attendance
        }
    )



def delete_employee(request):
    return render(request,"delete_employee.html")

def edit_employee(request, id):
    employee = get_object_or_404(Employee, id=id)
    salary = get_object_or_404(Salary, employee=employee)

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

    return render(request, "edit_employee.html", {
        "employee": employee,
        "salary": salary
    })



def employee_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            emp = Employee.objects.get(username=username, password=password)
            request.session["emp_id"] = emp.id
            return redirect("employee_home")
        except Employee.DoesNotExist:
            pass

    return render(request, "employee_login.html")

def contact(request):

    message_sent = False

    emp_id = request.session.get("emp_id")

    employee = None

    if emp_id:
        employee = Employee.objects.get(id=emp_id)

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

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

        if Employee.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("register")

        if Employee.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
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
        return redirect("employee_login")

    return render(request, "register.html")

def employee_home(request):
    return render(request,"employee_home.html")

def my_profile(request):
    emp = Employee.objects.get(id=request.session['emp_id'])
    salary = Salary.objects.filter(employee=emp).first()

    return render(request, "my_profile.html",{"employee": emp,"salary": salary})

def edit_profile(request):

    emp = Employee.objects.get(id=request.session['emp_id'])

    if request.method == "POST":
        emp.name = request.POST.get("name")
        emp.email = request.POST.get("email")
        emp.department = request.POST.get("department")
        
        emp.joindate = request.POST.get("joindate")
        emp.phone = request.POST.get("phone")

        emp.save()

        return redirect("my_profile")

    return render(request, "edit_profile.html", {"employee": emp})

def salary(request):
    emp = Employee.objects.get(id=request.session['emp_id'])
    salary = Salary.objects.filter(employee=emp).first()
    return render(request, "salary.html", {"salary": salary})



def download_payslip(request):

    emp = Employee.objects.get(id=request.session['emp_id'])
    sal = Salary.objects.get(employee=emp)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Payslip.pdf"'

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    title = styles["Heading1"]
    title.alignment = TA_CENTER
    title.textColor = HexColor("#0d6efd")

    elements = []

    elements.append(Paragraph("<b>EMPLOYEE MANAGEMENT SYSTEM</b>", title))
    elements.append(Paragraph("<b>MONTHLY PAYSLIP</b>", title))
    elements.append(Spacer(1,20))

    company = Table([
        ["Company", "ABC Technologies Pvt. Ltd."],
        ["Address", "Lucknow, Uttar Pradesh"],
        ["Date", str(date.today())],
        ["Status", "PAID"]
    ])

    company.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,-1),colors.lightblue),
        ("GRID",(0,0),(-1,-1),1,colors.black),
        ("BOTTOMPADDING",(0,0),(-1,-1),8)
    ]))

    elements.append(company)
    elements.append(Spacer(1,20))

    employee = Table([
        ["Employee Name", emp.name],
        ["Email", emp.email],
        ["Department", emp.department],
        ["Joining Date", str(emp.joindate)],
    ])

    employee.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,-1),colors.beige),
        ("GRID",(0,0),(-1,-1),1,colors.black)
    ]))

    elements.append(employee)
    elements.append(Spacer(1,20))

    salary = Table([
        ["Salary Head","Amount"],
        ["Basic Salary",f"₹ {sal.basic_salary}"],
        ["Bonus",f"₹ {sal.bonus}"],
        ["Deduction",f"₹ {sal.deduction}"],
        ["Net Salary",f"₹ {sal.total_salary}"],
    ])

    salary.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.darkblue),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("BACKGROUND",(0,4),(-1,4),colors.green),
        ("TEXTCOLOR",(0,4),(-1,4),colors.white),
        ("GRID",(0,0),(-1,-1),1,colors.black),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("BOTTOMPADDING",(0,0),(-1,-1),8)
    ]))

    elements.append(salary)
    elements.append(Spacer(1,25))

    footer = Paragraph(
        "<b>This is a computer generated payslip.</b><br/>"
        "No signature is required.<br/><br/>"
        "Employee Management System",
        styles["Normal"]
    )

    elements.append(footer)

    doc.build(elements)

    return response


def logout(request):
    request.session.flush()   # Session delete
    return redirect("employee_login")

def logout_admin(request):
    request.session.flush()   
    return redirect("admin_login")

















def leave_management(request):

    leaves = Leave.objects.all()

    return render(
        request,
        "leave_management.html",
        {
            "leaves": leaves
        }
    )


def add_leave(request):

    employees = Employee.objects.all()

    if request.method == "POST":

        employee_id = request.POST.get("employee")
        leave_type = request.POST.get("leave_type")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        reason = request.POST.get("reason")

        employee = get_object_or_404(
            Employee,
            id=employee_id
        )

        Leave.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status="Pending"
        )

        return redirect("view_leave")

    return render(
        request,
        "add_leave.html",
        {
            "employees": employees
        }
    )

def view_leave(request):

    leaves = Leave.objects.select_related("employee").all()

    query = request.GET.get("q", "").strip()

    if query:
        leaves = leaves.filter(
            Q(employee__name__icontains=query) |
            Q(leave_type__icontains=query) |
            Q(status__icontains=query) |
            Q(reason__icontains=query)
        )

    return render(
        request,
        "view_leave.html",
        {
            "leaves": leaves,
            "query": query
        }
    )

def edit_leave(request, id):

    leave = get_object_or_404(Leave, id=id)
    employees = Employee.objects.all()

    if request.method == "POST":

        leave.employee_id = request.POST.get("employee")
        leave.leave_type = request.POST.get("leave_type")
        leave.start_date = request.POST.get("start_date")
        leave.end_date = request.POST.get("end_date")
        leave.reason = request.POST.get("reason")
        leave.status = request.POST.get("status")

        leave.save()

        return redirect("view_leave")

    return render(
        request,
        "edit_leave.html",
        {
            "leave": leave,
            "employees": employees
        }
    )

def delete_leave(request, id):

    leave = get_object_or_404(
        Leave,
        id=id
    )

    if request.method == "POST":
        leave.delete()
        return redirect("view_leave")

    return render(
        request,
        "delete_leave.html",
        {
            "leave": leave
        }
    )

def approve_leave(request, id):

    leave = get_object_or_404(Leave, id=id)

    leave.status = "Approved"
    leave.save()

    return redirect("view_leave")


def reject_leave(request, id):

    leave = get_object_or_404(Leave, id=id)

    leave.status = "Rejected"
    leave.save()

    return redirect("view_leave")

def reports(request):

    context = {
        "total_employees": Employee.objects.count(),
        "total_departments": Department.objects.count(),
        "total_salary": Salary.objects.count(),
        "total_attendance": Attendance.objects.count(),
        "total_leaves": Leave.objects.count(),

        "present": Attendance.objects.filter(
            status="Present"
        ).count(),

        "absent": Attendance.objects.filter(
            status="Absent"
        ).count(),

        "half_day": Attendance.objects.filter(
            status="Half Day"
        ).count(),

        "pending_leaves": Leave.objects.filter(
            status="Pending"
        ).count(),

        "approved_leaves": Leave.objects.filter(
            status="Approved"
        ).count(),

        "rejected_leaves": Leave.objects.filter(
            status="Rejected"
        ).count(),
    }

    return render(
        request,
        "reports.html",
        context
    )

@login_required
def admin_profile(request):

    return render(
        request,
        "admin_profile.html"
    )


@login_required
def edit_admin_profile(request):

    if request.method == "POST":

        user = request.user

        user.first_name = request.POST.get("first_name", "").strip()
        user.last_name = request.POST.get("last_name", "").strip()
        user.email = request.POST.get("email", "").strip()

        user.save()

        messages.success(
            request,
            "Profile updated successfully."
        )

        return redirect("admin_profile")

    return render(
        request,
        "edit_admin_profile.html"
    )


@login_required
def change_admin_password(request):

    if request.method == "POST":

        form = PasswordChangeForm(
            request.user,
            request.POST
        )

        if form.is_valid():

            user = form.save()

            update_session_auth_hash(
                request,
                user
            )

            messages.success(
                request,
                "Password changed successfully."
            )

            return redirect("admin_profile")

    else:

        form = PasswordChangeForm(
            request.user
        )

    return render(
        request,
        "change_admin_password.html",
        {
            "form": form
        }
    )

@login_required
def admin_settings(request):

    if request.method == "POST":

        messages.success(
            request,
            "Settings saved successfully."
        )

        return redirect("admin_settings")

    return render(
        request,
        "admin_settings.html"
    )


@login_required
def admin_support(request):

    if request.method == "POST":

        SupportRequest.objects.create(
            user=request.user,
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            message=request.POST.get("message")
        )

        messages.success(
            request,
            "Your support request has been submitted successfully."
        )

        return redirect("admin_support")

    return render(
        request,
        "admin_support.html"
    )

@login_required
def support_requests(request):

    requests = SupportRequest.objects.all().order_by("-created_at")

    pending_count = SupportRequest.objects.filter(
        status="Pending"
    ).count()

    resolved_count = SupportRequest.objects.filter(
        status="Resolved"
    ).count()

    return render(
        request,
        "support_requests.html",
        {
            "requests": requests,
            "pending_count": pending_count,
            "resolved_count": resolved_count,
        }
    )
@login_required
def resolve_support(request, id):

    support = get_object_or_404(
        SupportRequest,
        id=id
    )

    support.status = "Resolved"
    support.save()

    messages.success(
        request,
        "Support request marked as resolved."
    )

    return redirect("support_requests")


@login_required
def delete_support(request, id):

    support = get_object_or_404(
        SupportRequest,
        id=id
    )

    support.delete()

    messages.success(
        request,
        "Support request deleted successfully."
    )

    return redirect("support_requests")

@login_required
def performance_management(request):

    performances = Performance.objects.select_related(
        "employee"
    ).order_by("-review_date")

    return render(
        request,
        "performance_management.html",
        {
            "performances": performances
        }
    )

@login_required
def add_performance(request):

    if request.method == "POST":

        employee_id = request.POST.get("employee")
        rating = request.POST.get("rating")
        review = request.POST.get("review")
        goals = request.POST.get("goals")

        employee = Employee.objects.get(id=employee_id)

        Performance.objects.create(
            employee=employee,
            rating=rating,
            review=review,
            goals=goals
        )

        return redirect("performance_management")

    employees = Employee.objects.all().order_by("name")

    return render(
        request,
        "add_performance.html",
        {
            "employees": employees
        }
    )

@login_required
def edit_performance(request, id):

    performance = get_object_or_404(
        Performance,
        id=id
    )

    if request.method == "POST":

        performance.rating = request.POST.get("rating")
        performance.review = request.POST.get("review")
        performance.goals = request.POST.get("goals")

        performance.save()

        return redirect("performance_management")

    return render(
        request,
        "add_performance.html",
        {
            "performance": performance,
            "employees": Employee.objects.all().order_by("name"),
            "edit_mode": True
        }
    )

@login_required
def delete_performance(request, id):

    performance = get_object_or_404(
        Performance,
        id=id
    )

    performance.delete()

    return redirect("performance_management")

def employee_attendance(request):
    emp_id = request.session.get("emp_id")

    if not emp_id:
        return redirect("employee_login")

    employee = Employee.objects.get(id=emp_id)

    attendance_records = Attendance.objects.filter(
        employee=employee
    ).order_by("-date")

    return render(
        request,
        "employee_attendance.html",
        {
            "employee": employee,
            "attendance_records": attendance_records
        }
    )

def employee_leave(request):

    emp_id = request.session.get("emp_id")

    if not emp_id:
        return redirect("employee_login")

    employee = Employee.objects.get(id=emp_id)

    leaves = Leave.objects.filter(
        employee=employee
    ).order_by("-applied_date")

    if request.method == "POST":

        leave_type = request.POST.get("leave_type")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        reason = request.POST.get("reason")

        Leave.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status="Pending"
        )

        return redirect("employee_leave")

    return render(
        request,
        "employee_leave.html",
        {
            "employee": employee,
            "leaves": leaves
        }
    )

def employee_documents(request):

    emp_id = request.session.get("emp_id")

    if not emp_id:
        return redirect("employee_login")

    employee = Employee.objects.get(id=emp_id)

    if request.method == "POST":

        document_type = request.POST.get("document_type")
        document_file = request.FILES.get("document")

        if document_file:
            Document.objects.create(
                employee=employee,
                document_type=document_type,
                document=document_file
            )

        return redirect("employee_documents")

    documents = Document.objects.filter(
        employee=employee
    ).order_by("-uploaded_at")

    return render(
        request,
        "employee_documents.html",
        {
            "employee": employee,
            "documents": documents
        }
    )

def employee_notifications(request):

    emp_id = request.session.get("emp_id")

    if not emp_id:
        return redirect("employee_login")

    employee = Employee.objects.get(id=emp_id)

    notifications = Notification.objects.filter(
        employee=employee
    ).order_by("-created_at")

    # Notifications ko read mark karna
    notifications.update(is_read=True)

    return render(
        request,
        "employee_notifications.html",
        {
            "employee": employee,
            "notifications": notifications
        }
    )




def employee_support(request):

    emp_id = request.session.get("emp_id")

    if not emp_id:
        return redirect("employee_login")

    employee = Employee.objects.get(id=emp_id)

    if request.method == "POST":

        message = request.POST.get("message")

        if message:
            SupportRequest.objects.create(
                user=None,
                name=employee.name,
                email=employee.email,
                message=message
            )

        return redirect("employee_support")

    requests = SupportRequest.objects.filter(
        email=employee.email
    ).order_by("-created_at")

    return render(
        request,
        "employee_support.html",
        {
            "employee": employee,
            "requests": requests
        }
    )


def admin_documents(request):

    documents = Document.objects.select_related(
        "employee"
    ).order_by("-uploaded_at")

    return render(
        request,
        "admin_documents.html",
        {
            "documents": documents
        }
    )


def admin_notifications(request):

    if request.method == "POST":

        employee_id = request.POST.get("employee")
        title = request.POST.get("title")
        message = request.POST.get("message")

        employee = Employee.objects.get(id=employee_id)

        Notification.objects.create(
            employee=employee,
            title=title,
            message=message
        )

        return redirect("admin_notifications")

    employees = Employee.objects.all().order_by("name")

    notifications = Notification.objects.select_related(
        "employee"
    ).order_by("-created_at")

    return render(
        request,
        "admin_notifications.html",
        {
            "employees": employees,
            "notifications": notifications
        }
    )

def employee_change_password(request):

    emp_id = request.session.get("emp_id")

    if not emp_id:
        return redirect("employee_login")

    employee = Employee.objects.get(id=emp_id)

    message = ""
    error = ""

    if request.method == "POST":

        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if current_password != employee.password:
            error = "Current password is incorrect."

        elif new_password != confirm_password:
            error = "New passwords do not match."

        elif len(new_password) < 6:
            error = "Password must be at least 6 characters."

        elif new_password == current_password:
            error = "New password must be different from current password."

        else:

            employee.password = new_password
            employee.save()

            message = "Password changed successfully."

    return render(
        request,
        "employee_change_password.html",
        {
            "employee": employee,
            "message": message,
            "error": error
        }
    )