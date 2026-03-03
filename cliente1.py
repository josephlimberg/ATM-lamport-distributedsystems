import socket
import time

class CajeroPython:
    def __init__(self, id):
        self.id = id
        self.reloj_logico = 0
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Conexión al servidor (Reemplazar con la IP pública de tu VM)
        self.conn.connect(("IP_DEL_SERVIDOR", 7000)) 
        
        self.conn.sendall(f"{self.id}\n".encode())

    def solicitar_retiro(self):
        self.reloj_logico += 1
        self.conn.sendall(f"REQUEST,{self.reloj_logico}\n".encode())
        print(f"[{self.id}] solicita acceso (Reloj={self.reloj_logico})...")

        respuesta = self.conn.recv(1024).decode().strip()
        cmd, ts_server = respuesta.split(",")
        ts_server = int(ts_server)
        
        self.reloj_logico = max(self.reloj_logico, ts_server) + 1
        print(f"[{self.id}] Servidor dice: {cmd} | Reloj actualizado a: {self.reloj_logico}")

        if cmd == "GRANT":
            print(f"[{self.id}] accede al banco, retirando $50...")
            
            self.reloj_logico += 1
            self.conn.sendall(f"WITHDRAW,{self.reloj_logico}\n".encode())
            
            resultado_raw = self.conn.recv(1024).decode().strip()
            res_cmd, res_ts, res_saldo = resultado_raw.split(",")
            
            self.reloj_logico = max(self.reloj_logico, int(res_ts)) + 1
            print(f"[{self.id}] Resultado: {res_cmd} (Saldo: {res_saldo}) | Reloj: {self.reloj_logico}")
            
            time.sleep(2)
            
            self.reloj_logico += 1
            self.conn.sendall(f"RELEASE,{self.reloj_logico}\n".encode())

    def run(self):
        while True:
            input("\nPresiona ENTER para intentar retirar desde cajero Python...")
            self.solicitar_retiro()

cajero = CajeroPython("cajero_python")
cajero.run()