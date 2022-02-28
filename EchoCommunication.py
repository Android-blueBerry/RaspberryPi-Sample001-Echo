# v1.0(2022/01/11)

import bluetooth
import subprocess

subprocess.call("sudo hciconfig hci0 piscan", shell=True) # discoverable on

HOST = ""
PORT = bluetooth.PORT_ANY
UUID = "00001101-0000-1000-8000-00805F9B34FB"

server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

def advertise():
    # 서비스 클래스 및 프로파일 등록
    name = "raspberrypi"
    service_id = UUID
    service_classes = [UUID, bluetooth.SERIAL_PORT_CLASS]
    profiles = [bluetooth.SERIAL_PORT_PROFILE]

    bluetooth.advertise_service(server_socket, name, service_id, service_classes, profiles)
    print("advertising...")

    # accept
    client_socket, client_address = server_socket.accept()
    print("accept! ", client_address)

    return client_socket

def receive_echo(client_socket: bluetooth.BluetoothSocket):
    while True:
        try:
            data: str = client_socket.recv(1024).decode('utf-8')
            print("receive:", data)

            client_socket.send(data)
            print("echo:", data)

        except:
            print("receive error")
            client_socket.close()
            break

client_socket = advertise()
receive_echo(client_socket)