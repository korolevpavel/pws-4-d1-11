import requests
import sys

print("Введите Trello APP-KEY")
key = input()
print("Введите Trello TOKEN")
token = input()
print("Введите Board ID")
board_id = input()

auth_params = {
    'key': key,
    'token': token,
}

base_url = "https://api.trello.com/1/{}"

def read():

    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format(
        'boards') + '/' + board_id + '/lists', auth_params).json()

    # Вывод названий колонок и задач
    for column in column_data:

        task_data = requests.get(base_url.format(
            'lists') + '/' + column['id'] + '/cards', params=auth_params).json()

        print(column['name'] + ' [{}]'.format(len(task_data)))

        if not task_data:
            print('\t' + 'Нет задач!')
            continue
        for task in task_data:
            print('\t' + task['name'] + '\t' + task['id'])


def create(name, column_name):

    column_id = column_find(column_name)
    if column_id is None:
        column_id = create_column(column_name)['id']

        requests.post(base_url.format('cards'), data={
                      'name': name, 'idList': column_id, **auth_params})

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


def create_column(name):

    return requests.post(base_url.format('lists'), data={'name': name, 'idBoard': board_id, **auth_params}).json()


def move(name, column_name):

    duplicate_tasks = find_duplicates(name)  

    if len(duplicate_tasks) > 1:  
        print("Задач с таким названием несколько:")  
        for index, task in enumerate(duplicate_tasks):  
            task_column_name = requests.get(base_url.format('lists') + '/' + task['idList'], params=auth_params).json()['name']  
            print("Задача №{}\tid: {}\tНаходится в колонке: {}\t ".format(index, task['id'], task_column_name))  
        task_id = input("Пожалуйста, введите ID задачи, которую нужно переместить: ")  
    else:  
        task_id = duplicate_tasks[0]['id']

    # Теперь, когда у нас есть id задачи, которую мы хотим переместить
    # Определеим id колонки
    column_id = column_find(column_name)
    if column_id is None:
        column_id = create_column(column_name)['id']

    # И выполним запрос к API для перемещения задачи в нужную колонку
    requests.put(base_url.format('cards') + '/' + task_id +
                 '/idList', data={'value': column['id'], **auth_params})


def column_find(name):
    column_id = None
    column_data = requests.get(base_url.format(
        'boards') + '/' + board_id + '/lists', params=auth_params).json()
    for column in column_data:
        if column['name'] == name:
            column_id = column['id']

            return column_id


def find_duplicates(task_name):

    column_data = requests.get(base_url.format(
        'boards') + '/' + board_id + '/lists', params=auth_params).json()

    duplicate_tasks = []
    for column in column_data:
        column_tasks = requests.get(base_url.format(
            'lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in column_tasks:
            if task['name'] == task_name:
                duplicate_tasks.append(task)
    return duplicate_tasks


if __name__ == "__main__":

    if len(sys.argv) <= 2:
        read()
    elif sys.argv[1] == 'create':
        create(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'create_column':
        create_column(sys.argv[2])
    elif sys.argv[1] == 'move':
        move(sys.argv[2], sys.argv[3])
