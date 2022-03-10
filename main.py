import random


def generate_text_pairs(amount, key):
    pairs = []
    for i in range(amount):
        pairs.append(random.randint(0, 2**16-1))
        pairs[i] = pairs[i], encrypt(pairs[i], key)
    return pairs


def get_bit_at_position(number, position):
    number >>= position
    return number & 1


def generate_key_bytes(pairs):
    inverse_s_box = [0xe, 0x3, 0x4, 0x8, 0x1, 0xc, 0xa, 0xf, 0x7, 0xd, 0x9, 0x6, 0xb, 0x2, 0x0, 0x5]
    success_rate = [0] * 2**8
    for key1 in range(16):
        for key2 in range(16):
            for pair in pairs:
                v4_5_8 = key1 ^ ((pair[1] >> 8) & 0xf)
                v4_13_16 = key2 ^ (pair[1] & 0xf)

                u4_5_8 = inverse_s_box[v4_5_8]
                u4_13_16 = inverse_s_box[v4_13_16]

                x5 = get_bit_at_position(pair[0], 11)
                x7 = get_bit_at_position(pair[0], 9)
                x8 = get_bit_at_position(pair[0], 8)

                u4_6 = get_bit_at_position(u4_5_8, 2)
                u4_8 = get_bit_at_position(u4_5_8, 0)
                u4_14 = get_bit_at_position(u4_13_16, 2)
                u4_16 = get_bit_at_position(u4_13_16, 0)

                if x5 ^ x7 ^ x8 ^ u4_6 ^ u4_8 ^ u4_14 ^ u4_16 == 0:
                    key_value = (key1 << 4) ^ key2
                    success_rate[key_value] += 1
    success_rate = [abs(x - len(pairs)/2) for x in success_rate]
    return success_rate.index(max(success_rate))


def perm(number):
    tmp = 0
    if number > 0x7fff:
        tmp ^= 0x8000
        number -= 0x8000
    if number > 0x3fff:
        tmp ^= 0x0800
        number -= 0x4000
    if number > 0x1fff:
        tmp ^= 0x0080
        number -= 0x2000
    if number > 0x0fff:
        tmp ^= 0x0008
        number -= 0x1000
    if number > 0x07ff:
        tmp ^= 0x4000
        number -= 0x0800
    if number > 0x03ff:
        tmp ^= 0x0400
        number -= 0x0400
    if number > 0x01ff:
        tmp ^= 0x0040
        number -= 0x0200
    if number > 0x00ff:
        tmp ^= 0x0004
        number -= 0x0100
    if number > 0x007f:
        tmp ^= 0x2000
        number -= 0x0080
    if number > 0x003f:
        tmp ^= 0x0200
        number -= 0x0040
    if number > 0x001f:
        tmp ^= 0x0020
        number -= 0x0020
    if number > 0x000f:
        tmp ^= 0x0002
        number -= 0x0010
    if number > 0x0007:
        tmp ^= 0x1000
        number -= 0x0008
    if number > 0x0003:
        tmp ^= 0x0100
        number -= 0x0004
    if number > 0x0001:
        tmp ^= 0x0010
        number -= 0x0002
    if number > 0x0000:
        tmp ^= 0x0001
    return tmp


def sub(number, s_box):
    b = [0, 0, 0, 0]
    b[0], b[1] = divmod(number, 0x1000)
    b[1], b[2] = divmod(b[1], 0x100)
    b[2], b[3] = divmod(b[2], 0x10)
    number = 0
    mul = 0x1000
    for item in b:
        number += mul * s_box[item]
        mul //= 0x10
    return number


def encrypt(text, key):
    s_box = [0xe, 0x4, 0xd, 0x1, 0x2, 0xf, 0xb, 0x8, 0x3, 0xa, 0x6, 0xc, 0x5, 0x9, 0x0, 0x7]

    text = text ^ key
    text = sub(text, s_box)
    text = perm(text)

    text = text ^ key
    text = sub(text, s_box)
    text = perm(text)

    text = text ^ key
    text = sub(text, s_box)
    text = perm(text)

    text = text ^ key
    text = sub(text, s_box)
    text = text ^ key

    return text


def decrypt(text, key):
    inverse_s_box = [0xe, 0x3, 0x4, 0x8, 0x1, 0xc, 0xa, 0xf, 0x7, 0xd, 0x9, 0x6, 0xb, 0x2, 0x0, 0x5]

    text = text ^ key
    text = sub(text, inverse_s_box)
    text = text ^ key

    text = perm(text)
    text = sub(text, inverse_s_box)
    text = text ^ key

    text = perm(text)
    text = sub(text, inverse_s_box)
    text = text ^ key

    text = perm(text)
    text = sub(text, inverse_s_box)
    text = text ^ key

    return text


if __name__ == '__main__':
    for i in range(1):
        random.seed(i)
        key = random.randint(0, 2**16-1)
        pairs = generate_text_pairs(8000, key)
        print(f"key in bits {bin(key)}")
        print(f"part of the key we care about {bin(key % 0x10 ^ ((key % 0x1000) & 0xf00)>>4)}")
        print(f"calculated key {bin(generate_key_bytes(pairs))}")
