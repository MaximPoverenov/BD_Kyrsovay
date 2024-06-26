import configparser
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_or_update_config(file_path):
    """
    Метод создает или обновляет конфигурацию доступа к базе данных
    """
    config = configparser.ConfigParser()
    print("Создание и настройка файла конфигурации доступа к базе данных.")
    if os.path.exists(file_path):
        user_choice = input(f"Файл конфигурации {file_path} уже существует. Хотите пересоздать его? (y - да): ")
        if user_choice.lower() != 'y':
            print("Используется текущий файл конфигурации.")
            return
        else:
            os.remove(file_path)

    dbname = input("Введите имя базы данных(по умолчанию, bd_hh): ")
    dbname = dbname if dbname else 'bd_hh'

    user = input("Введите имя пользователя(по умолчанию, postgres): ")
    user = user if user else 'postgres'

    password = input("Введите пароль(по умолчанию, 123456): ")
    password = password if password else '123456'

    host = input("Введите хост(по умолчанию, localhost): ")
    host = host if host else 'localhost'

    port = input("Введите порт(по умолчанию, 5432): ")
    port = port if port else '5432'

    config['postgresql'] = {
        'dbname': dbname,
        'user': user,
        'password': password,
        'host': host,
        'port': port
    }

    with open(file_path, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
        print(f"Файл конфигурации {file_path} успешно создан.")


def create_db(file_path):
    """
    Метод создает базу данных
    """
    config = configparser.ConfigParser()
    config.read(file_path, encoding='utf-8')
    dbname = config.get('postgresql', 'dbname')
    user = config.get('postgresql', 'user')
    password = config.get('postgresql', 'password')
    host = config.get('postgresql', 'host')
    port = config.get('postgresql', 'port')

    conn = psycopg2.connect(dbname="postgres", user=user, password=password, host=host, port=port)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Проверка, существует ли база данных
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
    exists = cur.fetchone()

    if exists:
        # Удаление базы данных, если она существует
        user_choice = input(f"База данных {dbname} уже существует. Хотите удалить её? (y - да): ")
        if user_choice.lower() == 'y':
            cur.execute(f"DROP DATABASE {dbname}")
            print(f"База данных {dbname} удалена.")
        else:
            print("Используется текущая база данных.")
            cur.close()
            conn.close()
            return

    # Создание новой базы данных
    cur.execute(f"CREATE DATABASE {dbname}")
    print(f"База данных {dbname} создана.")

    # Закрытие соединений
    cur.close()
    conn.close()


def draw_progress_bar(current: int, total: int, bar_length: int = 30):
    """
    Отображает прогресс загрузки.
    Пример использования: print(f'\rЗагружено: {draw_progress_bar(позиция, количество, end=''}')
    :param current: текущая позиция
    :param total: общее количество
    :param bar_length: длина бара
    :return: строка с прогрессом
    """
    progress = current / total
    num_ticks = int(bar_length * progress)
    bar = '[' + '#' * num_ticks + '_' * (bar_length - num_ticks) + ']'
    percentage = int(progress * 100)
    return f'{bar} {percentage}%'