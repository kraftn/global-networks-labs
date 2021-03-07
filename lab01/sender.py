import socket
import sys
import random
from struct import unpack

from text_processing import Divider
from hamming_code import hamming_encode, generate_errors

if __name__ == '__main__':
    MESSAGE_LENGTH = 58

    with socket.socket() as s:
        s.connect(('127.0.0.1', 65000))

        possible_n_errors = input('Введите возможные количества ошибок: ')
        possible_n_errors = list(map(int, possible_n_errors.split(', ')))

        text = ''
        print('Введите текст:')
        lines = sys.stdin.readlines()
        for line in lines:
            text += line

        log = [0, 0, 0]
        divider = Divider(text, MESSAGE_LENGTH)
        for text_part in divider:
            code = hamming_encode(text_part)
            n_errors = random.sample(possible_n_errors, 1)[0]
            log[n_errors] += 1
            data = generate_errors(code, n_errors)
            s.sendall(''.join(map(str, data)).encode())
        # Завершить передачу кодовых слов
        s.sendall(bytes(1))

        receiver_log = []
        for i_response in range(3):
            receiver_log.append(unpack('I', s.recv(4))[0])
        receiver_text = s.recv(8192).decode()

        print()
        if receiver_text == text:
            print('Тексты на передатчике и приёмнике совпадают')
        else:
            print('Тексты на передатчике и приёмнике не совпадают')
        print()

        print('Количество кодовых слов без ошибок')
        print('на передатчике:', log[0])
        print('на приёмнике:', receiver_log[0], end='\n\n')
        print('Количество кодовых слов с одиночной ошибкой')
        print('на передатчике:', log[1])
        print('на приёмнике:', receiver_log[1], end='\n\n')
        print('Количество кодовых слов с двойными ошибками')
        print('на передатчике:', log[2])
        print('на приёмнике:', receiver_log[2], end='\n\n')

        print('Ошибок исправлено:', receiver_log[1])
