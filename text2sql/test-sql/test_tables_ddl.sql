SELECT datname FROM pg_database;

CREATE DATABASE shop_db
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TEMPLATE = template0;

CREATE TABLE user_account (
    id          BIGSERIAL PRIMARY KEY,
    username    VARCHAR(50) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    email       VARCHAR(100),
    phone       VARCHAR(20),
    status      SMALLINT NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE user_account IS '用户表, 存储系统用户的基础信息';
COMMENT ON COLUMN user_account.id IS '用户主键ID';
COMMENT ON COLUMN user_account.username IS '登录用户名, 全局唯一';
COMMENT ON COLUMN user_account.password IS '用户登录密码(加密存储)';
COMMENT ON COLUMN user_account.email IS '用户邮箱';
COMMENT ON COLUMN user_account.phone IS '用户手机号';
COMMENT ON COLUMN user_account.status IS '用户状态: 1-正常, 0-禁用';
COMMENT ON COLUMN user_account.created_at IS '创建时间';
COMMENT ON COLUMN user_account.updated_at IS '更新时间';

CREATE TABLE role (
    id          BIGSERIAL PRIMARY KEY,
    role_code   VARCHAR(50) NOT NULL UNIQUE,
    role_name   VARCHAR(50) NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE role IS '角色表, 存储系统中的角色定义';
COMMENT ON COLUMN role.id IS '角色主键ID';
COMMENT ON COLUMN role.role_code IS '角色编码, 如 ADMIN, USER';
COMMENT ON COLUMN role.role_name IS '角色名称';
COMMENT ON COLUMN role.description IS '角色描述';
COMMENT ON COLUMN role.created_at IS '角色创建时间';


CREATE TABLE user_role (
    id       BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_user_role UNIQUE (user_id, role_id),
    CONSTRAINT fk_user_role_user FOREIGN KEY (user_id) REFERENCES user_account(id),
    CONSTRAINT fk_user_role_role FOREIGN KEY (role_id) REFERENCES role(id)
);
COMMENT ON TABLE user_role IS '用户与角色关联关系表, 多对多关系';
COMMENT ON COLUMN user_role.id IS '用户角色关系主键ID';
COMMENT ON COLUMN user_role.user_id IS '用户ID, 关联 user_account.id';
COMMENT ON COLUMN user_role.role_id IS '角色ID, 关联 role.id';
COMMENT ON COLUMN user_role.created_at IS '绑定时间';


CREATE TABLE orders (
    id           BIGSERIAL PRIMARY KEY,
    order_no     VARCHAR(64) NOT NULL UNIQUE,
    user_id      BIGINT NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL,
    status       SMALLINT NOT NULL DEFAULT 0,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    paid_at     TIMESTAMP,
    CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES user_account(id)
);
COMMENT ON TABLE orders IS '订单表, 存储用户下单信息';
COMMENT ON COLUMN orders.id IS '订单主键ID';
COMMENT ON COLUMN orders.order_no IS '订单编号, 业务唯一';
COMMENT ON COLUMN orders.user_id IS '下单用户ID, 关联 user_account.id';
COMMENT ON COLUMN orders.total_amount IS '订单总金额';
COMMENT ON COLUMN orders.status IS '订单状态: 0-未支付, 1-已支付, 2-已取消';
COMMENT ON COLUMN orders.created_at IS '下单时间';
COMMENT ON COLUMN orders.paid_at IS '支付时间';

-- 查看当前数据库的所有表
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- 查询表的列信息以及列的注释
SELECT
    c.column_name,
    c.data_type,
    d.description
FROM information_schema.columns c
LEFT JOIN pg_catalog.pg_statio_all_tables st
    ON c.table_schema = st.schemaname
   AND c.table_name = st.relname
LEFT JOIN pg_catalog.pg_description d
    ON d.objoid = st.relid
   AND d.objsubid = c.ordinal_position
WHERE c.table_name = 'user_account';