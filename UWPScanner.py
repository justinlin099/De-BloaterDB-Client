import subprocess
DebugMode = False


def ScanUWP():
    import subprocess
    
    rawData = []

    #執行Powershell指令並且擷取輸出字串
    process = subprocess.Popen(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe', 'Get-AppxPackage'], stdout=subprocess.PIPE, creationflags = subprocess.CREATE_NO_WINDOW)

    for line in process.stdout:
        rawData.append(line.decode('utf-8'))

    if DebugMode:
        for line in rawData:
            print(line, end="")
        
    result=processData(rawData)
    return result
    
def processData(rawData):
    
    
    #建立空字典
    uwpAppList = {}
    uwpAppList["ProcessorName"]=getProcessor()
    uwpAppList["InstallDate"]=getInstallDate()
    uwpAppList["Manufacturer"]=getManufacturer()
    uwpAppList["Memory"]=getMemory()
    uwpAppList["UWPApps"]={}
    
    for i in range(len(rawData)):
        #判斷是否為應用程式名稱
        if rawData[i][0:4]=="Name":
            #取得應用程式名稱
            uwpAppName=rawData[i][20:-2]
            #建立應用程式名稱的字典
            uwpAppList["UWPApps"][uwpAppName]={}
            #建立應用程式名稱的字典的應用程式名稱鍵值
            uwpAppList["UWPApps"][uwpAppName]["Name"]=uwpAppName
            
            #取得應用程式架構
            uwpAppArchitecture=rawData[i+2][20:-2]
            uwpAppList["UWPApps"][uwpAppName]["Architecture"]=uwpAppArchitecture
            
            #取得應用程式版本
            uwpAppVersion=rawData[i+4][20:-2]
            uwpAppList["UWPApps"][uwpAppName]["Version"]=uwpAppVersion
            
            #取得應用程式發行者
            nameSplit=uwpAppName.split(".")
            uwpAppPublisher=nameSplit[0]
            uwpAppList["UWPApps"][uwpAppName]["Publisher"]=uwpAppPublisher
        
    if DebugMode:
        print(uwpAppList)
    
    return uwpAppList
    
def getProcessor():
    CPUNameOut=subprocess.Popen(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe', '(Get-ItemProperty Registry::HKEY_LOCAL_MACHINE\HARDWARE\DESCRIPTION\System\CentralProcessor\\0\).ProcessorNameString'], stdout=subprocess.PIPE, creationflags = subprocess.CREATE_NO_WINDOW)
    for line in CPUNameOut.stdout:
        CPUName=line.decode('utf-8')
    return CPUName[:-2]

def getInstallDate():
    InstallDateOut=subprocess.Popen(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe', 'wmic OS get InstallDate'], stdout=subprocess.PIPE, creationflags = subprocess.CREATE_NO_WINDOW)
    InstallDateRaw=[]
    for line in InstallDateOut.stdout:
        InstallDateRaw.append(line.decode('utf-8'))
    InstallDate={}
    InstallDate["Year"]=InstallDateRaw[1][0:4]
    InstallDate["Month"]=InstallDateRaw[1][4:6]
    InstallDate["Day"]=InstallDateRaw[1][6:8]
    
    return InstallDate

def getManufacturer():
    manufacturerOut=subprocess.Popen(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe', '(Get-ItemProperty Registry::HKEY_LOCAL_MACHINE\HARDWARE\DESCRIPTION\System\BIOS\).BaseBoardManufacturer'], stdout=subprocess.PIPE, creationflags = subprocess.CREATE_NO_WINDOW)
    manufacturer=""
    for line in manufacturerOut.stdout:
        manufacturer=line.decode('utf-8')
    return manufacturer[:-2]

def getMemory():
    MemoryTypeOut=subprocess.Popen(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe', 'wmic memorychip get SMBIOSMemoryType'], stdout=subprocess.PIPE, creationflags = subprocess.CREATE_NO_WINDOW)
    MemoryTypeRaw=[]
    for line in MemoryTypeOut.stdout:
        MemoryTypeRaw.append(line.decode('utf-8'))
    MemoryTypeRaw=MemoryTypeRaw[1][:2]
    
    #辨識記憶體類型
    if MemoryTypeRaw=="24":
        MemoryType="DDR3"
    elif MemoryTypeRaw=="26":
        MemoryType="DDR4"
    elif MemoryTypeRaw=="34":
        MemoryType="DDR5"
    else:
        MemoryType="Unknown"
        
    Memory={}
    Memory["Type"]=MemoryType
    
    #detect memory speed
    MemorySpeedOut=subprocess.Popen(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe', 'wmic memorychip get Speed'], stdout=subprocess.PIPE, creationflags = subprocess.CREATE_NO_WINDOW)
    MemorySpeedRaw=[]
    for line in MemorySpeedOut.stdout:
        MemorySpeedRaw.append(line.decode('utf-8'))
    MemorySpeed=MemorySpeedRaw[1][:4]
    Memory["Speed"]=MemorySpeed
    
    #calculate memory size
    MemorySizeOut=subprocess.Popen(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe', 'wmic memorychip get Capacity'], stdout=subprocess.PIPE, creationflags = subprocess.CREATE_NO_WINDOW)
    MemorySizeRaw=[]
    for line in MemorySizeOut.stdout:
        MemorySizeRaw.append(line.decode('utf-8'))
    MemorySize=0
    for i in MemorySizeRaw[1:-1]:
        MemorySize+=int(i[:-2])
    MemorySize=MemorySize/1024/1024/1024
    Memory["Size"]=int(MemorySize)
    
    Memory["String"]=str(Memory["Size"])+"GB "+Memory["Type"]+" "+Memory["Speed"]+"MHz"
    
    return Memory

if __name__ == '__main__':
    ScanUWP()