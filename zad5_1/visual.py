#!"C:\Users\aleksander.ozarowski\Projects\inf6sem\Krypto\Scripts\python.exe"

import random
from PIL import Image


def gen_pixel():
    r = random.randint(0, 1)
    if r == 0:
        return [[0, 1], [0, 1]]
    else:
        return [[1, 0], [1, 0]]


def create_two_img_shares(arr):
    y_l = len(arr)
    x_l = len(arr[0])

    share1 = [[0] * (x_l * 2) for _ in range(y_l * 2)]
    share2 = [[0] * (x_l * 2) for _ in range(y_l * 2)]

    for y in range(y_l):
        for x in range(x_l):
            pattern = gen_pixel()
            for dy in range(2):
                for dx in range(2):
                    share1[2 * y + dy][2 * x + dx] = pattern[dy][dx]
                    if arr[y][x] == 1:
                        share2[2 * y + dy][2 * x + dx] = pattern[dy][dx]
                    else:
                        share2[2 * y + dy][2 * x + dx] = 1 - pattern[dy][dx]

    return share1, share2


def print_arr(arr):
    for row in arr:
        for v in row:
            print(" " if v == 1 else "#", end="")
        print()


def decrypt_with_two_shares(s1, s2):
    y_l = len(s1)
    x_l = len(s1[0])
    merged_arr = [[0] * x_l for _ in range(y_l)]
    for y in range(y_l):
        for x in range(x_l):
            merged_arr[y][x] = 0 if (s1[y][x] == 0 or s2[y][x] == 0) else 1
    return merged_arr


if __name__ == "__main__":
    img = Image.open("some_picture.png").convert("L")
    w, h = img.size
    threshold = 128

    img_arr = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            img_arr[y][x] = 1 if img.getpixel((x, y)) >= threshold else 0

    print("The original image")
    print_arr(img_arr)

    share1, share2 = create_two_img_shares(img_arr)

    print("\nShare 1")
    print_arr(share1)

    print("\nShare 2")
    print_arr(share2)

    merged = decrypt_with_two_shares(share1, share2)

    print("\nDecrypted (merged shares)")
    print_arr(merged)
