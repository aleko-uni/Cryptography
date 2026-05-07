import sys

e = int(sys.argv[1])
n = int(sys.argv[2])
file_path = "C:\\Users\\aleksander.ozarowski\\Projects\\inf6sem\\Krypto\\zad2\\msg.txt"

with open(file_path, 'r') as file:
    file_content = ''
    line = file.readline()

    while line:
        file_content += line
        line = file.readline()

encrypted_msg = ""
for char in file_content:
    c = pow(ord(char), e, n)
    encrypted_msg += str(c).zfill(8)

text_file = open("enc_msg.txt", "w")
text_file.write(encrypted_msg)
text_file.close()

