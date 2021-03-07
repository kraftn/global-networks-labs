class Divider:
    def __init__(self, text, codeword_length):
        self.codeword_length = codeword_length
        self.data = ''
        for letter in text:
            letter_code = bin(ord(letter))[2:]
            letter_code = (16 - len(letter_code)) * '0' + letter_code
            self.data += letter_code

        self.i_codeword = 0
        self.n_codewords = len(self.data) // codeword_length

        remainder = len(self.data) % codeword_length
        if remainder != 0:
            self.n_codewords += 1
            self.data += (codeword_length - remainder) * '0'

    def __iter__(self):
        return self

    def __next__(self):
        i = self.i_codeword
        if i < self.n_codewords:
            self.i_codeword += 1
            return self.data[i*self.codeword_length:(i+1)*self.codeword_length]
        else:
            raise StopIteration()


def merge(codewords):
    data = ''
    for codeword in codewords:
        data += codeword

    text = ''
    i_letter = 0
    letter_code = data[:16]
    while '1' in letter_code:
        text += chr(int(letter_code, base=2))
        i_letter += 1
        letter_code = data[16*i_letter:16*(i_letter+1)]
    return text
