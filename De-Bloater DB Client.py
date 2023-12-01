# Debloater DB Client
# Version: v0.1.2-alpha
# 待修復問題:
# 2. 網路連線的例外處理
# 待新增功能：
# 1. 設定
# 2. 查看報表
# 3. 匯出報表
import base64
import os
import json
import subprocess
import threading
import time
import UWPScanner
import tkinter as tk
from tkinter import filedialog
from PIL import Image,ImageTk
Image.CUBIC = Image.BICUBIC
import ttkbootstrap as ttk
import requests
import DBDBERes
from ctypes import windll
from ttkbootstrap import utility,scrolled
debugMessage=""

VERSION = "v0.1.2-alpha"

def getThemeMode(themeName):
    if themeName=="cosmo" or themeName=="flatly" or themeName=="journal" or themeName=="litera" or themeName=="lumen" or themeName=="minty" or themeName=="pulse" or themeName=="sandstone" or themeName=="simplex"  or themeName=="united" or themeName=="yeti" or themeName=="morph" or themeName=="cerculean":
        return "b"
    else:
        return "w"

def loadConfig():
    try:
        with open("data/config.json", "r",encoding="utf8") as configFile:
            config=json.load(configFile)
            global __debugMode, themeName, tag
            __debugMode = config["debugMode"]
            themeName = config["themeName"]
            tag = config["tag"]
            return config
    except:# 例外處理新增 config.json
        try:
            os.mkdir("data")
        finally:
            with open("data/config.json", "w+",encoding="utf8") as configFile:
                config={"debugMode":False,"themeName":"cosmo","tag":"Unknown"}
                json.dump(config, configFile, indent=4, ensure_ascii=False)
            loadConfig()


#自訂視窗 Code
def set_appwindow():
    global hasstyle
    GWL_EXSTYLE=-20
    WS_EX_APPWINDOW=0x00040000
    WS_EX_TOOLWINDOW=0x00000080
    if not hasstyle:
        hwnd = windll.user32.GetParent(root.winfo_id())
        style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        root.withdraw()
        root.after(10, lambda:root.wm_deiconify())
        hasstyle=True

def quit():
    root.destroy()

def minimize(hide=False):
    hwnd = windll.user32.GetParent(root.winfo_id())
    windll.user32.ShowWindow(hwnd, 0 if hide else 6)

