from cryptography.fernet import Fernet

# Gera uma chave Fernet
key = Fernet.generate_key()

# Converte a chave em formato de string
key_str = key.decode()

print(key_str)
