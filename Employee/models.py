from django.db import models
from django.contrib.auth.models import User


class Employee(models.Model):
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(unique=True, null=True)
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=30)
    department = models.CharField(max_length=100, null=True)
    joindate = models.DateField(null=True)
    phone = models.CharField(max_length=15, null=True)

    def __str__(self):
        return self.name

class Leave(models.Model):

    LEAVE_TYPES = [
        ("Casual Leave", "Casual Leave"),
        ("Sick Leave", "Sick Leave"),
        ("Earned Leave", "Earned Leave"),
        ("Emergency Leave", "Emergency Leave"),
        ("Other", "Other"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="leave_records"
    )

    leave_type = models.CharField(
        max_length=30,
        choices=LEAVE_TYPES
    )

    start_date = models.DateField()

    end_date = models.DateField()

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    applied_date = models.DateField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.employee.name} - {self.leave_type}"
    


class Salary(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="salary_records"
    )
    basic_salary = models.IntegerField()
    bonus = models.IntegerField(default=0)
    deduction = models.IntegerField(default=0)
    total_salary = models.IntegerField()

    def __str__(self):
        return self.employee.name

class Department(models.Model):
    department_name = models.CharField(max_length=100)
    department_code = models.CharField(max_length=20)
    department_head = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.department_name

class Attendance(models.Model):

    STATUS_CHOICES = [
        ("Present", "Present"),
        ("Absent", "Absent"),
        ("Half Day", "Half Day"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    remarks = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"{self.employee.name} - {self.date}"



    class AdminSettings(models.Model):
        user = models.OneToOneField(
            User,
            on_delete=models.CASCADE,
            related_name="admin_settings"
        )

    email_notifications = models.BooleanField(default=True)
    login_alerts = models.BooleanField(default=True)

    two_factor = models.BooleanField(default=False)
    secure_session = models.BooleanField(default=True)

    leave_notifications = models.BooleanField(default=True)
    attendance_alerts = models.BooleanField(default=True)

    theme = models.CharField(
        max_length=10,
        choices=[
            ("dark", "Dark"),
            ("light", "Light"),
        ],
        default="dark"
    )

    animations = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} Settings"


class SupportRequest(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)

    email = models.EmailField()

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Resolved", "Resolved"),
        ],
        default="Pending"
    )

    def __str__(self):
        return f"{self.name} - {self.status}"


class Performance(models.Model):

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="performances"
    )

    rating = models.PositiveIntegerField(default=0)

    review = models.TextField(
        blank=True,
        null=True
    )

    goals = models.TextField(
        blank=True,
        null=True
    )

    review_date = models.DateField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.employee.name} - {self.rating}/5"

class Document(models.Model):

    DOCUMENT_TYPES = [
        ("Aadhar Card", "Aadhar Card"),
        ("PAN Card", "PAN Card"),
        ("Resume", "Resume"),
        ("Joining Letter", "Joining Letter"),
        ("Experience Letter", "Experience Letter"),
        ("Other", "Other"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPES
    )

    document = models.FileField(
        upload_to="employee_documents/"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.employee.name} - {self.document_type}"

class Notification(models.Model):

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=200)

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - {self.title}"