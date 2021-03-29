from ftp_client import FTPClient


def parse_input(text):
    words = text.split(' ')
    command = words[0]
    words.pop(0)
    return command, words


def main():
    client = None
    command = None
    while True:
        while client is None:
            command, args = parse_input(input('Необходимо подключиться к серверу\n'))
            if command == 'connect':
                active_mode = True if args[0] == 'active' else False
                client = FTPClient(active_mode, 1)
                if len(args) == 2:
                    code = client.connect(args[1])
                else:
                    code = client.connect(args[1], args[2], args[3])
                if code == 530:
                    print('Неверный логин или пароль!\n')
                    client = None
                elif code == 230:
                    print('Подключение выполнено успешно\n')
            elif command == 'close':
                return

        while command != 'quit':
            command, args = parse_input(input())
            if command == 'pwd':
                print(client.pwd())
            elif command == 'list':
                print(client.list())
            elif command == 'cwd':
                code = client.cwd(args[0])
                if code == 550:
                    print('Директории не существует')
                elif code == 250:
                    print('Переход выполнен успешно')
            elif command == 'download':
                code = client.download_file(args[0], args[1])
                if code == 550:
                    print('Нет прав на скачивание, или файл не существует')
                elif code == 226:
                    print('Файл скачан')
            elif command == 'upload':
                code = client.upload_file(args[0], args[1])
                if code == 550:
                    print('Нет прав на загрузку')
                elif code == 226:
                    print('Файл загружен')
            elif command == 'mkdir':
                code = client.create_folder(args[0])
                if code == 550:
                    print('Нет прав на создание директории, или директрия уже существует')
                elif code == 257:
                    print('Директория успешно создана')
            elif command == 'rmdir':
                code = client.remove_folder(args[0])
                if code == 550:
                    print('Нет прав на удаление директории, или директории не существует')
                elif code == 250:
                    print('Директория успешно удалена')
            elif command == 'delete':
                code = client.delete_file(args[0])
                if code == 550:
                    print('Нет прав на удаление файла, или файла не существует')
                elif code == 250:
                    print('Файл успешно удалён')
            elif command == 'quit':
                client.disconnect()
                client = None
            elif command == 'close':
                client.disconnect()
                return


if __name__ == '__main__':
    doc = """Подключиться - connect
Текущая директория - pwd
Список файлов и директорий - list
Сменить директорию - cwd
Скачать файл - download
Загрузить файл - upload
Создать директорию - mkdir
Удалить директорию - rmdir
Удалить файл - delete
Закрыть сессию - quit
Завершить работу - close
"""
    print(doc)
    main()
