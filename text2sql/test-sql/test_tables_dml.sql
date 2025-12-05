INSERT INTO user_account (username, password, email, phone, status)
VALUES
('admin',  '$2a$10$adminpwdhash', 'admin@example.com', '13800000001', 1),
('alice',  '$2a$10$alicepwdhash', 'alice@example.com', '13800000002', 1),
('bob',    '$2a$10$bobpwdhash',   'bob@example.com',   '13800000003', 1),
('tom',    '$2a$10$tompwdhash',   'tom@example.com',   '13800000004', 0);

INSERT INTO role (role_code, role_name, description)
VALUES
('ADMIN', '系统管理员', '拥有系统全部管理权限'),
('USER',  '普通用户',   '普通业务操作权限'),
('FIN',   '财务人员',   '订单与账务管理权限');

INSERT INTO user_role (user_id, role_id)
VALUES
(1, 1),  -- admin -> ADMIN
(1, 3),  -- admin -> FIN
(2, 2),  -- alice -> USER
(3, 2),  -- bob   -> USER
(4, 2);  -- tom   -> USER (已禁用用户)


INSERT INTO orders (order_no, user_id, total_amount, status, paid_at)
VALUES
('ORD202501010001', 2, 199.00, 1, '2025-01-01 10:15:00'),
('ORD202501010002', 2, 89.50,  0, NULL),
('ORD202501010003', 3, 560.00, 1, '2025-01-02 14:30:00'),
('ORD202501010004', 3, 1200.00, 2, NULL),
('ORD202501010005', 1, 9999.00, 1, '2025-01-03 09:00:00');

