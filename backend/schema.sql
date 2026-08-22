-- HRMS database schema
-- Run this in MySQL Workbench (or `mysql -u root -p < schema.sql`) after creating the target database.

CREATE DATABASE IF NOT EXISTS hrms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hrms_db;

-- ============ USERS ============
CREATE TABLE IF NOT EXISTS users (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  employee_id       VARCHAR(50) NOT NULL UNIQUE,
  email             VARCHAR(255) NOT NULL UNIQUE,
  password_hash     VARCHAR(255) NULL,
  role              ENUM('Employee', 'HR') NOT NULL DEFAULT 'Employee',
  full_name         VARCHAR(150) NOT NULL,
  address           VARCHAR(255) NULL,
  phone             VARCHAR(30) NULL,
  profile_picture   VARCHAR(500) NULL,
  job_title         VARCHAR(150) NULL,
  department        VARCHAR(150) NULL,
  is_verified       TINYINT(1) NOT NULL DEFAULT 0,
  verify_token      VARCHAR(255) NULL,
  auth_provider     ENUM('local', 'google') NOT NULL DEFAULT 'local',
  created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_users_role (role),
  INDEX idx_users_email (email)
) ENGINE=InnoDB;

-- ============ ATTENDANCE ============
CREATE TABLE IF NOT EXISTS attendance (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  user_id         INT NOT NULL,
  date            DATE NOT NULL,
  check_in_time   DATETIME NULL,
  check_out_time  DATETIME NULL,
  status          ENUM('Present', 'Absent', 'Half-day', 'Leave') NOT NULL DEFAULT 'Absent',
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_attendance_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE KEY uq_user_date (user_id, date),
  INDEX idx_attendance_date (date)
) ENGINE=InnoDB;

-- ============ LEAVE REQUESTS ============
CREATE TABLE IF NOT EXISTS leave_requests (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  user_id         INT NOT NULL,
  type            ENUM('Paid', 'Sick', 'Unpaid') NOT NULL,
  start_date      DATE NOT NULL,
  end_date        DATE NOT NULL,
  remarks         VARCHAR(500) NULL,
  status          ENUM('Pending', 'Approved', 'Rejected') NOT NULL DEFAULT 'Pending',
  admin_comment   VARCHAR(500) NULL,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_leave_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_leave_status (status),
  INDEX idx_leave_user (user_id)
) ENGINE=InnoDB;

-- ============ PAYROLL ============
CREATE TABLE IF NOT EXISTS payroll (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  user_id         INT NOT NULL UNIQUE,
  basic_salary    DECIMAL(12,2) NOT NULL DEFAULT 0,
  allowances      DECIMAL(12,2) NOT NULL DEFAULT 0,
  deductions      DECIMAL(12,2) NOT NULL DEFAULT 0,
  net_salary      DECIMAL(12,2) NOT NULL DEFAULT 0,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_payroll_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;
