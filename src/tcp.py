import socket
import sys
import threading

sock = 0
work = True


def get_int32_from_bytes(data):
    res = int.from_bytes(data[0:4], 'big')
    data = data[4:]
    return data, res


def get_string(data):
    data, len = get_int32_from_bytes(data)
    str = data[0:len].decode('utf-8')
    data = data[len:]
    return data, str


def close_sock():
    sock.close()


def get_text(set_text):
    if len(sys.argv) < 2:
        print("Enter SOG-server ip-address as command line argument")
        exit(1)
    address = sys.argv[-1]
    print(address)

    while work:
        try:
            global sock
            sock = socket.socket()
            sock.connect((address, 8536))
            frame = bytearray()
            frame.append(100)
            frame.append(0)
            sock.send(frame)

            while work:
                data = sock.recv(16*1024)
                data, flag = get_int32_from_bytes(data)
                if flag == 1:
                    data, text = get_string(data)
                    data, title = get_string(data)
                    set_text(text, title)
                else:
                    print("Bad frame")
                    break
            close_sock()
        except:        
            print("connection error")
            try:
                close_sock()
            except:
                i = 0

thread = 0


def start_socket(par):
    thread = threading.Thread(target=get_text, args=(par.setup_text,))
    thread.start()


def stop_socket():
    global work
    work = False
    close_sock()
