# TCPClient.py

import socket
from constants import HOST, PORT, BUFFER_SIZE

if __name__ == '__main__':
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))

        # send username to the server
        print(s.recv(BUFFER_SIZE).decode('utf8'))
        username = input('Username: ')
        s.sendall(username.encode('utf8'))

        # print the server msg
        print(s.recv(BUFFER_SIZE).decode('utf8'))

        try:
            # connection established
            while True:
                req = input('>> ')
                if req:
                    s.sendall((f'{req}').encode('utf8'))
                    print(s.recv(BUFFER_SIZE).decode('utf8'))
                    
                    # terminate connection
                    if req.lower() == 'quit':
                        print(s.recv(BUFFER_SIZE).decode('utf8'))
                        break
        except KeyboardInterrupt:
            print('\n[!] Keyboard Interrupted!')
        except:
            print('Cannot connect to the server right now. Please retry in a bit.')
        finally:
            s.close()
            print('Client terminating...')
    except:
        print('Cannot connect to the server right now. Please retry in a bit.')
