from http.server import HTTPServer, BaseHTTPRequestHandler
import rsa
import json

(publicKey, privateKey) = rsa.newkeys(512)

decryptedKey = None

def setKey(key):
    global decryptedKey
    decryptedKey = key

def getKey():
    global decryptedKey
    return decryptedKey

class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        status = 200
        contentType = 'application/octet-stream'
        self.send_response(status)
        self.send_header('Content-type', contentType)
        self.end_headers()

        if(self.path == '/public-key'):
            print('Client requested public key')
            self.wfile.write(publicKey.save_pkcs1(format='DER'))

        if(self.path == '/symmetric-key'):
            print('Client requested symmetric key')
            self.wfile.write(getKey())
        return

    def do_POST(self):
        status = 200
        contentType = 'application/octet'
        print('Client sent encrypted symmetric key')
        contentLength = int(self.headers.get('Content-Length'))
        content = json.loads(self.rfile.read(contentLength).decode())

        keyLength = content['length']
        key = content['key']

        key = rsa.decrypt(key.to_bytes(keyLength, 'big'), privateKey)
        setKey(key)
        print(getKey())

        self.send_response(status)
        self.send_header('Content-type', contentType)
        self.end_headers()
        return


HOST_NAME = 'localhost'
PORT_NUMBER = 8080

print("Server running on port ", PORT_NUMBER )
httpServer = HTTPServer((HOST_NAME, PORT_NUMBER), Server)
try:
    httpServer.serve_forever()
except KeyboardInterrupt:
    pass

httpServer.server_close()
