# Dayflow HRMS — Database

## 1. Overview

The Dayflow database stores information required for employee management, authentication, attendance, leave management, and payroll.

**Database:** MySQL

## 2. Database Name

```text
dayflow_hrms
```

Create the database:

```sql
CREATE DATABASE dayflow_hrms;
```

Select it:

```sql
USE dayflow_hrms;
```

## 3. Main Tables

### Users

Stores login and role information.

```text
users
-------------------------
id
employee_id
email
password_hash
role
is_verified
created_at
```

### Employees

Stores employee profile and job information.

```text
employees
-------------------------
id
user_id
first_name
last_name
phone
address
department
designation
joining_date
profile_picture
```

### Attendance

Stores employee attendance.

```text
attendance
-------------------------
id
employee_id
date
check_in
check_out
status
```

Status values:

```text
Present
Absent
Half-day
Leave
```

### Leave Requests

Stores employee leave applications.

```text
leave_requests
-------------------------
id
employee_id
leave_type
start_date
end_date
remarks
status
admin_comment
created_at
```

Status values:

```text
Pending
Approved
Rejected
```

Leave types:

```text
Paid
Sick
Unpaid
```

### Payroll

Stores employee salary information.

```text
payroll
-------------------------
id
employee_id
basic_salary
allowances
deductions
net_salary
updated_at
```

## 4. Relationships

```text
Users
  │
  └── Employees
          │
          ├── Attendance
          │
          ├── Leave Requests
          │
          └── Payroll
```

### Relationship Summary

* One User can have one Employee profile.
* One Employee can have many Attendance records.
* One Employee can have many Leave Requests.
* One Employee can have one or multiple Payroll records depending on payroll design.

## 5. Data Integrity

The database should use:

* Primary keys
* Foreign keys
* Unique constraints
* NOT NULL constraints
* Appropriate data types

Important unique fields:

```text
employee_id
email
```

## 6. Database Security

* Passwords must be hashed before storage.
* Database credentials must not be hardcoded.
* Use environment variables.
* Do not commit `.env` to GitHub.
* Restrict database permissions where possible.

## 7. Sample Database Setup

```sql
CREATE DATABASE dayflow_hrms;

USE dayflow_hrms;

SHOW TABLES;
```

The application can then create/manage tables through SQLAlchemy migrations or the selected database initialization method.

## 8. Backup

Regular database backups should be maintained during development and deployment.

Example MySQL backup:

```bash
mysqldump -u root -p dayflow_hrms > dayflow_backup.sql
```

Restore:

```bash
mysql -u root -p dayflow_hrms < dayflow_backup.sql
```

## 9. Future Enhancements

* Database migrations using Alembic
* Audit history
* Notification table
* Salary slip table
* Department table
* Designation table
* Employee document table
* Automated database backups
