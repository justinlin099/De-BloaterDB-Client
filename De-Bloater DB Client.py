# Debloater DB Client
# Version: v0.3.0-beta
# 待新增功能：
# 3. 匯出報表
import base64
from pathlib import Path
import json
import subprocess
import threading
import time
import UWPScanner
from PIL import Image
Image.CUBIC = Image.BICUBIC
import ttkbootstrap as ttk
import requests
import DBDBERes
from ctypes import windll
from ttkbootstrap import scrolled
import reportGenerator
debugMessage=""
appTiles=[]

VERSION = "v0.3.0-beta"

class uwpAppTile():
    def __init__(self,appName,developerName,appDescription,appType,appPath,installPath,uninstallPath,appShortName,developerURL,bloatRating,necessary,bloatReason):
        self.appName=appName
        self.developerName=developerName
        self.appDescription=appDescription
        self.appType=appType
        self.appPath=appPath
        self.installPath=installPath
        self.uninstallPath=uninstallPath
        self.appShortName=appShortName
        self.developerURL=developerURL
        self.bloatRating=bloatRating
        self.necessary=necessary
        self.bloatReason=bloatReason
        
    def pack(self,root):
        if getThemeMode(themeName)=="b":
            frameStyle="light"
            style="inverse-light"
        else:
            frameStyle="dark"
            style="inverse-dark"
        tile=ttk.Frame(root,bootstyle=frameStyle)
        tile.pack(side="top",fill="x",padx=int(20*getZoomValue()//1.75),pady=int(10*getZoomValue()//1.75))
        if self.bloatRating>=5:
            bloatRatingColorLabel=ttk.Frame(tile,bootstyle="danger")
        elif self.bloatRating>=1:
            bloatRatingColorLabel=ttk.Frame(tile,bootstyle="warning")
        else:
            bloatRatingColorLabel=ttk.Frame(tile,bootstyle="success")
        bloatRatingColorLabel.pack(side="bottom",fill="x",expand=True,ipadx=int(10*getZoomValue()//1.75),ipady=int(10*getZoomValue()//1.75))
        titleFrame=ttk.Frame(tile,bootstyle=frameStyle)
        titleFrame.pack(side="top",fill="both",expand=True,padx=int(20*getZoomValue()//1.75),pady=int(10*getZoomValue()//1.75))
        tileTitle=ttk.Label(titleFrame,text=self.appName,font=("微軟正黑體", 12),bootstyle=style)
        tileTitle.grid(row=0,column=0,sticky="w")
        if self.appType=="UWP":
            subTitle = ttk.Label(titleFrame,text=self.installPath,font=("微軟正黑體", 8),bootstyle=style)
            subTitle.grid(row=1,column=0,sticky="w")
        else:
            subTitle = ttk.Label(titleFrame,text=self.uninstallPath,font=("微軟正黑體", 8),bootstyle=style)
            subTitle.grid(row=1,column=0,sticky="w")
        tileDescription=ttk.Label(tile,text=self.bloatReason,font=("微軟正黑體", 8),bootstyle=style, wraplength=int(900*getZoomValue()//1.75))
        tileDescription.pack(side="top",fill="both",expand=True,padx=int(20*getZoomValue()//1.75),pady=int(10*getZoomValue()//1.75))
        #bloatrating label
        if self.bloatRating>=5:
            bloatRatingLabel = ttk.Label(bloatRatingColorLabel,text=str(self.bloatRating)+" (強烈建議移除)",font=("微軟正黑體", 12),bootstyle="inverse-danger")
        elif self.bloatRating>=3:
            bloatRatingLabel = ttk.Label(bloatRatingColorLabel,text=str(self.bloatRating)+" (建議移除)",font=("微軟正黑體", 12),bootstyle="inverse-warning")   
        elif self.bloatRating>=1:
            bloatRatingLabel = ttk.Label(bloatRatingColorLabel,text=str(self.bloatRating)+" (不須使用可移除)",font=("微軟正黑體", 12),bootstyle="inverse-warning")
        else:
            bloatRatingLabel = ttk.Label(bloatRatingColorLabel,text=str(self.bloatRating)+" (不須移除)",font=("微軟正黑體", 12),bootstyle="inverse-success")
        bloatRatingLabel.pack(side="left",fill="both",expand=True,padx=int(20*getZoomValue()//1.75))
        #checkbutton
        self.tileCheckButton=ttk.Checkbutton(bloatRatingColorLabel, text="移除", variable=ttk.BooleanVar(), bootstyle="toolbutton-danger")
        self.tileCheckButton.pack(side="right",padx=int(20*getZoomValue()//1.75))
        #根據是否為必要軟體，決定是否勾選checkbutton
        if self.necessary:
            self.tileCheckButton.state(["!selected"])
        elif not self.necessary and self.bloatRating>=1:
            self.tileCheckButton.state(["selected"])
    
    def uninstall(self):
        # 取得按鈕狀態
        if self.tileCheckButton.instate(["selected"]):
            # 移除
            if self.appType=="UWP":
                subprocess.Popen(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe', 'Get-AppxPackage '+self.installPath+' | Remove-AppxPackage'], stdout=subprocess.PIPE, creationflags = subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen(self.uninstallPath, stdout=subprocess.PIPE, creationflags = subprocess.CREATE_NO_WINDOW)
        
            
            
            
def getThemeMode(themeName):
    if themeName=="cosmo" or themeName=="flatly" or themeName=="journal" or themeName=="litera" or themeName=="lumen" or themeName=="minty" or themeName=="pulse" or themeName=="sandstone" or themeName=="simplex"  or themeName=="united" or themeName=="yeti" or themeName=="morph" or themeName=="cerculean":
        return "b"
    else:
        return "w"

def loadConfig():
    configPath = Path('data/config.json')
    if configPath.exists():
        with open("data/config.json", "r",encoding="utf8") as configFile:
            config=json.load(configFile)
            global __debugMode, themeName, tag
            __debugMode = config["debugMode"]
            themeName = config["themeName"]
            tag = config["tag"]
            return config
    else:
        configPath.parent.mkdir(parents=True, exist_ok=True)
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
    hardwareInfo["gpu"] = subprocess.check_output("wmic path win32_VideoController get name", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("big5").split("\n")[1].strip()
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
    
    if __debugMode:
        print(hardwareInfo)
        global debugMessage
        debugMessage+="\n"+str(hardwareInfo)
        consoleText.config(text=debugMessage)
    
    
    #更新電腦製造商Logo
    global manufacturerPic
    if getThemeMode(themeName)=="b":
        #framework
        if hardwareInfo["manufacturer"]=="framework" or hardwareInfo["manufacturer"]=="Framework":
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_framework_b))
        #MSI
        elif hardwareInfo["manufacturer"]=="Micro-Star International Co., Ltd." or hardwareInfo["manufacturer"]=="MSI" or hardwareInfo["manufacturer"]=="MSI " or hardwareInfo["manufacturer"]=="MSI Corporation" or hardwareInfo["manufacturer"]=="Micro-Star International Co., Ltd" or hardwareInfo["manufacturer"]=="Micro-Star International Co., Ltd ":
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_msi_b))
        #ASUS
        elif hardwareInfo["manufacturer"]=="ASUSTeK COMPUTER INC." or hardwareInfo["manufacturer"]=="ASUSTeK COMPUTER INC" or hardwareInfo["manufacturer"]=="ASUSTeK COMPUTER INC " or hardwareInfo["manufacturer"]=="ASUSTeK COMPUTER INC. ":
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_asus_b))
        #HP
        elif hardwareInfo["manufacturer"]=="HP" or hardwareInfo["manufacturer"]=="Hewlett-Packard" or hardwareInfo["manufacturer"]=="Hewlett-Packard ":
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_hp_b))
        #DELL
        elif hardwareInfo["manufacturer"]=="Dell Inc." or hardwareInfo["manufacturer"]=="Dell Inc" or hardwareInfo["manufacturer"]=="Dell Inc. " or hardwareInfo["manufacturer"]=="Dell Inc ": 
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_dell_b))
        #Lenovo
        elif hardwareInfo["manufacturer"]=="LENOVO" or hardwareInfo["manufacturer"]=="LENOVO " or hardwareInfo["manufacturer"]=="Lenovo" or hardwareInfo["manufacturer"]=="Lenovo ":
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_lenovo_b))
        #Microsoft
        elif hardwareInfo["manufacturer"]=="Microsoft Corporation" or hardwareInfo["manufacturer"]=="Microsoft Corporation " or hardwareInfo["manufacturer"]=="Microsoft Corporation  " or hardwareInfo["manufacturer"]=="Microsoft Corporation   ":
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_microsoft_b))
        #Acer
        elif hardwareInfo["manufacturer"]=="Acer" or hardwareInfo["manufacturer"]=="Acer " or hardwareInfo["manufacturer"]=="Acer Incorporated" or hardwareInfo["manufacturer"]=="Acer Incorporated " or hardwareInfo["manufacturer"]=="Acer Incorporated  " or hardwareInfo["manufacturer"]=="Acer Incorporated   ":
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_acer_b))
            
    
    else:
        #framework
        if hardwareInfo["manufacturer"]=="framework" or hardwareInfo["manufacturer"]=="Framework":
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_framework_w))
        #MSI
        elif hardwareInfo["manufacturer"]=="Micro-Star International Co., Ltd." or hardwareInfo["manufacturer"]=="MSI" or hardwareInfo["manufacturer"]=="MSI " or hardwareInfo["manufacturer"]=="MSI Corporation" or hardwareInfo["manufacturer"]=="Micro-Star International Co., Ltd" or hardwareInfo["manufacturer"]=="Micro-Star International Co., Ltd ":
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_msi_w))
        #ASUS
        elif hardwareInfo["manufacturer"]=="ASUSTeK COMPUTER INC." or hardwareInfo["manufacturer"]=="ASUSTeK COMPUTER INC" or hardwareInfo["manufacturer"]=="ASUSTeK COMPUTER INC " or hardwareInfo["manufacturer"]=="ASUSTeK COMPUTER INC. ":
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_asus_w))
        #HP
        elif hardwareInfo["manufacturer"]=="HP" or hardwareInfo["manufacturer"]=="Hewlett-Packard" or hardwareInfo["manufacturer"]=="Hewlett-Packard ":
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_hp_w))
        #DELL
        elif hardwareInfo["manufacturer"]=="Dell Inc." or hardwareInfo["manufacturer"]=="Dell Inc" or hardwareInfo["manufacturer"]=="Dell Inc. " or hardwareInfo["manufacturer"]=="Dell Inc ":
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_dell_w))
        #Lenovo
        elif hardwareInfo["manufacturer"]=="LENOVO" or hardwareInfo["manufacturer"]=="LENOVO " or hardwareInfo["manufacturer"]=="Lenovo" or hardwareInfo["manufacturer"]=="Lenovo ":
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_lenovo_w))
        #Microsoft
        elif hardwareInfo["manufacturer"]=="Microsoft Corporation" or hardwareInfo["manufacturer"]=="Microsoft Corporation " or hardwareInfo["manufacturer"]=="Microsoft Corporation  " or hardwareInfo["manufacturer"]=="Microsoft Corporation   ": 
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_microsoft_w))
        #Acer
        elif hardwareInfo["manufacturer"]=="Acer" or hardwareInfo["manufacturer"]=="Acer " or hardwareInfo["manufacturer"]=="Acer Incorporated" or hardwareInfo["manufacturer"]=="Acer Incorporated " or hardwareInfo["manufacturer"]=="Acer Incorporated  " or hardwareInfo["manufacturer"]=="Acer Incorporated   ":
            manufacturerPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.manufacturer_acer_w))
            
    
    try:     
        manufacturerPic = manufacturerPic.subsample(int(round(1.75/getZoomValue(),0)))
        manufacturerPicLabel.config(image=manufacturerPic)
    except:
        print("無法取得電腦製造商Logo")
    
    
    
    
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
    try:
        gpuLabel.config(text="圖形處理器: "+hardwareInfo["gpu"]+" "+str(round(int(hardwareInfo["vram"])/(1024**3),1))+"GB")
    except:
        hardwareInfo["gpu"] = subprocess.check_output("wmic path win32_VideoController get name", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("big5").split("\n")[-3].strip()
        hardwareInfo["vram"] = subprocess.check_output("wmic path win32_VideoController get AdapterRAM", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("utf-8").split("\n")[-3].strip()
        try:
            gpuLabel.config(text="圖形處理器: "+hardwareInfo["gpu"]+" "+str(round(int(hardwareInfo["vram"])/(1024**3),1))+"GB")
        except:
            gpuLabel.config(text="圖形處理器: "+hardwareInfo["gpu"])
    
    
    hardDiskLabel.config(text="硬碟存儲器: "+hardwareInfo["hdd"])
    osLabel.config(text="作業系統: "+hardwareInfo["os"])
    osInstallDateLabel.config(text="安裝日期: "+hardwareInfo["installDate"][0:4]+"年"+hardwareInfo["installDate"][4:6]+"月"+hardwareInfo["installDate"][6:8]+"日 "+hardwareInfo["installDate"][8:10]+":"+hardwareInfo["installDate"][10:12]+":"+hardwareInfo["installDate"][12:14])
    #bios標籤(含製造商及版本)
    biosLabel.config(text="BIOS: v"+hardwareInfo["bios"]+" ("+hardwareInfo["biosManufacturer"]+")")
    
    
        
    return hardwareInfo

  
def scanBloatware():
    global bloatDB, myUWPList, appTiles
    #meter.config(subtext="正在掃描...", textright="分")
    meter["amountused"]=100
    meter["subtext"]="正在掃描..."
    myUWPList = UWPScanner.ScanUWP()
    #scan UWP
    appTiles=[]
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
            
            appTiles.append(uwpAppTile(app["appName"],app["developerName"],app["appDescription"],app["appType"],app["appPath"],app["installPath"],app["uninstallPath"],app["appShortName"],app["developerURL"],app["bloatRating"],app["necessary"],app["bloatReason"]))
            
            meter.update()
            time.sleep(0.1)
        
        #scan desktop app
        elif app["appType"]=="Desktop":
            path = Path(app["installPath"])
            if path.exists():
                if __debugMode:
                    debugMessage+="\n找到預裝軟體："+app["appName"]
                    consoleText.config(text=debugMessage)
                    print("找到預裝軟體："+app["appName"])
                meter.step(app["bloatRating"])
                if __debugMode:
                    debugMessage+="\ndeduct "+str(app["bloatRating"])+" points from "+app["appName"]
                    consoleText.config(text=debugMessage)
                    print("\ndeduct "+str(app["bloatRating"])+" points from "+app["appName"])
                if app["uninstallPath"].find("*")!=-1:
                    uninstallPath=app["uninstallPath"].split("*")
                    uninstallBase=Path(uninstallPath[0])
                    for folder in uninstallBase.iterdir():
                        if folder.is_dir():
                            if Path(str(folder)+uninstallPath[1]).exists():
                                app["uninstallPath"]=str(folder)+uninstallPath[1]
                                break
                    
                appTiles.append(uwpAppTile(app["appName"],app["developerName"],app["appDescription"],app["appType"],app["appPath"],app["installPath"],app["uninstallPath"],app["appShortName"],app["developerURL"],app["bloatRating"],app["necessary"],app["bloatReason"]))
                meter.update()
                time.sleep(0.1)
            
    
    meter["subtext"]="掃描完成!"
    
    
        
    
    #meter.config(subtext="掃描完成!", textright="分")

    
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
        gotoReport()
        

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
    iconPicStart = iconPicStart.subsample(int(1.75*4//zoomValue))


    start_height = int(450*zoomValue//1.75)
    start_width = int(600*zoomValue//1.75)
    screen_width = startUpScreen.winfo_screenwidth()
    screen_height = startUpScreen.winfo_screenheight()
        # Coordinates of the upper left corner of the window to make the window appear in the center
    x_cordinate = int((screen_width/2) - (start_width/2))
    y_cordinate = int((screen_height/2) - (start_height/2))
    startUpScreen.geometry("{}x{}+{}+{}".format(start_width, start_height, x_cordinate, y_cordinate))
    startUpScreen.overrideredirect(True)
    startFrame = ttk.Frame(startUpScreen)
    startFrame.pack(fill="both", padx=int(30*zoomValue//1.75), pady=int(30*zoomValue//1.75), expand=True)
    labelFrame = ttk.Frame(startFrame)
    labelFrame.pack(fill="both", expand=True)
    
    startIcon = ttk.Label(labelFrame, image=iconPicStart)
    startIcon.grid(row=0, column=0, sticky="w", padx=int(10*zoomValue//1.75), pady=int(10*zoomValue//1.75))

    startTitleLabel = ttk.Label(labelFrame, text="De-Bloater DB", font=("微軟正黑體", 25))
    startTitleLabel.grid(row=1, column=0, sticky="w", padx=int(10*zoomValue//1.75))
    startSubTitleLabel=ttk.Label(labelFrame, text="預裝軟體移除器", font=("微軟正黑體", 10))
    startSubTitleLabel.grid(row=2, column=0, sticky="w", padx=int(10*zoomValue//1.75))
    startSubTitleLabel=ttk.Label(labelFrame, text="軟體版本："+VERSION, font=("微軟正黑體", 8), bootstyle="secondary")
    startSubTitleLabel.grid(row=3, column=0, sticky="w", padx=int(10*zoomValue//1.75))
    
    #progressLabel
    progressLabel = ttk.Label(startFrame, text="正在檢查 Bloatware 定義檔...", font=("微軟正黑體", 8), bootstyle="primary")
    progressLabel.pack(side="bottom",padx=int(10*zoomValue//1.75),fill="x")

    #progressbar
    startProgressbar = ttk.Progressbar(startFrame, orient="horizontal", mode="determinate", maximum=100, value=0)
    startProgressbar.pack(side="bottom",padx=int(10*zoomValue//1.75),fill="x")
    
    
    global bloatDB
    startUpScreen.after(500, lambda:getBloatDB())
    
    startUpScreen.mainloop()
    
    
    
def gotoHelp():
    #開啟瀏覽器至GitHub專案https://github.com/justinlin099/De-BloaterDB-Client/wiki
    import webbrowser    
    urL='https://debloaterdb.justinl.in/'
    webbrowser.get('windows-default').open_new(urL)
    
def gotoSettings():
    #open config.json using notepad
    subprocess.call("notepad data/config.json", shell=True, creationflags = subprocess.CREATE_NO_WINDOW)
    

    # settingsScreen = ttk.Toplevel(root, topmost=True)
    
    # settingsScreen.overrideredirect(True)
    # settingsScreen.title("設定")
    # window_height = 600
    # window_width = 800
    # screen_width = root.winfo_screenwidth()
    # screen_height = root.winfo_screenheight()
    #     # Coordinates of the upper left corner of the window to make the window appear in the center
    # x_cordinate = int((screen_width/2) - (window_width/2))
    # y_cordinate = int((screen_height/2) - (window_height/2))
    # settingsScreen.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
    # settingsScreen.iconphoto(False, iconPic)
    
def gotoReport():
    global reportPage
    reportPage = ttk.Toplevel(root)
    #reportPage.overrideredirect(True)
    reportPage.title("掃描結果")
    window_height = int(768*zoomValue//1.75)
    window_width = int(1024*zoomValue//1.75)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
        # Coordinates of the upper left corner of the window to make the window appear in the center
    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))
    reportPage.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
    reportPage.iconphoto(False, iconPic)
    
    reportPageFrame = ttk.Frame(reportPage)
    reportPageFrame.pack(fill="both", padx=int(30*zoomValue//1.75), pady=int(30*zoomValue//1.75), expand=True)
    
    reportPageTitleFrame = ttk.Frame(reportPageFrame)
    reportPageTitleFrame.pack(side="top",fill="x", expand=True)
    reportPageTitleLabel = ttk.Label(reportPageTitleFrame, text="掃描結果", font=("微軟正黑體", 25))
    reportPageTitleLabel.grid(row=0, column=0, sticky="w", padx=int(10*zoomValue//1.75))
    reportPageSubTitleLabel = ttk.Label(reportPageTitleFrame, text="找到"+str(len(appTiles))+"款預裝軟體", font=("微軟正黑體", 10))
    reportPageSubTitleLabel.grid(row=1, column=0, sticky="w", padx=int(10*zoomValue//1.75))
    
    reportScrollFrame = scrolled.ScrolledFrame(reportPageFrame,autohide=True,height=int(450*zoomValue//1.75))
    reportScrollFrame.pack(side="top",fill="both", expand=True)
    
    
    for tile in appTiles:
        tile.pack(reportScrollFrame)
        print(tile.appName)
    
    bottomButtonFrame = ttk.Frame(reportPageFrame)
    bottomButtonFrame.pack(side="bottom",fill="x", expand=True)
    
    global reportPageBackButton, reportPageUninstallButton
    reportPageBackButton = ttk.Button(bottomButtonFrame, text="返回", command=reportPage.destroy)
    reportPageBackButton.pack(side="right", padx=int(10*zoomValue//1.75), pady=int(10*zoomValue//1.75))
    
    reportPageUninstallButton = ttk.Button(bottomButtonFrame, text="移除所選程式", command=uninstall_function, bootstyle="danger")
    reportPageUninstallButton.pack(side="right", padx=int(10*zoomValue//1.75), pady=int(10*zoomValue//1.75))
    
    # 產生報告
    reportGenerationButton = ttk.Button(bottomButtonFrame, text="產生報告並上傳", command=gotoGenerateReport)
    reportGenerationButton.pack(side="right", padx=int(10*zoomValue//1.75), pady=int(10*zoomValue//1.75))
    
    reportPage.mainloop()

def uninstallBloatApps():
    for tile in appTiles:
        tile.uninstall()
    print("uninstall done")
    time.sleep(8)
    scanbtn_function()
    reportPage.destroy()

def uninstall_function():
    boolean_wheel = threading.Thread(target=uninstallBloatApps)
    boolean_wheel.start()
   
    # block button
    reportPageBackButton['state'] = 'disabled'
    reportPageUninstallButton['state'] = 'disabled'
    
    
    
    
def gotoGenerateReport():
    generateReportWindow=ttk.Toplevel(reportPage)
    generateReportWindow.title("產生報告")
    window_height = int(600*zoomValue//1.75)
    window_width = int(800*zoomValue//1.75)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
        # Coordinates of the upper left corner of the window to make the window appear in the center
    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))
    generateReportWindow.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
    generateReportWindow.iconphoto(False, iconPic)
    
    generateReportFrame = ttk.Frame(generateReportWindow)
    generateReportFrame.pack(fill="both", padx=int(30*zoomValue//1.75), pady=int(30*zoomValue//1.75), expand=True)
    # 標題
    generateReportTitleFrame = ttk.Frame(generateReportFrame)
    generateReportTitleFrame.pack(side="top",fill="x", expand=True)
    generateReportTitleLabel = ttk.Label(generateReportTitleFrame, text="產生報告", font=("微軟正黑體", 25))
    generateReportTitleLabel.grid(row=0, column=0, sticky="w", padx=int(10*zoomValue//1.75))
    generateReportSubTitleLabel = ttk.Label(generateReportTitleFrame, text="請輸入您的名稱與電子郵件，按下確認後將會開啟您的電子郵件寄送程式，請將產生的報表放進附件中寄給我們。", font=("微軟正黑體", 10), wraplength=int(700*zoomValue//1.75))
    generateReportSubTitleLabel.grid(row=1, column=0, sticky="w", padx=int(10*zoomValue//1.75))
    
    #文字方塊外框
    generateReportEntryFrame = ttk.Frame(generateReportFrame)
    generateReportEntryFrame.pack(side="top",fill="x", expand=True)
    #新增一個文字方塊要求輸入使用者名稱
    userNameLabel = ttk.Label(generateReportEntryFrame, text="請輸入您的名稱：", font=("微軟正黑體", 10))
    userNameLabel.grid(row=0, column=0, sticky="w", padx=int(10*zoomValue//1.75), pady=int(10*zoomValue//1.75))
    userNameEntry = ttk.Entry(generateReportEntryFrame, font=("微軟正黑體", 10))
    userNameEntry.grid(row=0, column=1, sticky="we", padx=int(10*zoomValue//1.75), pady=int(10*zoomValue//1.75), columnspan=2)
    
    #新增一個文字方塊要求輸入使用者電子郵件
    userMailLabel = ttk.Label(generateReportEntryFrame, text="請輸入您的電子郵件：", font=("微軟正黑體", 10))
    userMailLabel.grid(row=1, column=0, sticky="w", padx=int(10*zoomValue//1.75), pady=int(10*zoomValue//1.75))
    userMailEntry = ttk.Entry(generateReportEntryFrame, font=("微軟正黑體", 10))
    userMailEntry.grid(row=1, column=1, sticky="we", padx=int(10*zoomValue//1.75), pady=int(10*zoomValue//1.75), columnspan=2)
    
    # 新增確認與取消按鈕
    confirmButton = ttk.Button(generateReportFrame, text="確認", command=lambda:generateReport(generateReportWindow, appTiles, hardwareInfo, myUWPList, userNameEntry.get(), userMailEntry.get(), meter.amountusedvar.get()))
    confirmButton.pack(side="right", padx=int(10*zoomValue//1.75), pady=int(10*zoomValue//1.75))
    cancelButton = ttk.Button(generateReportFrame, text="取消", command=generateReportWindow.destroy)
    cancelButton.pack(side="right", padx=int(10*zoomValue//1.75), pady=int(10*zoomValue//1.75))
    
    # userName = input("請輸入您的名稱：")
    # userMail = input("請輸入您的電子郵件：")
    # report = reportGenerator.generateReport(appTiles, hardwareInfo, myUWPList, userName, userMail, meter.amountusedvar.get())
    
    generateReportWindow.mainloop()
    
def generateReport(generateReportWindow,appTiles, hardwareInfo, myUWPList, userName, userMail, score):
    if userName=="" or userMail=="":
        ttk.dialogs.dialogs.Messagebox.show_error("請輸入您的名稱與電子郵件!", title='請輸入您的名稱與電子郵件', parent=generateReportWindow, alert=True)
        return
    else:
        report = reportGenerator.generateReport(appTiles, hardwareInfo, myUWPList, userName, userMail, score)
        ttk.dialogs.dialogs.Messagebox.show_info("已經將報告存檔於您的桌面上，檔名為"+report+"，將會開啟電子郵件寄送頁面，請將報告以附件檔傳送給我們！", title='產生報表成功', parent=generateReportWindow, alert=True)
        reportGenerator.uploadReport()
        ttk.dialogs.dialogs.Messagebox.show_info("感謝您的貢獻!", title='已成功上傳報告', parent=generateReportWindow, alert=True)
        generateReportWindow.destroy()
    
# 取得系統縮放倍率
def getZoomValue():
    import ctypes
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    zoomValue = user32.GetDpiForSystem()/96
    return zoomValue



loadConfig()

zoomValue = getZoomValue()

# 主程式
root=ttk.Window(themename=themeName, alpha=0)




#remove titlebar
root.overrideredirect(True)


#設定縮放
#utility.enable_high_dpi_awareness(root,2.25) 


root.title("De-Bloater DB 預裝軟體移除器")
#root.wm_attributes("-topmost", 1)
window_height = int(1024*zoomValue//1.75)
window_width = int(1280*zoomValue//1.75)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
    # Coordinates of the upper left corner of the window to make the window appear in the center
x_cordinate = int((screen_width/2) - (window_width/2))
y_cordinate = int((screen_height/2) - (window_height/2))
root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

iconPic = ttk.PhotoImage(data=base64.b64decode(DBDBERes.icon))

root.iconphoto(False, iconPic)
root.iconphoto(True, iconPic)
# root.iconbitmap(DBDBERes.iconico)
# root.iconbitmap(default=DBDBERes.iconico)
titleBarIcon = iconPic.subsample(int(20/zoomValue*1.75))


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
insideTitleFrame.pack(side="bottom", fill="x", padx=int(20*zoomValue//1.75), pady=int(20*zoomValue//1.75))



titleBar=ttk.Frame(titleFrame, bootstyle="info")
titleBar.pack(side="left", fill="x", padx=int(20*zoomValue//1.75), pady=int(20*zoomValue//1.75))
titleFrame.bind('<Button-1>', SaveLastClickPos)
titleFrame.bind('<B1-Motion>', Dragging)
titleBarButton=ttk.Frame(titleFrame, bootstyle="info")
titleBarButton.pack(side="right",  padx=int(20*zoomValue//1.75), pady=int(20*zoomValue//1.75))


# 標題標籤
titleIcon = ttk.Label(titleBar, image=titleBarIcon, bootstyle="inverse-info")
titleIcon.grid(row=0, column=0, sticky="w", padx=int(10*zoomValue//1.75), pady=int(10*zoomValue//1.75))
subTitleLabel = ttk.Label(titleBar, text="預裝軟體移除器", font=("微軟正黑體", 10), bootstyle="inverse-info")
subTitleLabel.grid(row=0, column=1, sticky="w")


#關閉視窗按鈕
closeButton = ttk.Button(titleBarButton, text="✕", command=quit, bootstyle="danger")
closeButton.grid(row=0, column=5, sticky="e",ipadx=int(20*zoomValue//1.75))
#最小化按鈕
minimizeButton = ttk.Button(titleBarButton, text="__", command=minimize, bootstyle="info")
minimizeButton.grid(row=0, column=4, sticky="e",ipadx=int(5*zoomValue//1.75))
#help按鈕
helpButton = ttk.Button(titleBarButton, text="?", command=gotoHelp, bootstyle="info")
helpButton.grid(row=0, column=3, sticky="e",ipadx=int(5*zoomValue//1.75))
#setting按鈕
settingButton = ttk.Button(titleBarButton, text="⚙", command=gotoSettings, bootstyle="info")
settingButton.grid(row=0, column=2, sticky="e",ipadx=int(5*zoomValue//1.75))

mainFrame = ttk.Frame(root)
mainFrame.pack(fill="both", padx=int(20*zoomValue//1.75), pady=int(20*zoomValue//1.75), expand=True,side="bottom")

titleLabel = ttk.Label(insideTitleFrame, text="De-Bloater DB", font=("微軟正黑體", 25), bootstyle="inverse-info")
titleLabel.grid(row=2, column=0, sticky="w", padx=int(10*zoomValue//1.75))
versionLabel = ttk.Label(insideTitleFrame, text="軟體版本："+VERSION, font=("微軟正黑體", 10), bootstyle="inverse-info")
versionLabel.grid(row=3, column=0, sticky="w", padx=int(10*zoomValue//1.75))
global tagLabel
tagLabel = ttk.Label(insideTitleFrame, text="Bloatware 定義檔版本："+tag, font=("微軟正黑體", 10), bootstyle="inverse-info")
tagLabel.grid(row=4, column=0, sticky="w", padx=int(10*zoomValue//1.75))


if __debugMode:
    Notebook = ttk.Notebook(mainFrame,bootstyle="info")
    Notebook.pack(side="left", padx=int(10*zoomValue//1.75), pady=int(10*zoomValue//1.75), fill="both", expand=True)
    hardwareInfoFrame = scrolled.ScrolledFrame(Notebook,autohide=True,width=int(700*zoomValue//1.75),padding=int(10*zoomValue//1.75))
    Notebook.add(hardwareInfoFrame.container, text="硬體資訊")
    #新增一個 scrolled text console 顯示除錯訊息
    consoleFrame = scrolled.ScrolledFrame(Notebook,autohide=True,width=int(700*zoomValue//1.75),padding=int(10*zoomValue//1.75))
    Notebook.add(consoleFrame.container, text="除錯訊息")
    
    
    consoleText=ttk.Label(consoleFrame,text=debugMessage, wraplength=int(700*zoomValue//1.75))
    consoleText.pack(side="top", fill="both", expand=True)
    
    
else:
    #hardwareinfo frame
    hardwareInfoOFrame = ttk.LabelFrame(mainFrame, text="硬體資訊", bootstyle="info")
    hardwareInfoOFrame.pack(side="left", padx=int(10*zoomValue//1.75), pady=int(10*zoomValue//1.75), fill="both", expand=True)
    hardwareInfoFrame = scrolled.ScrolledFrame(hardwareInfoOFrame,autohide=True,width=int(700*zoomValue//1.75),padding=int(10*zoomValue//1.75))
    hardwareInfoFrame.pack(side="top", fill="both", expand=True)    



   
manufacturerPicLabel = ttk.Label(hardwareInfoFrame)
manufacturerPicLabel.grid(column=0, row=0, padx=int(10*zoomValue//1.75), pady=int(10*zoomValue//1.75), sticky="w")
manufacturerLabel= ttk.Label(hardwareInfoFrame, text="我的電腦",font=("微軟正黑體", 25), wraplength=int(700*zoomValue//1.75))
manufacturerLabel.grid(column=0, row=1, padx=int(10*zoomValue//1.75), sticky="w")
modelLabel= ttk.Label(hardwareInfoFrame, text="我的電腦",font=("微軟正黑體", 15), wraplength=int(700*zoomValue//1.75))
modelLabel.grid(column=0, row=2, padx=int(10*zoomValue//1.75), sticky="w")
cpuLabel = ttk.Label(hardwareInfoFrame,text="CPU: Unknown", wraplength=int(700*zoomValue//1.75))
cpuLabel.grid(column=0, row=3, padx=int(10*zoomValue//1.75), pady=int(5*zoomValue//1.75), sticky="w")
coreLabel = ttk.Label(hardwareInfoFrame,text="CPU: Unknown", wraplength=int(700*zoomValue//1.75))
coreLabel.grid(column=0, row=4, padx=int(10*zoomValue//1.75), sticky="w")
ramLabel = ttk.Label(hardwareInfoFrame,text="RAM: Unknown", wraplength=int(700*zoomValue//1.75))
ramLabel.grid(column=0, row=5, padx=int(10*zoomValue//1.75), pady=int(5*zoomValue//1.75), sticky="w")
gpuLabel = ttk.Label(hardwareInfoFrame,text="GPU: Unknown", wraplength=int(700*zoomValue//1.75))
gpuLabel.grid(column=0, row=6, padx=int(10*zoomValue//1.75), pady=0, sticky="w")
hardDiskLabel = ttk.Label(hardwareInfoFrame,text="Hard Disk: Unknown", wraplength=int(700*zoomValue//1.75))
hardDiskLabel.grid(column=0, row=7, padx=int(10*zoomValue//1.75), pady=int(5*zoomValue//1.75), sticky="w")
osLabel = ttk.Label(hardwareInfoFrame,text="OS: Unknown", wraplength=int(700*zoomValue//1.75))
osLabel.grid(column=0, row=8, padx=int(10*zoomValue//1.75), pady=0, sticky="w")
osInstallDateLabel = ttk.Label(hardwareInfoFrame,text="OS Install Date: Unknown", wraplength=int(700*zoomValue//1.75))
osInstallDateLabel.grid(column=0, row=9, padx=int(10*zoomValue//1.75), pady=int(5*zoomValue//1.75), sticky="w")
biosLabel = ttk.Label(hardwareInfoFrame,text="BIOS: Unknown", wraplength=int(700*zoomValue//1.75))
biosLabel.grid(column=0, row=10, padx=int(10*zoomValue//1.75), pady=0, sticky="w")




meterFrame=ttk.Frame(mainFrame)
meterFrame.pack(side="left", fill="both", expand=True)
# # 畫一個 Meter 在畫面正中央當掃描按鈕

meter = ttk.Meter(meterFrame, amountused=100, subtext="尚未掃描", textright="分", bootstyle="warning",textfont=("微軟正黑體", 30),subtextfont=("微軟正黑體", 10))
meter.pack(side="top", pady=int(30*zoomValue//1.75), padx=int(30*zoomValue//1.75), fill="both", expand=True)

scanProgressBar = ttk.Progressbar(meterFrame, orient="horizontal", mode="indeterminate", maximum=100, value=0)
scanProgressBar.pack(side="bottom", padx=int(30*zoomValue//1.75), fill="x", expand=True)

scanButton=ttk.Button(meterFrame, text="掃描", command=scanbtn_function, bootstyle="success")
scanButton.pack(side="top", padx=int(30*zoomValue//1.75), pady=int(10*zoomValue//1.75), fill="both", expand=True)

#新增查看報表按鈕
reportButton=ttk.Button(meterFrame, text="查看報表", command=gotoReport, bootstyle="info")
reportButton.pack(side="top", padx=int(30*zoomValue//1.75), pady=int(10*zoomValue//1.75), fill="both", expand=True)
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
    




    
