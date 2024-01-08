
from multiprocessing import Pool
import time
import threading
import grequests
import requests

TOKEN = 'c4eafb11-cf60-4cc2-a85e-f8f489f6b798'


class Lights:
    def __init__(self):
        self.headers = {"Authorization": f'Bearer {TOKEN}'}
        self.device_list = self.getDevices()
        self.sync = 0.01
        
    def getRequest(self, url):
        return requests.get(url, headers = self.headers).json()
        
    def postRequest(self, *args):
        args = args[0]
        num = self.device_list.index(args[0].split("/")[5])
        d = [x["arguments"] for x in args[1]["commands"]]
        print(f"Updated {num} with data {d} at {time.time()}")
        r = requests.post(args[0], json=args[1], headers=self.headers)


    def getDevices(self):
        url = 'https://api.smartthings.com/v1/devices'
        devices = self.getRequest(url)
        devices_parsed = [[device["deviceId"], int(device["label"])] for device in devices["items"]]
        devices_sorted = sorted(devices_parsed,key=lambda l:l[1])
        ids = [device[0] for device in devices_sorted]
        return ids

    def formatData(self, hue, saturation, brightness):
        
        data = {
            "commands": [
                {
                "component": "main",
                "capability": "colorControl",
                "command": "setColor",
                "arguments": [{
                    "hue": hue,
                    "saturation":saturation,
                }]
                },
                {
                "component": "main",
                "capability": "switchLevel",
                "command": "setLevel",
                "arguments": [brightness]
                },
            ]
        }
        if hue is None:
            data["commands"] = [data["commands"][1]]
        
        return data

    def programLights(self, lights, hue=None, saturation=100, brightness=None):
        startTime = time.time()
        data = self.formatData(hue, saturation, brightness)
        # for light in lights:
        #     url = f"https://api.smartthings.com/v1/devices/{self.device_list[light]}/commands"
        #     t1 = threading.Thread(target=self.postRequest, args=(url, data,))
        #     t1.start()
        # t1.join()
        # args = [[f"https://api.smartthings.com/v1/devices/{self.device_list[light]}/commands", data] for light in lights]
        # with Pool(len(lights)) as p:
        #     p.map(self.postRequest, args)

        urls = [f"https://api.smartthings.com/v1/devices/{self.device_list[light]}/commands" for light in lights]
        reqs = (grequests.post(u, json=data,headers=self.headers) for u in urls)
        grequests.map(reqs)

lightsa = [[0,1,2],[3,4],[5,6],[7,8],[9,10],[11,12]]
interval = 1

lights = Lights()
while True:
    for index, x in enumerate(lightsa):
        hue = int(100/13*(index+1))
        # threading.Thread(target=lights.programLights, args=(x,), kwargs={"brightness":20, "hue":hue}).start()

        # threading.Thread(target=lights.programLights, args=(x,), kwargs={"brightness":0, "hue":hue}).start()
        # time.sleep(interval)
        lights.programLights(x, brightness=5, hue=hue)
        lights.programLights(x, brightness=0,)
    
##you need to make a rule look into this