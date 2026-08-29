-- ============================================================
-- 小滴智能OA办公审核AI系统 - 数据库初始化脚本
-- ============================================================

CREATE DATABASE IF NOT EXISTS oa_system
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE oa_system;

-- -----------------------------------------------------------
-- 1. 用户表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(64) NOT NULL UNIQUE COMMENT '用户名（登录账号）',
    password VARCHAR(256) NOT NULL COMMENT '密码（bcrypt加密存储）',
    name VARCHAR(64) NOT NULL COMMENT '姓名',
    role VARCHAR(32) NOT NULL COMMENT '角色（admin/manager/finance/hr/employee）',
    department VARCHAR(64) COMMENT '部门',
    position VARCHAR(64) COMMENT '职位',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------
-- 2. 请假申请表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS leave_applications (
    id VARCHAR(64) PRIMARY KEY COMMENT '申请编号（UUID）',
    employee_id VARCHAR(64) NOT NULL COMMENT '员工ID',
    employee_name VARCHAR(64) NOT NULL COMMENT '员工姓名',
    employee_role VARCHAR(32) NOT NULL,
    department VARCHAR(64),
    leave_type VARCHAR(32) NOT NULL COMMENT '请假类型（年假/病假/事假/婚假/产假/丧假）',
    leave_days INT NOT NULL COMMENT '请假天数',
    start_date DATE NOT NULL COMMENT '开始日期',
    end_date DATE NOT NULL COMMENT '结束日期',
    reason TEXT COMMENT '请假原因',
    status VARCHAR(32) DEFAULT 'pending' COMMENT '状态（pending/approved/rejected/finished）',
    manager_approval VARCHAR(32) DEFAULT 'pending' COMMENT '主管审批',
    hr_approval VARCHAR(32) DEFAULT 'pending' COMMENT 'HR审批',
    comments TEXT COMMENT '审批意见',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_employee (employee_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------
-- 3. 预设账号（bcrypt hash of 'admin123'）
--    实际 hash: $2b$12$LJ3m4ys4GlInf0TSJ7q3KuOe7TJyhBbfSMHmMkWJ3RNZbAfvAwrei
-- -----------------------------------------------------------
INSERT INTO users (username, password, name, role, department, position) VALUES
('admin',        '$2b$12$LJ3m4ys4GlInf0TSJ7q3KuOe7TJyhBbfSMHmMkWJ3RNZbAfvAwrei', '系统管理员', 'admin',     '管理部', '系统管理员'),
('manager_zhang','$2b$12$LJ3m4ys4GlInf0TSJ7q3KuOe7TJyhBbfSMHmMkWJ3RNZbAfvAwrei', '张主管',     'manager',   '技术部', '部门主管'),
('manager_li',   '$2b$12$LJ3m4ys4GlInf0TSJ7q3KuOe7TJyhBbfSMHmMkWJ3RNZbAfvAwrei', '李经理',     'manager',   '财务部', '部门经理'),
('finance_wang', '$2b$12$LJ3m4ys4GlInf0TSJ7q3KuOe7TJyhBbfSMHmMkWJ3RNZbAfvAwrei', '王财务',     'finance',   '财务部', '财务专员'),
('hr_liu',       '$2b$12$LJ3m4ys4GlInf0TSJ7q3KuOe7TJyhBbfSMHmMkWJ3RNZbAfvAwrei', '刘HR',       'hr',        '人事部', 'HR专员'),
('employee_zhao','$2b$12$LJ3m4ys4GlInf0TSJ7q3KuOe7TJyhBbfSMHmMkWJ3RNZbAfvAwrei', '赵工',       'employee',  '技术部', '高级工程师'),
('employee_qian','$2b$12$LJ3m4ys4GlInf0TSJ7q3KuOe7TJyhBbfSMHmMkWJ3RNZbAfvAwrei', '钱工',       'employee',  '技术部', '工程师')
ON DUPLICATE KEY UPDATE username=username;
