# -*- coding:utf-8 -*-
# Github: GWillS163
# User: 駿清清 
# Date: 4/6/2023 
# Time: 2:52 PM
import datetime
import os
import shutil
import subprocess

import keyring
import requests
import re

apiInterface = "https://api.openai-proxy.com/pro/chat/completions"
apiKey = keyring.get_password("openAI", "openAIKey")
sessionId = "978424b3-b07a-4462-ae6a-830bcf1b43a5"

plantUMLPath = "static/plantuml.jar"
encoding = "gbk"

demoCodePath = "static/demo/demoCode.txt"
demoPngPath = "static/demo/demoPng.png"

# showed
showedPath = 'static/'
showedPngName = "showedCode.png"
showedCodePath = showedPath + "showedCode.txt"
showedPngPath = showedPath + showedPngName

# history
codeSaveFolder = "static/history/code/"
pngSaveFolder = "static/history/png/"


def separate(responseData):
    # responseData = """'好的，以下是一个简单的UML活动图代码demo，符合plantUML的语法，可以在markdown文本中直接展示。\n\n```\n@startuml\nstart\nif (Have enough money?) then (yes)\n  -->[true] Buy Item\n  if (Item is expensive?) then (yes)\n    -->[true] Get Coupon\n  else (no)\n    -[dashed]->[no] End\n  endif\nelse (no)\n  ->[false] End\nendif\nstop\n@enduml\n```\n\n该UML活动图描述了一个简单的购物流程，用到的UML活动图元素有：\n\n- `start`：开始节点\n- `if`：条件节点\n- `true`/`false`：分支节点\n- `-->`：表示流程走向\n- `dashed`：表示虚线\n- `stop`：结束节点\n\n该UML活动图描述了购物流程，如果买东西的钱够，就购买商品，如果商品价格高，就可以得到优惠券，否则结束购物。这个流程可以帮助人们理解购物过程的流程和决策。\n\n以上是UML活动图的代码描述和解释，希望对您有所帮助。"""
    # get the uml code
    # umlCode start with ``` and end with ```, so we use re to get the code
    try:
        umlCode = re.findall(r'@startuml(.*)@enduml', responseData, re.S)[0]
        umlCode = """```\n@startuml\n""" + umlCode + """\n@enduml\n```"""
        # get the uml text, other sections are not uml code
        umlText = responseData.split(umlCode)[1].strip()
    except Exception as e:
        print("没有找到UML代码", e)
        umlCode = responseData
        umlText = ""

    print("umlCode:", umlCode)
    print("UMLIntro", umlText)
    return umlCode, umlText


# backend_api()
def askChatGPT(
        chat_text):
    defaultPrompt = "\n结合以上需求帮我写一个UML图代码demo，要符合plantUML的语法。 你的回答要包含_uml代码和uml代码描述。UML图内名称部分是中文,有关UML语法的关键词必须是英文：start,stop,if,else,-->,-[dashed]->,true,false。"
    # 调用后台接口获取回复
    reqData = {
        "apiKey": apiKey,
        "sessionId": "test",
        "content": chat_text + defaultPrompt
    }
    print("正在询问AI客服", chat_text)
    try:
        response = requests.post(apiInterface, json=reqData)
        print("response:", response)
        if response.status_code != 200:
            print("请求失败")
            return None, None, None
    except requests.RequestException as e:
        print("请求失败", e)
        return None, None, None

    rawResponse = response.json()
    print(rawResponse)
    responseText = rawResponse['data']
    umlCodePart, umlText = separate(responseText)

    return rawResponse, umlCodePart, umlText


# backend_api()
def getImage(umlCode):
    print("根据uml_text生成图片")

    # 1. save the code file
    with open(showedCodePath, "w", encoding=encoding) as f:
        f.write(umlCode)
    print("umlCode保存成功", showedCodePath)

    # 2. generate the png. use subprocess to run the command
    cmd = f"java  " \
          f"-Dfile.encoding=GBK  " \
          f"-Djava.awt.headless=true " \
          f"-Dsun.java2d.uiScale=1.0 " \
          f"-Dsun.java2d.dpiaware=false " \
          f"-Dsun.java2d.noddraw=true " \
          f"-jar {plantUMLPath} " \
          f"static/showedCode.txt"
    # f"-t png -o {showedPngName} " \
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    print(p)
    p.wait()
    print("图片生成成功", showedPngPath)

    # 3. back up the code and png to history folder
    # 3.1 get the current time
    now = datetime.datetime.now()
    nowStr = now.strftime("%Y-%m-%d-%H-%M-%S")
    # 3.2 save the code file
    codeSavePath = codeSaveFolder + nowStr + ".txt"
    pngSavePath = pngSaveFolder + nowStr + ".png"
    # if os.path.exists(showedCodePath):
    shutil.copyfile(showedCodePath, codeSavePath)
    # if os.path.exists(showedPngPath):
    shutil.copyfile(showedPngPath, pngSavePath)
    print("文件备份完成", codeSavePath, pngSavePath)

    return showedPngPath


if __name__ == '__main__':
    # askChatGPT()
    # separate(1)
    umlCode = """```
@startuml
title Login and Register Module

interface IUser {
  +register(username: string, password: string): boolean
  +login(username: string, password: string): boolean
  +logout(): void
  +getUser(): string
}

class UserImpl {
  +username: string
  +password: string
  +loggedIn: boolean
  +constructor(username: string, password: string)
  +register(username: string, password: string): boolean
  +login(username: string, password: string): boolean
  +logout(): void
  +getUser(): string
}

class LoginHelper {
  +loggedin: boolean
  +currentUser: string
  +login(username: string, password: string): boolean
  +logout(): void
  +promptRegister(): void
}

IUser <|.. UserImpl
LoginHelper --> IUser
@enduml
```
"""

    print(getImage(umlCode))
