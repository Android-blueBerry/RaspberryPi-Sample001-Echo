# (라즈베리파이)에코 통신 예제

<img width="80%" src="./img/blueberry_title.png"/>

---

### 개요

1. 시리얼 포트 프로파일을 사용하는 블루투스 기기 간 통신 예제입니다.

   매우 기초적인 방법으로 블루투스 통신을 테스트 해볼 수 있습니다.

2. RFCOMM 서버 소켓을 생성해 클라이언트의 연결 요청을 대기합니다.

3. 데이터를 받으면 해당 데이터를 다시 클라이언트로 보냅니다(Echo)

​    

---

### 개발환경

+ Language <b>Python 3.8</b>
+ Library <b>PyBluez, subprocess</b>

​    

---

### 라즈베리파이 설정

* 이 예제는 Raspberry Pi OS 최신버전에서 테스트되었습니다.

​    

### PyBluez 모듈 설치

라즈베리파이에서 블루투스 통신을 위한 PyBluez 모듈을 설치하세요.

```
$ sudo apt-get install bluetooth libbluetooth-dev
$ python3 -m pip install pybluez
```

​    

### SDP 서버 활성화

'dbus-org.bluez.service' 파일의 내용을 아래와 같이 수정하세요.

ExecStart=/usr/libexec/bluetooth/bluetoothd <b>--compat</b>

```
$ sudo nano /etc/systemd/system/dbus-org.bluez.service
```

```c
...

[Service]
Type=dbus
BusName=org.bluez
ExecStart=/usr/libexec/bluetooth/bluetoothd --compat
NotifyAccess=main
#WatchdogSec=10
#Restart=on-failure
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
LimitNPROC=1
ProtectHome=true
ProtectSystem=full

[Install]
...
```

​    

그런 다음 라즈베리파이를 재부팅 해주세요.

```
$ sudo reboot
```

​    

### SDP 퍼미션 설정

sdp 퍼미션을 설정해 주세요.

```
$ sudo chmod 777 /var/run/sdp
```

​    

일회성이므로 라즈베리파이를 재부팅하면 재설정 해야 합니다.

라즈베리파이를 시작할 때마다 퍼미션을 자동으로 설정하려면 bashrc 파일을 열어 수정하세요.

```
$ sudo nano ~/.bashrc
```

맨 아랫줄에 <b>sudo chmod 777 /var/run/sdp</b>를 추가합니다.



---

### 페어링 요청 응답

* blueBerry 애플리케이션과 연결하기 전에 먼저 페어링이 되어 있어야 합니다.
* blueBerry 애플리케이션에서 페어링 요청을 보내고 라즈베리파이에서 응답합니다.

​    

라즈베리파이에서 <b>bluetoothctl</b>명령어를 입력하세요.

```
$ bluetoothctl
```

​    

기기 검색이 가능하도록 discoverable 설정과 페어링 요청을 수락하기 위한 기본 에이전트를 설정하세요.

```
$ power on
$ default-agent
$ pairable on
$ discoverable on
```

​    

이제 blueBerry에서 페어링 요청을 보내고 응답을 받을 수 있습니다.

```c
Request confirmation
[agent] Confirm passkey 999999 (yes/no): yes
```

​    

---

### 예제

* 파이썬으로 제작되었습니다.

​    

1. 필요한 모듈을 추가합니다.

```python
import bluetooth
import subprocess
```

​    

2. 서버 소켓을 생성-바인드-대기 상태로 만드세요.

```python
# subprocess는 파이썬에서 라즈베리파이의 쉘 명령을 실행할 수 있게 해주는 라이브러리입니다.
subprocess.call("sudo hciconfig hci0 piscan", shell=True) # advertise하기 전에 블루투스 검색을 노출시키세요.

HOST = ""  # 생략 또는 MAC address
PORT = bluetooth.PORT_ANY
UUID = "00001101-0000-1000-8000-00805F9B34FB" # Serial Port Profile의 UUID입니다.

server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

...
```

​    

3. 서버 소켓의 <b>accept()</b>를 사용하기 전에 서비스를 게시해야합니다.

   블루투스 시리얼 통신을 위해 <b>SERIAL_PORT_CLASS</b> 및 <b>SERIAL_PORT_PROFILE</b>을 설정하고 게시해 주세요.

```python
# advertise
name = "raspberrypi"
service_id = UUID
service_classes = [UUID, bluetooth.SERIAL_PORT_CLASS]
profiles = [bluetooth.SERIAL_PORT_PROFILE]

bluetooth.advertise_service(server_socket, name, service_id, service_classes, profiles)
print("advertising...")

# accept
client_socket, client_address = server_socket.accept()
print("accept! ", client_address)

...
```

​    

4. 연결되었다면 client_socket으로 메시지를 받고 다시 전달합니다.

```python
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
```

​    

---

### 오류 해결

1. <b>ModuleNotFoundError: No module named 'bluetooth'</b>

   PyBluez 모듈이 설치되지 않은 경우입니다. 라즈베리파이에서 [PyBluez 모듈](#pybluez-모듈-설치)을 설치해 주세요.



2. <b>bluetooth.btcommon.BluetoothError: [Errno 2] No such file or directory</b>

   [SDP 서버](#sdp-서버-활성화)가 활성화되지 않은 경우입니다.



3. <b>bluetooth.btcommon.BluetoothError: [Errno 13] Permission denied</b>

   [sdp 퍼미션](#sdp-퍼미션-설정)이 설정되지 않은 경우입니다.

