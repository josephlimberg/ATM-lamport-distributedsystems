import pymysql
import socket
import threading
import heapq

lock = threading.Lock()
request_queue = []
clients = {}
reloj_servidor = 0

# Conexión a la base de datos (Reemplazar con tus credenciales reales)
db = pymysql.connect(
    host="localhost",
    user="USUARIO_BD", 
    password="PASSWORD_BD",
    database="banco"
)
cursor = db.cursor()

def handle_client(conn, addr):
    global reloj_servidor
    client_id = conn.recv(1024).decode().strip()
    print(f"[+] {client_id} conectado desde {addr}")
    with lock:
        clients[client_id] = conn

    while True:
        try:
            data = conn.recv(1024).decode().strip()
            if not data:
                break

            cmd, ts = data.split(",")
            ts = int(ts)

            with lock:
                reloj_servidor = max(reloj_servidor, ts) + 1
                print(f"[{client_id}] Mensaje: {cmd} | Reloj Servidor actualizado a: {reloj_servidor}")

            if cmd == "REQUEST":
                with lock:
                    heapq.heappush(request_queue, (ts, client_id))
                    grant_access()
            elif cmd == "RELEASE":
                with lock:
                    remove_from_queue(client_id)
                    grant_access()
            elif cmd == "WITHDRAW":
                with lock:
                    cursor.execute("SELECT saldo FROM cuenta WHERE id = 1")
                    saldo = cursor.fetchone()[0]

                    reloj_servidor += 1 

                    if saldo >= 50:
                        saldo -= 50
                        cursor.execute("UPDATE cuenta SET saldo = %s WHERE id = 1", (saldo,))
                        db.commit()
                        msg = f"APROBADO,{reloj_servidor},${saldo}\n"
                    else:
                        msg = f"RECHAZADO,{reloj_servidor},${saldo}\n"
                    
                    conn.sendall(msg.encode())
        except Exception as e:
            print(f"[ERROR] {e}")
            break

    conn.close()

def remove_from_queue(client_id):
    global request_queue
    request_queue = [(ts, cid) for (ts, cid) in request_queue if cid != client_id]
    heapq.heapify(request_queue)

def grant_access():
    global reloj_servidor
    if not request_queue:
        return
    ts, client_id = request_queue[0]
    conn = clients.get(client_id)
    if conn:
        try:
            reloj_servidor += 1
            msg = f"GRANT,{reloj_servidor}\n"
            conn.sendall(msg.encode())
            print(f"[Servidor] Enviando GRANT a {client_id} (Reloj={reloj_servidor})")
        except:
            pass

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Escucha en todas las interfaces de red de la máquina virtual
    server.bind(("0.0.0.0", 7000))
    server.listen(5)
    print("[Servidor] Banco en línea esperando solicitudes...")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    main()