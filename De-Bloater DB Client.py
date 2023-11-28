# Debloater DB Client
import base64
import os
import json
import subprocess
import UWPScanner
import tkinter as tk
from tkinter import filedialog
from PIL import Image,ImageTk
Image.CUBIC = Image.BICUBIC
import ttkbootstrap as ttk
import requests
import DBDBERes

VERSION = "v0.1.1-alpha"


with open("config.json", "r",encoding="utf8") as configFile:
    config=json.load(configFile)
    __debugMode = config["debugMode"]
    themeName = config["themeName"]
    tag = config["tag"]




#更新定義檔版本標籤
def updateTagLabel():
    tagLabel.config(text="Bloatware 定義檔版本："+tag)

# 取得 GitHub 上最新的 BloatDB.json
def getBloatDB():
    repoName="justinlin099/De-BloaterDB-Client"
    repoPath = "https://api.github.com/repos/"+repoName+"/releases"
    if __debugMode:
        print("正在取得最新的 Bloatware 定義檔...")
    
    
    
    # 取得最新的 Bloatware 定義檔版本
    web= requests.get(repoPath).json()
    releaseTags = [] 
    for release in web:
        releaseTags.append(release["tag_name"])
    if __debugMode:
        print("最新的 Bloatware 定義檔版本為："+releaseTags[0])
        
    # 下載最新的 BloatDB.json
    global tag
    tag=releaseTags[0]
    with open("config.json", "r",encoding="utf8") as configFile:
        config=json.load(configFile)
        config["tag"]=tag
    with open("config.json", "w",encoding="utf8") as configFile:
        json.dump(config, configFile, indent=4, ensure_ascii=False)
        
    updateTagLabel()
    fileName="BloatDB.json"
    downloadPath = "https://github.com/"+repoName+"/releases/download/"+tag+"/"+fileName
    
    if __debugMode:
        print("正在下載最新的 Bloatware 定義檔...")
    
    bloatDB = requests.get(downloadPath)
    
    bloatDB.encoding = "utf8"
    bloatDB=bloatDB.json()
    
    #儲存最新的 BloatDB.json
    with open(fileName, "w",encoding="utf8") as bloatDBFile:
        json.dump(bloatDB, bloatDBFile, indent=4, ensure_ascii=False)
        
    return bloatDB
    
root=ttk.Window(themename=themeName)
root.title("De-Bloater DB 預裝軟體移除器")
root.geometry("1280x1024")

def SaveLastClickPos(event):
    global lastClickX, lastClickY
    lastClickX = event.x
    lastClickY = event.y


def Dragging(event):
    x, y = event.x - lastClickX + root.winfo_x(), event.y - lastClickY + root.winfo_y()
    root.geometry("+%s+%s" % (x , y))

#remove titlebar
root.overrideredirect(True)

iconPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.icon))
iconPic = iconPic.subsample(20)



# 標題標籤外框
titleFrame = ttk.Frame(root, bootstyle="info")
titleFrame.pack(side="top", fill="x")

insideTitleFrame = ttk.Frame(titleFrame, bootstyle="info")
insideTitleFrame.pack(side="bottom", fill="x", padx=20, pady=20)



titleBar=ttk.Frame(titleFrame, bootstyle="info")
titleBar.pack(side="left", fill="x", padx=20, pady=20)
titleFrame.bind('<Button-1>', SaveLastClickPos)
titleFrame.bind('<B1-Motion>', Dragging)
titleBarButton=ttk.Frame(titleFrame, bootstyle="info")
titleBarButton.pack(side="right",  padx=20, pady=20)
# 標題標籤
titleIcon = ttk.Label(titleBar, image=iconPic, bootstyle="inverse-info")
titleIcon.grid(row=0, column=0, sticky="w", padx=10, pady=10)
subTitleLabel = ttk.Label(titleBar, text="預裝軟體移除器", font=("微軟正黑體", 10), bootstyle="inverse-info")
subTitleLabel.grid(row=0, column=1, sticky="w")


#關閉視窗按鈕
closeButton = ttk.Button(titleBarButton, text="✕", command=root.destroy, bootstyle="danger")
closeButton.grid(row=0, column=5, sticky="e",ipadx=20)
#最小化按鈕
minimizeButton = ttk.Button(titleBarButton, text="__", command=lambda: container.wm_state('iconic'), bootstyle="info")
minimizeButton.grid(row=0, column=4, sticky="e",ipadx=5)

mainFrame = ttk.Frame(root)
mainFrame.pack(fill="both", padx=20, pady=20, expand=True,side="bottom")

titleLabel = ttk.Label(insideTitleFrame, text="De-Bloater DB", font=("微軟正黑體", 25), bootstyle="inverse-info")
titleLabel.grid(row=2, column=0, sticky="w", padx=10)
versionLabel = ttk.Label(insideTitleFrame, text="軟體版本："+VERSION, font=("微軟正黑體", 10), bootstyle="inverse-info")
versionLabel.grid(row=3, column=0, sticky="w", padx=10)
tagLabel = ttk.Label(insideTitleFrame, text="Bloatware 定義檔版本："+tag, font=("微軟正黑體", 10), bootstyle="inverse-info")
tagLabel.grid(row=4, column=0, sticky="w", padx=10)



# 畫一個 Meter 在畫面正中央當掃描按鈕
meter = ttk.Meter(mainFrame)
meter.pack(side="top")

updateButton = ttk.Button(mainFrame, text="更新 Bloatware 定義檔", command=getBloatDB)
updateButton.pack(side="top", pady=20)


#檢查 BloatDB.json 是否存在
try:
    with open("BloatDB.json", "r",encoding="utf8") as bloatDBFile:
        bloatDB=json.load(bloatDBFile)
except:
    if __debugMode:
        print("BloatDB.json不存在")
    getBloatDB()
    with open("BloatDB.json", "r",encoding="utf8") as bloatDBFile:
        bloatDB=json.load(bloatDBFile)

root.mainloop()
    
