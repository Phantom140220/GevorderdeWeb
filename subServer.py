from flask import Flask, jsonify, make_response, request
import asyncio
from aiocoap import *
import secrets
import json

secret_key = secrets.token_hex(16)
lamps_id = ['1a', '1b', '1c', '2a', '2b', '2c', '3a', '3b', '3c', '4a', '4b', '4c', '5a', '5b', '5c', 'Al']
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

@app.route("/getAll", methods=['GET'])
async def getAlllamps():
    if request.remote_addr != '127.0.0.1:5000':
        d= {}
        for lamps in lamps_id[:-1]:
            d.update({lamps : int(await coapgetlampstatus('coap://lamp'+lamps+'.irst.be/lamp/dimming'))})
        print(d)
        return json.dumps(d)
    else:
        return 403

def argparser_id(id):
    if id in lamps_id:
        return True
    else:
        return False

def argparser_value(value):
    if int(value['dimming']) < 101 and int(value['dimming']) > 0:
        return True
    else:
        return False

async def coapgetlampstatus(url):
    print('coapgetlampstatus on', url)
    protocol = await Context.create_client_context()
    request = Message(code=GET, uri=url)
    try:
        response = await protocol.request(request).response
    except Exception as e:
        print('Failed to fetch resource:', e)
    else:
        print('Result: %s\n%r'%(response.code, response.payload))
        return response.payload


if __name__ == "__main__":
   app.run(host="127.0.0.1", port=8080, debug=True)
