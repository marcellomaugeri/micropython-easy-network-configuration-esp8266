import network
import ubinascii
import machine
import socket
import ujson
import utime

def activateAP():
    print('Activating access point...')
    accessPoint = network.WLAN(network.AP_IF)
    accessPoint.config( essid="ESP-"+ubinascii.hexlify(machine.unique_id()).decode('utf-8') , authmode=1)
    accessPoint.active(True)
    print('Done')
    return accessPoint

def doConnect(ssid, psw):
    wlan=network.WLAN(network.STA_IF)
    wlan.active(True)
    print('Connecting to network '+ssid+'...')
    wlan.connect(ssid, psw)
    for i in range(10):
        if not wlan.isconnected():
            print('Attempt '+str(i))
            utime.sleep(1)
        else:
            break
    if wlan.isconnected():
        print('Network config:', wlan.ifconfig())
        return True
    else:
        print('Not connected')
        return False
    
def receiveConfig(port):
    addr = socket.getaddrinfo("0.0.0.0", port)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    print("Listening on port:"+str(port))
    client, addr = s.accept()
    print('Client connected from', addr)
    newConfig=client.readline().decode('utf8')
    print('Received '+newConfig)
    newConfig=ujson.loads(newConfig)
    client.close()
    s.close()
    return newConfig

def config(port=33433):
    ap = activateAP()
    ok = False
    while True:
        newConfig = receiveConfig(port)
        if doConnect(newConfig["ssid"],newConfig["password"]):
            print('Valid config')
            ap.active(False)
            break