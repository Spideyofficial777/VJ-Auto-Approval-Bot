
# database.py
users = []
groups = []

def add_user(user_id):
    users.append(user_id)

def add_group(group_id):
    groups.append(group_id)

def all_users():
    return len(users)

def all_groups():
    return len(groups)

def remove_user(user_id):
    users.remove(user_id)
