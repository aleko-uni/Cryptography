import sys

d = int(sys.argv[1])
n = int(sys.argv[2])
file_path = "C:\\Users\\aleksander.ozarowski\\Projects\\inf6sem\\Krypto\\zad2\\enc_msg.txt"

with open(file_path, 'r') as file:
    file_content = file.read().strip()

decrypted_msg = ""
for x in range(0, len(file_content), 8):
    c = file_content[x : x+8]
    m = pow(int(c), d, n)
    decrypted_msg += chr(m)

text_file = open("dec_msg.txt", "w")
text_file.write(decrypted_msg)
text_file.close()

