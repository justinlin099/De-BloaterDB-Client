import time
import subprocess
from pathlib import Path

def generateReport(appTiles, hardwareInfo, uwpList, userName, Email, score):
    # Code to generate report

    fileName=str(Path.home())+"\\desktop\\"+time.strftime("%Y-%m-%d-%H%M%S-")+Email+".md"
    reportContent=""
    
    # 新增Header
    reportContent+="---\nlayout: post\ntitle: "
    
    #新增標題(電腦型號)
    reportContent+=hardwareInfo["model"]+"\nsubtitle: "
    #新增副標題(電腦製造商)
    reportContent+=hardwareInfo["manufacturer"]+"\ncategories: "
    #新增分類(電腦製造商)
    if hardwareInfo["manufacturer"]=="framework" or hardwareInfo["manufacturer"]=="Framework":
        reportContent+="Framework"
    #MSI
    elif hardwareInfo["manufacturer"]=="Micro-Star International Co., Ltd." or hardwareInfo["manufacturer"]=="MSI" or hardwareInfo["manufacturer"]=="MSI " or hardwareInfo["manufacturer"]=="MSI Corporation" or hardwareInfo["manufacturer"]=="Micro-Star International Co., Ltd" or hardwareInfo["manufacturer"]=="Micro-Star International Co., Ltd ":
        reportContent+="MSI"
    #ASUS
    elif hardwareInfo["manufacturer"]=="ASUSTeK COMPUTER INC." or hardwareInfo["manufacturer"]=="ASUSTeK COMPUTER INC" or hardwareInfo["manufacturer"]=="ASUSTeK COMPUTER INC " or hardwareInfo["manufacturer"]=="ASUSTeK COMPUTER INC. ":
        reportContent+="ASUS"                
    #HP
    elif hardwareInfo["manufacturer"]=="HP" or hardwareInfo["manufacturer"]=="Hewlett-Packard" or hardwareInfo["manufacturer"]=="Hewlett-Packard ":
        reportContent+="HP"
    #DELL
    elif hardwareInfo["manufacturer"]=="Dell Inc." or hardwareInfo["manufacturer"]=="Dell Inc" or hardwareInfo["manufacturer"]=="Dell Inc. " or hardwareInfo["manufacturer"]=="Dell Inc ": 
        reportContent+="DELL"
    #Lenovo
    elif hardwareInfo["manufacturer"]=="LENOVO" or hardwareInfo["manufacturer"]=="LENOVO " or hardwareInfo["manufacturer"]=="Lenovo" or hardwareInfo["manufacturer"]=="Lenovo ":
        reportContent+="Lenovo"
    #Microsoft
    elif hardwareInfo["manufacturer"]=="Microsoft Corporation" or hardwareInfo["manufacturer"]=="Microsoft Corporation " or hardwareInfo["manufacturer"]=="Microsoft Corporation  " or hardwareInfo["manufacturer"]=="Microsoft Corporation   ":
        reportContent+="Microsoft"
    #Acer
    elif hardwareInfo["manufacturer"]=="Acer" or hardwareInfo["manufacturer"]=="Acer " or hardwareInfo["manufacturer"]=="Acer Incorporated" or hardwareInfo["manufacturer"]=="Acer Incorporated " or hardwareInfo["manufacturer"]=="Acer Incorporated  " or hardwareInfo["manufacturer"]=="Acer Incorporated   ":
        reportContent+="Acer"
    else :
        reportContent+=hardwareInfo["manufacturer"]
    
    reportContent+="\ntags: ["
    #新增標籤(E-mail)
    reportContent+=Email+"]\nauthor: 由 "
    #新增作者(使用者名稱)
    reportContent+=userName+" 上傳\n---\n\n"
    
    #新增分數
    reportContent+="<h2>總分：<font color=\""
    if(score>=90):
        reportContent+="green"
    elif(score>=60):
        reportContent+="orange"
    else:
        reportContent+="red"
    reportContent+="\">"+str(score)+"</font>/100</h2>\n\n"
    
    # 硬體資訊
    reportContent+="## 硬體資訊\n\n"
    reportContent+="| 項目 | 資訊 |\n| :------ | :--- |\n"
    reportContent+="| 製造商 | "+hardwareInfo["manufacturer"]+" |\n"
    reportContent+="| 電腦型號 | "+hardwareInfo["model"]+" |\n"
    reportContent+="| 中央處理器 | "+hardwareInfo["cpu"]+" |\n"
    reportContent+="| 處理器核心 | "+hardwareInfo["core"]+" Cores/ "+hardwareInfo["thread"]+" Threads |\n"
    reportContent+="| 系統記憶體 | "+hardwareInfo["ram"]["String"]+" |\n"
    try:
        reportContent+="| 圖形處理器 | "+hardwareInfo["gpu"]+" "+str(round(int(hardwareInfo["vram"])/(1024**3),1))+"GB"+" |\n"
    except:
        hardwareInfo["gpu"] = subprocess.check_output("wmic path win32_VideoController get name", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("big5").split("\n")[-3].strip()
        hardwareInfo["vram"] = subprocess.check_output("wmic path win32_VideoController get AdapterRAM", shell=False, creationflags = subprocess.CREATE_NO_WINDOW).decode("utf-8").split("\n")[-3].strip()
        try:
            reportContent+="| 圖形處理器 | "+hardwareInfo["gpu"]+" "+str(round(int(hardwareInfo["vram"])/(1024**3),1))+"GB"+" |\n"
        except:
            reportContent+="| 圖形處理器 | "+hardwareInfo["gpu"]+" |\n"
    reportContent+="| 硬碟存儲器 | "+hardwareInfo["hdd"]+" |\n"
    reportContent+="| 作業系統 | "+hardwareInfo["os"]+" |\n"
    reportContent+="| 安裝日期 | "+hardwareInfo["installDate"][0:4]+"年"+hardwareInfo["installDate"][4:6]+"月"+hardwareInfo["installDate"][6:8]+"日 "+hardwareInfo["installDate"][8:10]+":"+hardwareInfo["installDate"][10:12]+":"+hardwareInfo["installDate"][12:14]+" |\n"
    reportContent+="| BIOS | v"+hardwareInfo["bios"]+" ("+hardwareInfo["biosManufacturer"]+")"+" |\n\n"
    
    # 電腦製造商預裝軟體
    reportContent+="## 電腦製造商預裝軟體\n"
    #格式
    #### Clipchamp
    # > Clipchamp  
    # > 評分： 🔴⚫⚫⚫⚫  
    # > 描述：微軟收購的影片剪輯軟體，且內部有付費選項，功能也較陽春，如果不需要可以移除節省硬碟空間 
    for tile in appTiles:
        #辨識是否為微軟的預裝軟體，如果是則跳過
        if tile.developerName!="Microsoft" and tile.developerName!="microsoft" and tile.developerName!="Clipchamp":
            reportContent+="#### "+tile.appName+"\n"
            reportContent+="> "+tile.developerName+"  \n"
            reportContent+="> 評分： "
            for i in range(5):
                if i<tile.bloatRating:
                    reportContent+="🔴"
                else:
                    reportContent+="⚪"
            reportContent+="  \n"
            reportContent+="> 描述："+tile.bloatReason+"  \n\n"
            
    # 微軟預裝軟體
    reportContent+="## Microsoft 預裝軟體\n"
    
    for tile in appTiles:
        #辨識是否為微軟的預裝軟體，如果是則跳過
        if tile.developerName=="Microsoft" or tile.developerName=="microsoft" or tile.developerName=="Clipchamp":
            reportContent+="#### "+tile.appName+"\n"
            reportContent+="> "+tile.developerName+"  \n"
            reportContent+="> 評分： "
            for i in range(5):
                if i<tile.bloatRating:
                    reportContent+="🔴"
                else:
                    reportContent+="⚪"
            reportContent+="  \n"
            reportContent+="> 描述："+tile.bloatReason+"  \n\n"
              

    # 建立並寫入檔案
    try:
        with open(fileName, "w+", encoding="utf-8") as f:
            f.write(reportContent)
    except:
        fileName=str(Path.home())+time.strftime("%Y-%m-%d-%H%M%S-")+Email+".md"
        with open(fileName, "w+", encoding="utf-8") as f:
            f.write(reportContent)
    
    return time.strftime("%Y-%m-%d-%H%M%S-")+Email+".md"
        
        
def uploadReport():
    # Code to upload report
    #呼叫 Desktop 沒用，先暫時 Disable
    #subprocess.Popen(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe', "explorer.exe \"desktop\""], stdout=subprocess.PIPE, creationflags = subprocess.CREATE_NO_WINDOW)
    
    import webbrowser
    urL="mailto:justin.lin099backup+debloaterdb@gmail.com?subject=貢獻 De-Bloater DB 掃描結果&body=請將報告檔拖放至此傳送給我們！"
    webbrowser.get('windows-default').open_new(urL)