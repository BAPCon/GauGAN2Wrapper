from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import base64
from datetime import date
import requests

awsurl = "http://ec2-54-184-13-84.us-west-2.compute.amazonaws.com:443"

def GetTemporaryID():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("http://gaugan.org/gaugan2/")
    time.sleep(1.5)
    termsCheck = driver.find_element(By.XPATH,"//button[@aria-label='Close Tour']")
    termsCheck.send_keys(Keys.ENTER)
    termsCheck = driver.find_element(By.ID, "myCheck")
    termsCheck.send_keys(Keys.SPACE)
    fileUpload = driver.find_element(By.ID, "render")
    fileUpload.send_keys(Keys.ENTER)
    time.sleep(4)
    all_requests = driver.requests
    print("total requests: ", len(all_requests))
    for req in all_requests:
        if req.url.count("infer") > 0:
            print(req.url)
            first_part = str(req.body[0:200].decode("ascii"))
            first_part = first_part.split("=")[1]
            first_part = first_part.split("%2C")[1]
            first_part = first_part.split("&")[0]
    driver.close()
    return first_part

def EncodeImageFromPath(imagePath):
    with open(imagePath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return "image/png;base64,"+ str(encoded_string)[2:-1]

def FormatID(guaganID):
    today = date.today()
    today = today.strftime("%m/%d/%Y")
    if today[0] == "0": today = today[1:]
    return today+","+guaganID

def Render(Payload, guaganID):
       
    DefaultParams = {
            'name':'',
            "style_name":"0",
            "caption":"",
            "enable_seg":"false",
            "enable_edge":"false",
            "enable_caption":"false",
            "enable_image":"false",
            "use_model2": "false",
            "masked_edgemap":"encodedImage",
            "masked_image":"encodedImage",
            "masked_segmap":"encodedImage"
        }
    
    
    setDefault = False
    maskCount = 0
    
    if Payload.get("masked_segmap") != None:
        DefaultParams['enable_seg'] = "true"
        DefaultParams['masked_segmap'] = EncodeImageFromPath(Payload.get("masked_segmap"))
        maskCount += 1
        if setDefault == False: setDefault = "masked_segmap"
        
    if Payload.get("masked_image") != None:
        DefaultParams['enable_image'] = "true"
        DefaultParams['masked_image'] = EncodeImageFromPath(Payload.get("masked_image")) 
        maskCount += 1
        if setDefault == False: setDefault = "masked_image"
    
    if Payload.get("masked_edgemap") != None:
        DefaultParams['enable_edge'] = "true"
        DefaultParams['masked_edgemap'] = EncodeImageFromPath(Payload.get("masked_edgemap")) 
        maskCount += 1
        if setDefault == False: setDefault = "masked_edgemap"
    
    if maskCount == 1:
        activeMask = DefaultParams[setDefault]
        DefaultParams['masked_edgemap'] = activeMask
        DefaultParams['masked_image'] = activeMask
        DefaultParams['masked_segmap'] = activeMask
        
    if Payload.get("caption") != None:
        DefaultParams['caption'] = Payload.get("caption")
        DefaultParams['enable_caption'] = "true"
    
    if Payload.get("style_name") != None:
        DefaultParams['style_name'] = Payload.get("style_name")
        
    DefaultParams['name'] = FormatID(guaganID)
    
    response = requests.request("POST", awsurl+"/gaugan2_infer", data=DefaultParams)
    try: 
        if str(response.text).count("true") > 0:
            print("Request successful")
            time.sleep(1)
            OutputWrite(guaganID)
        else:print("Request Failed")
    except:
        print("Request Failed")
    
def OutputWrite(guaganID):
    today = date.today()
    today = today.strftime("%m/%d/%Y")
    if today[0] == "0": today = today[1:]
    payload={'name': today+','+guaganID}
    response = requests.request("POST", awsurl+"/gaugan2_receive_output", data=payload)
    open('output.png', 'wb').write(response.content)

def OutputRaw(guaganID):
    today = date.today()
    today = today.strftime("%m/%d/%Y")
    if today[0] == "0": today = today[1:]
    payload={'name': today+','+guaganID}
    response = requests.request("POST", awsurl+"/gaugan2_receive_output", data=payload)
    return response.content
      
#Render({"masked_segmap":"aafa.png","caption":"sunny","style_name":"1","masked_edgemap":"sketch.png"},"1660505386639-409178534")
