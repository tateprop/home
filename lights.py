
from multiprocessing import Pool
import time
import threading
import requests
import random
import string

TOKEN = 'a4bb4fa8-2510-4a2b-80e5-6c3c47badad5'
LOCATION_ID = "19b8c253-a92c-4727-8110-bb84808a6402"

class Lights:
    def __init__(self):
        self.headers = {"Authorization": f'Bearer {TOKEN}'}
        self.device_list = self.getDevices()
        self.sync = 1
        
    def getRequest(self, url):
        return requests.get(url, headers = self.headers).json()
        
    def postRequest(self, url, data):
        r = requests.post(url, json=data, headers=self.headers)
        return r.json()


    def getDevices(self):
        url = 'https://api.smartthings.com/v1/devices'
        devices = self.getRequest(url)
        devices_parsed = [[device["deviceId"], int(device["label"])] for device in devices["items"]]
        devices_sorted = sorted(devices_parsed,key=lambda l:l[1])
        ids = [device[0] for device in devices_sorted]
        return ids

    def formatData(self, hue, saturation, brightness):
        data = []
        if hue is not None:
            data.append({
                "component": "main",
                "capability": "colorControl",
                "command": "setColor",
                "arguments":[{
							"map": {
								"saturation": {
									"integer": saturation
								},
								"hue": {
									"integer": hue
								}
							}
                }]
                })
        if brightness is not None:
            data.append({
                "component": "main",
                "capability": "switchLevel",
                "command": "setLevel",
                "arguments": [{"integer": brightness}]
                })
        return data

    def createRule(self, data, devices):
        name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        completeData = {
            "name" : name,
            "actions" : [{
                "command" : {
                    "devices" : devices,
                    "commands" : data
                }
            }]
        }
        response = self.postRequest(f"https://api.smartthings.com/v1/rules?locationId={LOCATION_ID}", completeData)
        #print(response)
        id = response["id"]
        return id

    def executeTimedRule(self, *args):
        #better way!
        id, start, wait = args[0][0], args[0][1], args[0][2]
        now = time.time()
        if wait - (start-now) > 0:
            time.sleep(wait - (start-now))
        self.executeRule(id)

    def executeRule(self, id):
        self.postRequest(f"https://api.smartthings.com/v1/rules/execute/{id}?locationId={LOCATION_ID}", {})

    def purgeRules(self):
        r = self.getRequest(f"https://api.smartthings.com/v1/rules?locationId={LOCATION_ID}")
        ids = [x["id"] for x in r["items"]]
        for id in ids:
            requests.delete(f"https://api.smartthings.com/v1/rules/{id}?locationId={LOCATION_ID}", headers=self.headers)

    def runPattern(self, pattern, rules=None):
        print( pattern["loop"])
        if rules is None:
            ids = []
            for action in pattern["actions"]:
                hue = action["hue"] if "hue" in action else None
                saturation = action["saturation"] if "saturation" in action else 100
                brightness = action["brightness"] if "brightness" in action else None

                data = self.formatData(hue, saturation, brightness)
                devices = [self.device_list[light] for light in action["lights"]]
                id = self.createRule(data, devices)
                ids.append(id)
        else:
            ids = rules
        print("Created Rules")
        #testing 
        start = time.time() + 1
        args = [[ids[x], start, pattern["actions"][x]["time"]] for x in range(len(ids))]
        with Pool(len(ids)) as p:
            p.map(self.executeTimedRule, args)
        
        ##add True for infiite
        loops = pattern["loop"]
        if loops:
            pattern["loop"] = loops-1
            self.runPattern(pattern, rules=ids)
        else:
            self.purgeRules()
        

    
    def programLights(self, lights, hue=None, saturation=100, brightness=None):
        data = self.formatData(hue, saturation, brightness)
        devices = [self.device_list[light] for light in lights]
        id = self.createRule(data, devices)
        self.executeRule(id)
        
        


lights = Lights()
#lights.programLights([0,1], brightness=5, hue=0)
#lights.purgeRules()
pattern = {
    "actions" : [
        {"lights":[0,1,2], "brightness":20, "hue":0, "time":1},
        {"lights":[0,1,2], "brightness":0, "time":2},
        {"lights":[3,4], "brightness":20, "hue":20, "time":3},
        {"lights":[3,4], "brightness":0, "time":4},
        {"lights":[5,6], "brightness":20, "hue":40, "time":5},
        {"lights":[5,6], "brightness":0, "time":6},
        {"lights":[7,8], "brightness":20, "hue":60, "time":7},
        {"lights":[7,8], "brightness":0, "time":8},
        {"lights":[9,10], "brightness":20, "hue":80, "time":9},
        {"lights":[9,10], "brightness":0, "time":10},
        {"lights":[11,12], "brightness":20, "hue":90, "time":11},
        {"lights":[11,12], "brightness":0, "time":12},
    ],
    "loop" : 5
}

lights.runPattern(pattern)
#lights.purgeRules()
# while True:
#     for index, x in enumerate(lightsa):
#         hue = int(100/13*(index+1))
#         # threading.Thread(target=lights.programLights, args=(x,), kwargs={"brightness":20, "hue":hue}).start()

#         # threading.Thread(target=lights.programLights, args=(x,), kwargs={"brightness":0, "hue":hue}).start()
#         # time.sleep(interval)
#         lights.programLights(x, brightness=5, hue=hue)
#         lights.programLights(x, brightness=0,)
    
##you need to make a rule look into this