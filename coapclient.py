import asyncio
from aiocoap import *
lamps_id = ['1a', '1b', '1c', '2a', '2b', '2c', '3a', '3b', '3c', '4a', '4b', '4c', '5a', '5b', '5c', 'Al']
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

async def coapsetlampstatus(url, value, lamp_id, data):
    if argparser_id(lamp_id) and argparser_value(data):
        print('coapsetlampstatus on', url, 'with value', value)
        protocol = await Context.create_client_context()
        request = Message(code=PUT, uri=url, payload=value)

        try:
            response = await protocol.request(request).response
        except Exception as e:
            print('Failed to fetch resource:', e)
        else:
            print('Result: %s'%(response.code))
    else:
        return "invalid data"        
async def main():
   #await coapsetlampstatus('coap://lamp1c.irst.be/lamp/dimming', b'10', '1c',)
   
   val = await coapgetlampstatus('coap://lamp1c.irst.be/lamp/dimming')
   print("retrieved lamp value:", val)


if __name__ == "__main__":
   asyncio.run(main())