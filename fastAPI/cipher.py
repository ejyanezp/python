import rsa
import base64

msg = 'Hola mundo RSA'
byte_array = bytearray(msg, encoding="utf-8")
public, private = rsa.newkeys(1024)
encrypted = rsa.encrypt(byte_array, public)
decrypted = rsa.decrypt(encrypted, private)
print(f"{encrypted},\n{decrypted.decode()}")
print(base64.b64encode(encrypted).decode())
print(public)
print(private)



