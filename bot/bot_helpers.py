from functools import wraps

# TODO: читать администраторов из json
LIST_OF_ADMINS = [12345678, 87654321, 511727477]

def restricted(func):
    """Запрет доступа к обработчику для не-администраторов"""
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        #if user_id not in LIST_OF_ADMINS:
        if not is_user_admin(user_id):
            print("Нет прав доступа для user_id {}.".format(user_id))
            return
        return func(update, context, *args, **kwargs)
    return wrapped


def is_user_admin(user_id: int):
    """Проверка: пользователь является администратором?"""
    print(user_id)
    if user_id in LIST_OF_ADMINS:
        return True
    return False
    
