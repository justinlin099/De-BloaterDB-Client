# Debloater DB Client
import os
import json
import subprocess
import UWPScanner
import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
import requests


__debugMode = True

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
    tag=releaseTags[0]
    fileName="BloatDB.json"
    downloadPath = "https://github.com/"+repoName+"/releases/download/"+tag+"/"+fileName
    
    if __debugMode:
        print("正在下載最新的 Bloatware 定義檔...")
    
    bloatDB = requests.get(downloadPath)
    
    bloatDB.encoding = "utf8"
    bloatDB=bloatDB.json()
    return bloatDB
    
    

        
print(getBloatDB()[-1])
    
