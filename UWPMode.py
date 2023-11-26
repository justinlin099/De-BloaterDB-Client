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

UWPList = UWPScanner.ScanUWP()
with open("refDB.json", "r") as refFile:
    refList=json.load(refFile)
    
#比較 UWP 應用程式清單，找出refDB.json中沒有的應用程式
for uwpApp in UWPList["UWPApps"]:
    if uwpApp not in refList["UWPApps"]:
        print("新增應用程式：",uwpApp)
        
#選取要寫入DB的路徑
