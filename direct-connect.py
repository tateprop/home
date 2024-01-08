import requests

##todo 
#1 - work out how to set color - DONE
#2 - work out instant chnage no smoothing _NOPE
#3 - new file OOP structure
#4 - add simultanious function with time checks



token = 'c4eafb11-cf60-4cc2-a85e-f8f489f6b798'
authorization = f'Bearer {token}'
headers = {"Authorization": authorization}
r = requests.get('https://api.smartthings.com/v1/devices', headers=headers)
# Export the data for use in future steps
#print(r.json()["items"][0])
ids = [x["deviceId"] for x in r.json()["items"]]


data = {
  "commands": [
    {
      "component": "main",
      "capability": "colorControl",
      "command": "setColor",
      "arguments": [{
        "hue": 70,
        "saturation":100,
      }]
    },
    {
      "component": "main",
      "capability": "switchLevel",
      "command": "setLevel",
      "arguments": [100]
    },
  ]
}

for id in ids:
    url = f"https://api.smartthings.com/v1/devices/{id}/commands"
    x = requests.post(url, json = data, headers=headers)

    print(x.text)



    # url = f"https://api.smartthings.com/v1/devices/{id}"
    # r = requests.get(url, headers=headers)
    # capabilities = [x["id"] for x in r.json()["components"][0]["capabilities"]]
    # for cap in capabilities:
    #     url = f"https://api.smartthings.com/v1/capabilities/{cap}"
    #     r = requests.get(url, headers=headers)
    #     print(f"{cap} : {r.json()}")
    
    # url = f"https://api.smartthings.com/v1/devices/{id}/status"
    # r = requests.get(url, headers=headers)
    # print("\n\n")
    # print(r.json())

    # typeIntegrationId = "eb9e8518-9ee6-3c79-99d6-52e169c4ef62"
    # url = f"https://api.smartthings.com/v1/presentation/types/{typeIntegrationId}/deviceconfig"
    # r = requests.get(url, headers=headers)
    # print("\n\n")
    # print(r.json())
