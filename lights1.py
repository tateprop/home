from multiprocessing import Pool
import time
import threading
import requests
import random
import string
import tinytuya
import json

PID = "yyi07qf1sfqnxwaa"
SPACE = "179494647"

class Lights:
    def __init__(self):
        self.c = tinytuya.Cloud(
                    apiRegion="eu", 
                    apiKey="y5xhr5ct9934cgynk9rp", 
                    apiSecret="f790c9ac148d458caa3fa7f2f19a195a", 
                    apiDeviceID="bf41c4b17042f0e49eqzfv")
        self.device_list = self.getDevices()
        
    def postRequest(self, url, data):
        print("Again...")
        print(data)
        r = self.c.cloudrequest(url, action="POST", post=data)
        print(f"Bing Bong... {r}")
        return r

    def getRequest(self, url, data={}):
        print(data)
        r = self.c.cloudrequest(url, query=data)
        print(r)
        return r

    def getDevices(self):
        f = open('tuya-raw.json')
        data = json.load(f)["result"]

        devices_parsed = [[x["id"], int(x["name"])] for x in data]
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

    def createRule(self, devices):
        name = ''.join(random.choice(string.digits) for _ in range(10))
        completeData = {
                        "space_id": SPACE,
                        "name": name,
                        "product_id": PID,
                        "device_ids": ",".join(devices)
                        }
        response = self.postRequest("/v2.0/cloud/thing/group", completeData)

    def executeTimedRule(self, *args):
        print(args)
        id, start, wait, data = args[0][0], args[0][1], args[0][2], args[0][3]
        now = time.time()
        if wait - (start-now) > 0:
            time.sleep(wait - (start-now))
        self.executeRule(data)

    def executeRule(self, data):
        print("sending....")
        self.postRequest("/v2.0/cloud/thing/group/properties", data)

    def getGroupIDs(self):
        data = {
                "space_id": SPACE,
                "page_no": 1,
                "page_size": 20
                }
        result = self.getRequest("/v2.0/cloud/thing/group", data)["result"]
        group_ids = [str(x["id"]) for x in result["data_list"]]
        return group_ids
    def purgeRules(self):
        for id in self.getGroupIDs():
            url = f"/v2.0/cloud/thing/group/{id}"
            a = self.c.cloudrequest(url, action="DELETE")
        print("Purged Groups")

    def runPattern(self, pattern, rules=None):
        print( pattern["loop"])
        # if rules is None:
        #     for action in pattern["actions"]:
        #         hue = action["hue"] if "hue" in action else None
        #         saturation = action["saturation"] if "saturation" in action else 100
        #         brightness = action["brightness"] if "brightness" in action else None

        #         #data = self.formatData(hue, saturation, brightness)
        #         devices = [self.device_list[light] for light in action["lights"]]
        #         self.createRule(devices)
        #     ids = self.getGroupIDs()
        # else:
        #     ids = rules
        ids = self.getGroupIDs()
        print("Created Rules")
        #testing 
        start = time.time() + 1
        data = [{"group_id" : int(ids[x]), "properties": '{"bright_value":100}'} for x in range(len(ids))]
        args = [[ids[x], start, pattern["actions"][x]["time"], json.dumps(data[x])] for x in range(len(ids))]
        # with Pool(len(ids)) as p:
        #     p.map(self.executeTimedRule, args)
        for arg in args:
            self.executeTimedRule(arg)
        print("moved")
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
# #lights.programLights([0,1], brightness=5, hue=0)
#lights.purgeRules()
#lights.getRequest("/v2.0/cloud/space/child")
lights.getRequest(f"/v2.0/cloud/thing/group/{lights.getGroupIDs()[0]}/properties")
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



####TODO
#MAKE IT WORK


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
