import dataset
from passlib.hash import pbkdf2_sha256

# 连接到 SQLite 数据库
db = dataset.connect('sqlite:///rbac.db')

# 定义用户表模型
user_table = db['users']

# 定义角色表模型
role_table = db['roles']

# 定义权限表模型
permission_table = db['permissions']

# 定义用户角色关联表模型
user_role_table = db['user_role']

# 定义角色权限关联表模型
role_permission_table = db['role_permission']

def create_tables():
    # 检查表格是否已存在，如果不存在则创建
    if 'users' not in db.tables:
        user_table.create_column('username', db.types.string)
        user_table.create_column('password', db.types.string)

    if 'roles' not in db.tables:
        role_table.create_column('name', db.types.string)
        role_table.create_index(['name'], unique=True)

    if 'permissions' not in db.tables:
        permission_table.create_column('name', db.types.string)
        permission_table.create_index(['name'], unique=True)

    if 'user_role' not in db.tables:
        user_role_table.create_column('user_id', db.types.integer)
        user_role_table.create_column('role_id', db.types.integer)
        user_role_table.create_index(['user_id', 'role_id'], unique=True)

    if 'role_permission' not in db.tables:
        role_permission_table.create_column('role_id', db.types.integer)
        role_permission_table.create_column('permission_id', db.types.integer)
        role_permission_table.create_index(['role_id', 'permission_id'], unique=True)

# 其他代码保持不变
def create_user(username, password):
    # 创建用户
    hashed_password = pbkdf2_sha256.hash(password)
    return user_table.insert({'username': username, 'password': hashed_password})

def create_role(name):
    # 创建角色
    return role_table.insert({'name': name})

def create_permission(name):
    # 创建权限
    return permission_table.insert({'name': name})

def assign_role_to_user(user_id, role_id):
    # 分配角色给用户
    return user_role_table.insert({'user_id': user_id, 'role_id': role_id})

def assign_permission_to_role(role_id, permission_id):
    # 分配权限给角色
    return role_permission_table.insert({'role_id': role_id, 'permission_id': permission_id})

def authenticate_user(username, password):
    # 用户认证
    user = user_table.find_one(username=username)
    if user and pbkdf2_sha256.verify(password, user['password']):
        return user
    return None

def check_permission(user_id, permission_name):
    # 检查用户是否具有特定权限
    query = f"""
    SELECT COUNT(*) AS count
    FROM user_role
    JOIN role_permission ON user_role.role_id = role_permission.role_id
    JOIN permissions ON role_permission.permission_id = permissions.id
    WHERE user_role.user_id = :user_id AND permissions.name = :permission_name
    """
    result = db.query(query, {'user_id': user_id, 'permission_name': permission_name}).next()
    return result['count'] > 0

# 创建表格
create_tables()

# 创建用户、角色和权限
user_id = create_user('john_doe', 'password123')
admin_role_id = create_role('admin')
read_permission_id = create_permission('read')
write_permission_id = create_permission('write')

# 分配角色和权限
assign_role_to_user(user_id, admin_role_id)
assign_permission_to_role(admin_role_id, read_permission_id)
assign_permission_to_role(admin_role_id, write_permission_id)

# 进行用户认证
authenticated_user = authenticate_user('john_doe', 'password123')

if authenticated_user:
    print(f"User with ID '{authenticated_user['id']}' authenticated successfully.")
    # 检查用户权限
    if check_permission(authenticated_user['id'], 'read'):
        print("User has 'read' permission.")
    if check_permission(authenticated_user['id'], 'write'):
        print("User has 'write' permission.")
else:
    print("Authentication failed.")
