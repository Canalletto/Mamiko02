#!/usr/bin/env python3
import os
import zlib
import base64
import hashlib
import pwinput           # maskowanie * przy wpisywaniu hasła
from Crypto.Cipher import AES

# 0) Maskowane hasło
passphrase = pwinput.pwinput("Podaj frazę do szyfrowania: ", mask="*")

# 1) Wyprowadzenie 32-bajtowego klucza AES-256 z SHA-256(fraza)
key = hashlib.sha256(passphrase.encode("utf-8")).digest()
iv  = bytes(16)  # 16 bajtów zer jako IV

# 2) Zbieramy wszystkie .py w projekcie, pomijając katalog 'config/'
project_root = os.path.abspath(os.path.dirname(__file__))
excluded_dir = os.path.join(project_root, "config")

sources = []
for root, dirs, files in os.walk(project_root):
    if root.startswith(excluded_dir):
        continue
    for f in files:
        if not f.endswith(".py") or f == os.path.basename(__file__):
            continue
        path = os.path.join(root, f)
        with open(path, "r", encoding="utf-8") as rf:
            sources.append(rf.read())

all_code = "\n\n".join(sources).encode("utf-8")

# 3) Kompresja zlib
compressed = zlib.compress(all_code)

# 4) PKCS#7 padding do wielokrotności 16 bajtów
pad_len = 16 - (len(compressed) % 16)
padded  = compressed + bytes([pad_len]) * pad_len

# 5) Szyfrowanie AES-256-CBC
cipher    = AES.new(key, AES.MODE_CBC, iv)
encrypted = cipher.encrypt(padded)

# 6) Kodowanie Base64
payload = base64.b64encode(encrypted).decode("utf-8")

# 7) Zapis do pliku
outfile = os.path.join(project_root, "mamiko_payload.b64")
with open(outfile, "w", encoding="utf-8") as f:
    f.write(payload)

print(f"🔐 Payload zapisany w {outfile}. Zachowaj tę frazę, to Twój klucz!")