#取得電腦的硬體資訊(型號、CPU、RAM(GB/ddr type/雙通道)、硬碟、顯示卡、製造商)
def getHardwareInfo():
    global hardwareInfo
    hardwareInfo = {}
    #取得電腦的型號
    hardwareInfo["model"] = subprocess.check_output("wmic csproduct get name", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("utf-8").split("\n")[1].strip()
    #取得電腦的CPU
    hardwareInfo["cpu"] = subprocess.check_output("wmic cpu get name", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("utf-8").split("\n")[1].strip()
    #取得電腦的RAM總容量
    hardwareInfo["ram"] = UWPScanner.getMemory()
    #取得電腦的硬碟型號
    hardwareInfo["hdd"] = subprocess.check_output("wmic diskdrive get model", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("utf-8").split("\n")[1].strip()
    #取得電腦的顯示卡
    hardwareInfo["gpu"] = subprocess.check_output("wmic path win32_VideoController get name", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("utf-8").split("\n")[1].strip()
    #取得電腦的製造商
    hardwareInfo["manufacturer"] = subprocess.check_output("wmic computersystem get manufacturer", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("utf-8").split("\n")[1].strip()
    #取得顯示卡記憶體
    hardwareInfo["vram"] = subprocess.check_output("wmic path win32_VideoController get AdapterRAM", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("utf-8").split("\n")[1].strip()
    #取得電腦的BIOS
    hardwareInfo["bios"] = subprocess.check_output("wmic bios get name", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("utf-8").split("\n")[1].strip()
    #取得電腦的BIOS廠商
    hardwareInfo["biosManufacturer"] = subprocess.check_output("wmic bios get manufacturer", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("utf-8").split("\n")[1].strip()
    #取得核心數
    hardwareInfo["core"] = subprocess.check_output("wmic cpu get NumberOfCores", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("utf-8").split("\n")[1].strip()
    #取得線程數
    hardwareInfo["thread"] = subprocess.check_output("wmic cpu get NumberOfLogicalProcessors", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("utf-8").split("\n")[1].strip()
    #取得記憶體 Part Number (存成list)
    hardwareInfo["partNumber"] = subprocess.check_output("wmic memorychip get partnumber", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("utf-8").split("\r\r\n")[1:-2]
    #取得cpu頻率
    hardwareInfo["cpuSpeed"] = subprocess.check_output("wmic cpu get MaxClockSpeed", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("utf-8").split("\n")[1].strip()
    #記憶體序號
    hardwareInfo["serialNumber"] = subprocess.check_output("wmic memorychip get serialnumber", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("utf-8").split("\r\r\n")[1:-2]
    # 作業系統
    hardwareInfo["os"] = subprocess.check_output("wmic os get caption", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("big5").split("\n")[1].strip()
    # 安裝日期
    hardwareInfo["installDate"] = subprocess.check_output("wmic os get installdate", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("utf-8").split("\n")[1].strip()
    # 取得記憶體容量(存成list)
    hardwareInfo["memoryCapacity"] = subprocess.check_output("wmic memorychip get capacity", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("utf-8").split("\r\r\n")[1:-2]
    # 取得記憶體通道數
    hardwareInfo["memoryChannel"] = subprocess.check_output("wmic memorychip get memorytype", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("utf-8").split("\r\r\n")[1:-2]
    
    #更新電腦製造商Logo
    global manufacturerPic
    if getThemeMode(themeName)=="b":
        if hardwareInfo["manufacturer"]=="framework" or hardwareInfo["manufacturer"]=="Framework":
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_framework_b))
            manufacturerPicLabel.config(image=manufacturerPic)
        elif hardwareInfo["manufacturer"]=="Micro-Star International Co., Ltd." or hardwareInfo["manufacturer"]=="MSI" or hardwareInfo["manufacturer"]=="MSI " or hardwareInfo["manufacturer"]=="MSI Corporation" or hardwareInfo["manufacturer"]=="Micro-Star International Co., Ltd" or hardwareInfo["manufacturer"]=="Micro-Star International Co., Ltd ":
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_msi_b))
            manufacturerPicLabel.config(image=manufacturerPic)
    else:
        if hardwareInfo["manufacturer"]=="framework" or hardwareInfo["manufacturer"]=="Framework":
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_framework_w))
            manufacturerPicLabel.config(image=manufacturerPic)
        elif hardwareInfo["manufacturer"]=="Micro-Star International Co., Ltd." or hardwareInfo["manufacturer"]=="MSI" or hardwareInfo["manufacturer"]=="MSI " or hardwareInfo["manufacturer"]=="MSI Corporation" or hardwareInfo["manufacturer"]=="Micro-Star International Co., Ltd" or hardwareInfo["manufacturer"]=="Micro-Star International Co., Ltd ":
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_msi_w))
            manufacturerPicLabel.config(image=manufacturerPic)
    
    
    
    
    #更新電腦名稱標籤
    manufacturerLabel.config(text=hardwareInfo["manufacturer"])
    modelLabel.config(text=hardwareInfo["model"])
    #更新CPU標籤
    cpuLabel.config(text="中央處理器: "+hardwareInfo["cpu"]+" @ "+str(round(int(hardwareInfo["cpuSpeed"])/1000,1))+" GHz")
    coreLabel.config(text="處理器核心: "+hardwareInfo["core"]+" Cores/ "+hardwareInfo["thread"]+" Threads")
    memoryInfoText=""
    memoryIndex=1
    for memory in hardwareInfo["partNumber"]:
        memoryInfoText+="\n\t記憶體插槽"+str(memoryIndex)+": "+str(int(hardwareInfo["memoryCapacity"][memoryIndex-1])//(1024**3))+"GB " +memory+"SN:"+hardwareInfo["serialNumber"][memoryIndex-1]
        memoryIndex+=1
    ramLabel.config(text="系統記憶體: "+hardwareInfo["ram"]["String"]+memoryInfoText)
    
    gpuLabel.config(text="圖形處理器: "+hardwareInfo["gpu"]+" "+str(round(int(hardwareInfo["vram"])/(1024**3),1))+"GB")
    hardDiskLabel.config(text="硬碟存儲器: "+hardwareInfo["hdd"])
    osLabel.config(text="作業系統: "+hardwareInfo["os"])
    osInstallDateLabel.config(text="安裝日期: "+hardwareInfo["installDate"][0:4]+"年"+hardwareInfo["installDate"][4:6]+"月"+hardwareInfo["installDate"][6:8]+"日 "+hardwareInfo["installDate"][8:10]+":"+hardwareInfo["installDate"][10:12]+":"+hardwareInfo["installDate"][12:14])
    #bios標籤(含製造商及版本)
    biosLabel.config(text="BIOS: v"+hardwareInfo["bios"]+" ("+hardwareInfo["biosManufacturer"]+")")
    
    if __debugMode:
        print(hardwareInfo)
        global debugMessage
        debugMessage+="\n"+str(hardwareInfo)
        consoleText.config(text=debugMessage)
        
    return hardwareInfo

  
def scanBloatware():
    global bloatDB
    #meter.config(subtext="正在掃描...", textright="分")
    meter["amountused"]=100
    meter["subtext"]="正在掃描..."
    myUWPList = UWPScanner.ScanUWP()
    #scan UWP
    for app in bloatDB:
        global debugMessage
        if(app["installPath"] in myUWPList["UWPApps"]):
            if __debugMode:
                
                debugMessage+="\n找到預裝軟體："+app["appName"]
                consoleText.config(text=debugMessage)
                print("找到預裝軟體："+app["appName"])
                
            if app["developerName"]!="Microsoft" and app["developerName"]!="microsoft" and app["developerName"]!="Clipchamp":
                meter.step(app["bloatRating"])
                if __debugMode:
                    debugMessage+="\ndeduct "+str(app["bloatRating"])+" points from "+app["appName"]
                    consoleText.config(text=debugMessage)
                    print("\ndeduct "+str(app["bloatRating"])+" points from "+app["appName"])
                
            meter.update()
            time.sleep(0.1)
            
    
    meter["subtext"]="掃描完成!"
        
    
    #meter.config(subtext="掃描完成!", textright="分")

def some_function(x, y):
    time.sleep(10)
    
def scanbtn_function():
    x = 100
    y = 100
    
    boolean_wheel = threading.Thread(target=scanBloatware)
    boolean_wheel.start()
   
    # block button
    scanButton['state'] = 'disabled'
    reportButton['state'] = 'disabled'
    
    
    
    # start updating progressbar
    update_progressbar(boolean_wheel)  # send thread as parameter - so it doesn't need `global`
        
def update_progressbar(thread):
    
    if meter["amountused"]>=95:
        meter["bootstyle"]="success"
    elif meter["amountused"]>=70:
        meter["bootstyle"]="warning"
    elif meter["amountused"]<70:
        meter["bootstyle"]="danger"
   
    if thread.is_alive():
        # update progressbar
        scanProgressBar.start(10)
        # check again after 250ms (0.25s)
        root.after(250, update_progressbar, thread)
    else:
        # hide progressbar
        scanProgressBar.stop()
        # unblock button
        scanButton['state'] = 'normal'
        reportButton['state'] = 'normal'
        

#更新定義檔版本標籤
def updateTagLabel():
    tagLabel.config(text="Bloatware 定義檔版本："+tag)

# 取得 GitHub 上最新的 BloatDB.json
def getBloatDB():
    repoName="justinlin099/De-BloaterDB-Client"
    repoPath = "https://api.github.com/repos/"+repoName+"/releases"
    if __debugMode:
        global debugMessage
        debugMessage+="\n正在取得最新的 Bloatware 定義檔..."
        consoleText.config(text=debugMessage)
        print("正在取得最新的 Bloatware 定義檔...")
    progressLabel.config(text="正在取得最新的 Bloatware 定義檔...")
    startProgressbar["value"]=10
    startUpScreen.update()
    
    
    
    # 取得最新的 Bloatware 定義檔版本
    try:
        web= requests.get(repoPath).json()
    except:
        ttk.dialogs.dialogs.Messagebox.show_error("網路連線失敗，請檢查網路連線!", title='網路連線失敗', parent=startUpScreen, alert=True)
        startProgressbar["value"]=0
        startUpScreen.update()
        time.sleep(3)
        quit()
    releaseTags = [] 
    for release in web:
        releaseTags.append(release["tag_name"])
    if __debugMode:
        # global debugMessage
        debugMessage+="\n最新的 Bloatware 定義檔版本為："+releaseTags[0]
        consoleText.config(text=debugMessage)
        print("最新的 Bloatware 定義檔版本為："+releaseTags[0])
        
    progressLabel.config(text="最新的 Bloatware 定義檔版本為："+releaseTags[0])
    startProgressbar["value"]=30
    startUpScreen.update()
    time.sleep(1)
        
    # 下載最新的 BloatDB.json
    global tag
    tag=releaseTags[0]
    with open("data/config.json", "r",encoding="utf8") as configFile:
        config=json.load(configFile)
        if config["tag"]!=tag:
            config["tag"]=tag
            if __debugMode:
                # global debugMessage
                debugMessage+="\n找到新版本!"
                consoleText.config(text=debugMessage)
                print("找到新版本!")
            progressLabel.config(text="找到新版本!")
            #版本不同，下載最新的 BloatDB.json
            fileName="BloatDB.json"
            downloadPath = "https://github.com/"+repoName+"/releases/download/"+tag+"/"+fileName
            
            if __debugMode:
                # global debugMessage
                debugMessage+="\n正在下載最新的 Bloatware 定義檔..."
                consoleText.config(text=debugMessage)
                print("正在下載最新的 Bloatware 定義檔...")
            progressLabel.config(text="正在下載最新的 Bloatware 定義檔...")
            startProgressbar["value"]=50
            startUpScreen.update()
            
            global bloatDB
            
            bloatDB = requests.get(downloadPath)
            
            bloatDB.encoding = "utf8"
            
            
            bloatDB=bloatDB.json()
            
            #儲存最新的 BloatDB.json
            with open("data/"+fileName, "w+",encoding="utf8") as bloatDBFile:
                json.dump(bloatDB, bloatDBFile, indent=4, ensure_ascii=False)
                time.sleep(1)
        
        else:
            if __debugMode:
                # global debugMessage
                debugMessage+="\n已經是最新版本!"
                consoleText.config(text=debugMessage)
                print("已經是最新版本!")
            progressLabel.config(text="已經是最新版本!")
            startProgressbar["value"]=50
            startUpScreen.update()
            time.sleep(1)
            
            #讀取最新的 BloatDB.json
            with open("data/BloatDB.json", "r",encoding="utf8") as bloatDBFile:
                bloatDB=json.load(bloatDBFile)
        
        
                
        
    with open("data/config.json", "w",encoding="utf8") as configFile:
        json.dump(config, configFile, indent=4, ensure_ascii=False)
        
     
    updateTagLabel()
    
        
    #取得電腦的硬體資訊(型號、CPU、RAM、硬碟、顯示卡、製造商)
    progressLabel.config(text="正在取得電腦的硬體資訊...")
    startProgressbar["value"]=80
    startUpScreen.update()
    getHardwareInfo()
    
    
    progressLabel.config(text="完成!")
    startProgressbar["value"]=100
    startUpScreen.update()
    time.sleep(1)
        
    startUpScreen.withdraw()
    root.deiconify()
    root.attributes('-alpha', 1)
    

def createStartUpScreen(root):
    global startUpScreen, startProgressbar, progressLabel
    
    root.withdraw()
    
    # StartUp Screen
    startUpScreen = ttk.Toplevel(root, topmost=True)
    startUpScreen.title("De-Bloater DB 預裝軟體移除器")
    

    iconPicStart = ttk.PhotoImage(data=base64.b64decode(DBDBERes.icon))
    iconPicStart = iconPicStart.subsample(4)


    start_height = 450
    start_width = 600
    screen_width = startUpScreen.winfo_screenwidth()
    screen_height = startUpScreen.winfo_screenheight()
        # Coordinates of the upper left corner of the window to make the window appear in the center
    x_cordinate = int((screen_width/2) - (start_width/2))
    y_cordinate = int((screen_height/2) - (start_height/2))
    startUpScreen.geometry("{}x{}+{}+{}".format(start_width, start_height, x_cordinate, y_cordinate))
    startUpScreen.overrideredirect(True)
    startFrame = ttk.Frame(startUpScreen)
    startFrame.pack(fill="both", padx=30, pady=30, expand=True)
    labelFrame = ttk.Frame(startFrame)
    labelFrame.pack(fill="both", expand=True)
    
    startIcon = ttk.Label(labelFrame, image=iconPicStart)
    startIcon.grid(row=0, column=0, sticky="w", padx=10, pady=10)

    startTitleLabel = ttk.Label(labelFrame, text="De-Bloater DB", font=("微軟正黑體", 25))
    startTitleLabel.grid(row=1, column=0, sticky="w", padx=10)
    startSubTitleLabel=ttk.Label(labelFrame, text="預裝軟體移除器", font=("微軟正黑體", 10))
    startSubTitleLabel.grid(row=2, column=0, sticky="w", padx=10)
    startSubTitleLabel=ttk.Label(labelFrame, text="軟體版本："+VERSION, font=("微軟正黑體", 8), bootstyle="secondary")
    startSubTitleLabel.grid(row=3, column=0, sticky="w", padx=10)
    
    #progressLabel
    progressLabel = ttk.Label(startFrame, text="正在檢查 Bloatware 定義檔...", font=("微軟正黑體", 8), bootstyle="primary")
    progressLabel.pack(side="bottom",padx=10,fill="x")

    #progressbar
    startProgressbar = ttk.Progressbar(startFrame, orient="horizontal", mode="determinate", maximum=100, value=0)
    startProgressbar.pack(side="bottom",padx=10,fill="x")
    
    
    global bloatDB
    startUpScreen.after(500, lambda:getBloatDB())
    
    startUpScreen.mainloop()
    
    
    
def gotoHelp():
    #開啟瀏覽器至GitHub專案https://github.com/justinlin099/De-BloaterDB-Client/wiki
    import webbrowser    
    urL='https://github.com/justinlin099/De-BloaterDB-Client/wiki'
    webbrowser.get('windows-default').open_new(urL)
    
def gotoSettings():
    settingsScreen = ttk.Toplevel(root, topmost=True)
    
    settingsScreen.overrideredirect(True)
    settingsScreen.title("設定")
    window_height = 600
    window_width = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
        # Coordinates of the upper left corner of the window to make the window appear in the center
    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))
    settingsScreen.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
    settingsScreen.iconphoto(False, iconPic)


loadConfig()

# 主程式
root=ttk.Window(themename=themeName, alpha=0)




#remove titlebar
root.overrideredirect(True)


#設定縮放
utility.enable_high_dpi_awareness(root,2.25) 


root.title("De-Bloater DB 預裝軟體移除器")
#root.wm_attributes("-topmost", 1)
window_height = 1024
window_width = 1280
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
    # Coordinates of the upper left corner of the window to make the window appear in the center
x_cordinate = int((screen_width/2) - (window_width/2))
y_cordinate = int((screen_height/2) - (window_height/2))
root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

iconPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.icon))
#root.iconphoto(1, iconPic)
root.iconbitmap("icon.ico")
root.iconbitmap(default="icon.ico")
titleBarIcon = iconPic.subsample(20)


def SaveLastClickPos(event):
    global lastClickX, lastClickY
    lastClickX = event.x
    lastClickY = event.y

def Dragging(event):
    x, y = event.x - lastClickX + root.winfo_x(), event.y - lastClickY + root.winfo_y()
    root.geometry("+%s+%s" % (x , y))

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
titleIcon = ttk.Label(titleBar, image=titleBarIcon, bootstyle="inverse-info")
titleIcon.grid(row=0, column=0, sticky="w", padx=10, pady=10)
subTitleLabel = ttk.Label(titleBar, text="預裝軟體移除器", font=("微軟正黑體", 10), bootstyle="inverse-info")
subTitleLabel.grid(row=0, column=1, sticky="w")


#關閉視窗按鈕
closeButton = ttk.Button(titleBarButton, text="✕", command=quit, bootstyle="danger")
closeButton.grid(row=0, column=5, sticky="e",ipadx=20)
#最小化按鈕
minimizeButton = ttk.Button(titleBarButton, text="__", command=minimize, bootstyle="info")
minimizeButton.grid(row=0, column=4, sticky="e",ipadx=5)
#help按鈕
helpButton = ttk.Button(titleBarButton, text="?", command=gotoHelp, bootstyle="info")
helpButton.grid(row=0, column=3, sticky="e",ipadx=5)
#setting按鈕
settingButton = ttk.Button(titleBarButton, text="⚙", command=gotoSettings, bootstyle="info")
settingButton.grid(row=0, column=2, sticky="e",ipadx=5)

mainFrame = ttk.Frame(root)
mainFrame.pack(fill="both", padx=20, pady=20, expand=True,side="bottom")

titleLabel = ttk.Label(insideTitleFrame, text="De-Bloater DB", font=("微軟正黑體", 25), bootstyle="inverse-info")
titleLabel.grid(row=2, column=0, sticky="w", padx=10)
versionLabel = ttk.Label(insideTitleFrame, text="軟體版本："+VERSION, font=("微軟正黑體", 10), bootstyle="inverse-info")
versionLabel.grid(row=3, column=0, sticky="w", padx=10)
global tagLabel
tagLabel = ttk.Label(insideTitleFrame, text="Bloatware 定義檔版本："+tag, font=("微軟正黑體", 10), bootstyle="inverse-info")
tagLabel.grid(row=4, column=0, sticky="w", padx=10)


if __debugMode:
    Notebook = ttk.Notebook(mainFrame,bootstyle="info")
    Notebook.pack(side="left", padx=10, pady=10, fill="both", expand=True)
    hardwareInfoFrame = scrolled.ScrolledFrame(Notebook,autohide=True,width=700,padding=10)
    Notebook.add(hardwareInfoFrame.container, text="硬體資訊")
    #新增一個 scrolled text console 顯示除錯訊息
    consoleFrame = scrolled.ScrolledFrame(Notebook,autohide=True,width=700,padding=10)
    Notebook.add(consoleFrame.container, text="除錯訊息")
    
    
    consoleText=ttk.Label(consoleFrame,text=debugMessage, wraplength=700)
    consoleText.pack(side="top", fill="both", expand=True)
    
    
else:
    #hardwareinfo frame
    hardwareInfoOFrame = ttk.LabelFrame(mainFrame, text="硬體資訊", bootstyle="info")
    hardwareInfoOFrame.pack(side="left", padx=10, pady=10, fill="both", expand=True)
    hardwareInfoFrame = scrolled.ScrolledFrame(hardwareInfoOFrame,autohide=True,width=700,padding=10)
    hardwareInfoFrame.pack(side="top", fill="both", expand=True)    



   
manufacturerPicLabel = ttk.Label(hardwareInfoFrame)
manufacturerPicLabel.grid(column=0, row=0, padx=10, pady=10, sticky="w")
manufacturerLabel= ttk.Label(hardwareInfoFrame, text="我的電腦",font=("微軟正黑體", 25), wraplength=700)
manufacturerLabel.grid(column=0, row=1, padx=10, sticky="w")
modelLabel= ttk.Label(hardwareInfoFrame, text="我的電腦",font=("微軟正黑體", 15), wraplength=700)
modelLabel.grid(column=0, row=2, padx=10, sticky="w")
cpuLabel = ttk.Label(hardwareInfoFrame,text="CPU: Unknown", wraplength=700)
cpuLabel.grid(column=0, row=3, padx=10, pady=5, sticky="w")
coreLabel = ttk.Label(hardwareInfoFrame,text="CPU: Unknown", wraplength=700)
coreLabel.grid(column=0, row=4, padx=10, sticky="w")
ramLabel = ttk.Label(hardwareInfoFrame,text="RAM: Unknown", wraplength=700)
ramLabel.grid(column=0, row=5, padx=10, pady=5, sticky="w")
gpuLabel = ttk.Label(hardwareInfoFrame,text="GPU: Unknown", wraplength=700)
gpuLabel.grid(column=0, row=6, padx=10, pady=0, sticky="w")
hardDiskLabel = ttk.Label(hardwareInfoFrame,text="Hard Disk: Unknown", wraplength=700)
hardDiskLabel.grid(column=0, row=7, padx=10, pady=5, sticky="w")
osLabel = ttk.Label(hardwareInfoFrame,text="OS: Unknown", wraplength=700)
osLabel.grid(column=0, row=8, padx=10, pady=0, sticky="w")
osInstallDateLabel = ttk.Label(hardwareInfoFrame,text="OS Install Date: Unknown", wraplength=700)
osInstallDateLabel.grid(column=0, row=9, padx=10, pady=5, sticky="w")
biosLabel = ttk.Label(hardwareInfoFrame,text="BIOS: Unknown", wraplength=700)
biosLabel.grid(column=0, row=10, padx=10, pady=0, sticky="w")




meterFrame=ttk.Frame(mainFrame)
meterFrame.pack(side="left", fill="both", expand=True)
# # 畫一個 Meter 在畫面正中央當掃描按鈕

meter = ttk.Meter(meterFrame, amountused=100, subtext="尚未掃描", textright="分", bootstyle="warning",textfont=("微軟正黑體", 30),subtextfont=("微軟正黑體", 10))
meter.pack(side="top", pady=30, padx=30, fill="both", expand=True)

scanProgressBar = ttk.Progressbar(meterFrame, orient="horizontal", mode="indeterminate", maximum=100, value=0)
scanProgressBar.pack(side="bottom", padx=30, fill="x", expand=True)

scanButton=ttk.Button(meterFrame, text="掃描", command=scanbtn_function, bootstyle="success")
scanButton.pack(side="top", padx=30, pady=10, fill="both", expand=True)

#新增查看報表按鈕
reportButton=ttk.Button(meterFrame, text="查看報表", command=scanbtn_function, bootstyle="info")
reportButton.pack(side="top", padx=30, pady=10, fill="both", expand=True)
reportButton["state"] = "disabled"






#顯示硬體資訊


# updateButton = ttk.Button(hardwareInfoFrame, text="更新 Bloatware 定義檔", command=getBloatDB)
# updateButton.pack(side="left")

#自訂視窗 Code
hasstyle = False
root.update_idletasks()
root.withdraw()
set_appwindow()

#SetupScreen
createStartUpScreen(root)


root.mainloop()
    




    
