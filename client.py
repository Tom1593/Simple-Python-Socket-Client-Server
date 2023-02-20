import socket

def get_msg(socket, full_msg):
    del(full_msg)
    full_msg = ""
    while True:
        msg = socket.recv(8)
        full_msg += msg.decode("utf-8")
        if 'END' in msg.decode("utf-8") or len(msg) <= 0:
            break  
    if "exit" in full_msg:
        print(full_msg[:-7])
        return "exit" 
    return full_msg[:-4]
    

def send_msg(msg, socket):
    socket.send(bytes(msg,"utf-8"))

def main(): 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), 8888))
    print(f"connected to {socket.gethostname()}:8888")
    new_msg = ""
    msg = ""
    new_msg = get_msg(s, new_msg)
    while new_msg != 'exit':
        print(new_msg)
        msg = input("whats your replay?\n")
        send_msg(msg, s)
        new_msg = get_msg(s, new_msg)


if __name__ == "__main__":        
    main()