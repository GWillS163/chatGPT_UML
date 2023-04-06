from flask import Flask, request, render_template

from interface import *

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    print("接收了初次进入请求")
    return render_template('index.html',
                           index=True)


@app.route('/chat', methods=['GET', 'POST'])
def run():
    if request.method == 'GET':
        print("接收了一个GET请求")
        return render_template('index.html')

    print("接收了一个POST请求")
    print(request.form)
    userText = request.form['message']
    print("请求内容：", userText)

    rawResponse, umlCode, umlText = askChatGPT(userText)
    imgAddress = getImage(umlCode)
    return render_template('index.html',
                           chat_text=userText,
                           umlIntro=umlText,
                           umlCode=umlCode,
                           )


@app.route('/demo', methods=['GET'])
def get_demo():
    print("Demo 界面")
    userText = "生成一个简单示例"
    mockResponse = "Mock AI的简短回复"
    umlText = "这是一个简单的示例，用于展示UML图的生成"
    umlCode = """```@startuml
Alice -> Bob: test
@enduml```"""
    return render_template('index.html',
                           chat_text=userText,
                           response=mockResponse,
                           umlCode=umlCode,
                           umlText=umlText,
                           image_data='static/history/png/testingUMLCode.png'
                           )


if __name__ == '__main__':
    app.run()
