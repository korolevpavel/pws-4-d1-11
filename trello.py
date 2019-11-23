import requests
import sys

print("Введите Trello APP-KEY")
key = input()
print("Введите Trello TOKEN")
token = input()

auth_params = {
    'key': key,
    'token': token,
}

base_url = "https://api.trello.com/1/{}"

board_id = "aBWO5jvk"


def read():

    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format(
        'boards') + '/' + board_id + '/lists', auth_params).json()

    # Вывод названий колонк и задач
    for column in column_data:
        print(column['name'])
        task_data = requests.get(base_url.format(
            'lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        if not task_data:
            print('\t' + 'Нет задач!')
            continue
        for task in task_data:
            print('\t' + task['name'])


def create(name, column_name):

     # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format(
        'boards') + '/' + board_id + '/lists', auth_params).json()

    # Найдем перебором нужную колонку
    for column in column_data:
        if column['name'] == column_name:
            # Создадим задачу
            requests.post(base_url.format('cards'), data={
                          'name': name, 'idList': column['id'], **auth_params})
            break


def move(name, column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format(
        'boards') + '/' + board_id + '/lists', params=auth_params).json()

    # Среди всех колонок нужно найти задачу по имени и получить её id
    task_id = None
    for column in column_data:
        column_tasks = requests.get(base_url.format(
            'lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in column_tasks:
            if task['name'] == name:
                task_id = task['id']
                break
        if task_id:
            break

    # Теперь, когда у нас есть id задачи, которую мы хотим переместить
    # Переберём данные обо всех колонках, пока не найдём ту, в которую мы будем перемещать задачу
    for column in column_data:
        if column['name'] == column_name:
            # И выполним запрос к API для перемещения задачи в нужную колонку
            requests.put(base_url.format('cards') + '/' + task_id +
                         '/idList', data={'value': column['id'], **auth_params})
            break


if __name__ == "__main__":

    if len(sys.argv) <= 2:
        read()
    elif sys.argv[1] == 'create':
        create(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'move':
        move(sys.argv[2], sys.argv[3])
