import socket
from struct import pack

from hamming_code import hamming_decode, calc_number_parity_bits
from text_processing import merge

if __name__ == '__main__':
    MESSAGE_LENGTH = 58
    BLOCK_LENGTH = MESSAGE_LENGTH + calc_number_parity_bits(MESSAGE_LENGTH) + 1

    with socket.socket() as s:
        s.bind(('127.0.0.1', 65000))
        s.listen(1)
        connection, address = s.accept()
        with connection:
            messages = []
            log = [0, 0, 0]
            while True:
                message = connection.recv(BLOCK_LENGTH)
                if len(message) == 1:
                    break
                n_errors, message = hamming_decode(message.decode(),
                                                   MESSAGE_LENGTH)
                log[n_errors] += 1
                messages.append(''.join(map(str, message)))
            text = merge(messages)
            print('Полученный текст:')
            print(text)

            for info in log:
                connection.sendall(pack('I', info))
            connection.sendall(text.encode())
