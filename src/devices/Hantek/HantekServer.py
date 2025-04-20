import socket
import threading
from devices.Hantek6022API.PyHT6022.LibUsbScope import Oscilloscope


HOST = "0.0.0.0"  # Luistert op alle interfaces
PORT = 5025  # Standaard SCPI poort

def handle_client(conn, addr, scope):
    print(f"Verbonden met {addr}")
    conn.sendall(b"Hantek 6022BL SCPI Server\n")
    while True:
        try:
            data = conn.recv(1024).decode("utf-8").strip()
            if not data:
                break
            print(f"Ontvangen: {data}")
            
            if data == "*IDN?":
                conn.sendall(b"Hantek,6022BL,123456,1.0\n")
            elif data == "MEASURE?":
                wave_data = scope.capture()
                conn.sendall(f"{wave_data}\n".encode("utf-8"))
            elif data == "EXIT":
                conn.sendall(b"Bye\n")
                break
            else:
                conn.sendall(b"ERROR: Unknown command\n")
        except Exception as e:
            print(f"Fout: {e}")
            break
    conn.close()

def start_server():
    scope = Oscilloscope()
    scope.open()
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"SCPI Server luistert op {HOST}:{PORT}")
    
    while True:
        conn, addr = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr, scope))
        client_thread.start()

if __name__ == "__main__":
    start_server()
