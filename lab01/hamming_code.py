import random


def calc_number_parity_bits(message_length):
    res = 1
    while 2**res < res + message_length + 1:
        res += 1
    return res


def calc_parity_bit(matrix_row, block):
    res = 0
    for x, y in zip(matrix_row, block):
        res += x * y
    return res % 2


def create_transformation_matrix(n_parity_bits, block_length):
    matrix = [[0 for j in range(block_length)] for i in range(n_parity_bits)]
    for i_column in range(block_length):
        str_number = bin(i_column + 1)[:1:-1]
        str_number += '0' * (n_parity_bits - len(str_number))
        number = list(map(int, str_number))
        for i_row in range(n_parity_bits):
            matrix[i_row][i_column] = number[i_row]
    return matrix


def hamming_encode(codeword: str):
    codeword = list(map(int, codeword))
    message_length = len(codeword)
    n_parity_bits = calc_number_parity_bits(message_length)
    block_length = n_parity_bits + message_length
    # Порядковые номера, начиная с 1
    parity_bits_positions = [2**i for i in range(n_parity_bits)]

    res = [0 for i in range(block_length)]
    i_copy = 0
    # Порядковые номера, начиная с 1
    for bit_pos in range(1, block_length+1):
        if bit_pos not in parity_bits_positions:
            res[bit_pos-1] = codeword[i_copy]
            i_copy += 1

    matrix = create_transformation_matrix(n_parity_bits, block_length)

    for i_parity_bit, parity_bit_pos in enumerate(parity_bits_positions):
        res[parity_bit_pos-1] = calc_parity_bit(matrix[i_parity_bit], res)

    # Последний бит для различия одиночных и двойных ошибок
    res.append(sum(res) % 2)
    return res


def hamming_decode(block: str, message_length):
    block = list(map(int, block))
    is_even_sum = sum(block) % 2 == 0
    block = block[:-1]

    block_length = len(block)
    n_parity_bits = block_length - message_length

    matrix = create_transformation_matrix(n_parity_bits, block_length)
    syndrome = [0 for i in range(n_parity_bits)]
    for i_parity_bit in range(n_parity_bits):
        syndrome[i_parity_bit] = calc_parity_bit(matrix[i_parity_bit], block)

    pos_to_correct = None
    n_errors = 0
    if 1 in syndrome:
        if not is_even_sum:
            n_errors = 1
            str_syndrome = ''.join(map(str, syndrome[::-1]))
            pos_to_correct = int(str_syndrome, base=2)
        else:
            n_errors = 2

    res = []
    parity_bits_positions = [2**i for i in range(n_parity_bits)]
    for bit_pos in range(1, block_length+1):
        if bit_pos not in parity_bits_positions:
            if bit_pos == pos_to_correct:
                res.append(1 - block[bit_pos-1])
            else:
                res.append(block[bit_pos-1])

    return n_errors, res


def generate_errors(block: list, n_errors):
    res = block[:-1]
    indexes = random.sample(range(len(res)), n_errors)
    for index in indexes:
        res[index] = 1 - res[index]
    res.append(block[-1])
    return res
