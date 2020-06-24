#!/usr/bin/python3
#append-script for appending to a qfs client
#Quang Tran 06 24 20

import requests
import base64
import sys

client_ip = input("Input client ip or type \"r\" to reuse the last ip: ")

if client_ip == "r":
    try:
        with open("client_ip.log", "r") as f:
            client_ip = f.read()
    except:
        print("Error in retrieving past ip")

#client_ip check
try:
    r = requests.get("http://{}/".format(client_ip))
    if r.status_code != 200:
        raise
except:
    print("Invalid/Unavailable IP")
    sys.exit()

#record successful ip
with open("client_ip.log", "w") as f:
    f.write(client_ip)

append_path = input("Append file path: ")
content = input("Append string content: ")

#convert content to base64
b64content = base64.b64encode(content.encode()).decode()
append_json = {"file_path": append_path, "content": b64content}

#send request
r = requests.post("http://{}/append/".format(client_ip), json=append_json)

if r.status_code == 200:
    print("Append successful")
else:
    print("Append failed")
