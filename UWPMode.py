#UWPMode.py
#架構：掃描 UWP 應用程式清單，比對 Windows 預設清單，產生 UWP 應用程式清單

#匯入模組
import os
import json
import subprocess
import UWPScanner
import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
global openPath

def writeBloatDB(writeList):
    #選取要寫入DB的路徑
    global openPath
    if openPath != "":
        with open(openPath, "w",encoding="utf8") as bloatDB:
            json.dump(writeList, bloatDB, indent=4, ensure_ascii=False)
            print("寫入DB完成")
    else:
        print("未選取路徑")
        openPath = filedialog.askopenfilename(title="選取要寫入DB的路徑",filetypes=[("JSON","*.json")])
        writeBloatDB()
        
def readBloatDB():
    #選取要讀取DB的路徑
    global openPath
    openPath = filedialog.askopenfilename(title="選取要讀取DB的路徑",filetypes=[("JSON","*.json")])
    if openPath != "":
        with open(openPath, "r",encoding="utf8") as bloatDB:
            writeList=json.load(bloatDB)
            return writeList
    else:
        print("未選取路徑")
        readBloatDB()

UWPList = UWPScanner.ScanUWP()
with open("refDB.json", "r",encoding="utf8") as refFile:
    refList=json.load(refFile)
    
writeList = readBloatDB()
#比較 UWP 應用程式清單，找出refDB.json中沒有的應用程式
for uwpApp in UWPList["UWPApps"]:
    if uwpApp not in refList["UWPApps"]:
        writeListCheck = False
        for writeListApp in writeList:
            if writeListApp["installPath"] == uwpApp:
                writeListCheck = True
        if writeListCheck == False:        
            addFlag = input("新增應用程式："+str(uwpApp)+"?(Y/N)")
            if(addFlag == "Y" or addFlag == "y"):
                # 格式:
                #     {
                #         "appName": "AudioDirector essential for MSI",
                #         "appShortName": "AudioDirector",
                #         "appDescription": "AudioDirector essential for MSI",
                #         "developerName": "CyberLink",
                #         "developerURL": "https://www.cyberlink.com/",
                #         "appType": "UWP",
                #         "installPath": "CyberLink.AudioDirectorforMSI",
                #         "uninstallPath": "CyberLink.AudioDirectorforMSI",
                #         "appPath": "CyberLink.AudioDirectorforMSI",
                #         "bloatRating": 3,
                #         "necessary": false,
                #         "bloatReason": "MSI 筆電內附的音樂剪輯軟體，但是是試用版，如果要使用完整功能的話需要付費購買。安裝在電腦上不會影響效能，但是會佔用空間。如果不需要可以進行移除。"
                #     },
                writeList.append({
                    "appName": input("輸入應用程式名稱："),
                    "appShortName": uwpApp,
                    "appDescription": "Unknown",
                    "developerName": UWPList["UWPApps"][uwpApp]["Publisher"],
                    "developerURL": "Unknown",
                    "appType": "UWP",
                    "installPath": uwpApp,
                    "uninstallPath": uwpApp,
                    "appPath": uwpApp,
                    "bloatRating": int(input("輸入應用程式評級：")),
                    "necessary": False,
                    "bloatReason": input("輸入理由：")
                })
        
#選取要寫入DB的路徑
writeBloatDB(writeList)