import json
from functools import wraps
from pathlib import Path

# TODO: читать администраторов из json
LIST_OF_ADMINS = [12345678, 87654321, 511727477]
DATA_FOLDER = 'data'


def restricted(func):
    """Запрет доступа к обработчику для не-администраторов"""

    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if not is_user_admin(user_id):
            print(f'Нет прав доступа для user_id {user_id}.')
            return
        return func(update, context, *args, **kwargs)

    return wrapped


def is_user_admin(user_id: int) -> bool:
    """Проверка: пользователь является администратором?"""
    print(user_id)
    if user_id in LIST_OF_ADMINS:
        return True
    return False


def read_json(filename: str):
    """Десереализовать JSON"""
    with open(Path.cwd() / Path(DATA_FOLDER) / filename,
              'r', encoding='utf8') as file_:
        file_json = file_.read()
    return json.loads(file_json)


def write_json(data, filename: str):
    """Сереализовать JSON"""
    with open(Path.cwd() / Path(DATA_FOLDER) / filename,
              'w', encoding='utf8') as file_:
        file_.write(json.dumps(data, indent=4, ensure_ascii=False))


def get_doc(filename: str):
    """Считать и вернуть бинарный файл"""
    with open(Path.cwd() / Path(DATA_FOLDER) / filename,
              'rb', encoding='utf8') as file_:
        doc = file_.read()
    return doc
