import subprocess
DebugMode = True


def ScanUWP():
    import subprocess
    
    rawData = []

    #執行Powershell指令並且擷取輸出字串
    process = subprocess.Popen(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe', 'Get-AppxPackage'], stdout=subprocess.PIPE)

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
    
    
    if DebugMode:
        print(uwpAppList)
    
    return uwpAppList
    
def getProcessor():
    CPUNameOut=subprocess.Popen(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe', '(Get-ItemProperty Registry::HKEY_LOCAL_MACHINE\HARDWARE\DESCRIPTION\System\CentralProcessor\\0\).ProcessorNameString'], stdout=subprocess.PIPE)
    for line in CPUNameOut.stdout:
        CPUName=line.decode('utf-8')
    return CPUName[:-2]

def getInstallDate():
    InstallDateOut=subprocess.Popen(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe', 'wmic OS get InstallDate'], stdout=subprocess.PIPE)
    InstallDateRaw=[]
    for line in InstallDateOut.stdout:
        InstallDateRaw.append(line.decode('utf-8'))
    InstallDate={}
    InstallDate["Year"]=InstallDateRaw[1][0:4]
    InstallDate["Month"]=InstallDateRaw[1][4:6]
    InstallDate["Day"]=InstallDateRaw[1][6:8]
    
    return InstallDate

def getManufacturer():
    ManufacturerOut=subprocess.Popen(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe', '(Get-ItemProperty Registry::HKEY_LOCAL_MACHINE\HARDWARE\DESCRIPTION\System\BIOS\).BaseBoardManufacturer'], stdout=subprocess.PIPE)
    for line in ManufacturerOut.stdout:
        Manufacturer=line.decode('utf-8')
    return Manufacturer[:-2]

def getMemory():
    MemoryTypeOut=subprocess.Popen(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe', 'wmic memorychip get SMBIOSMemoryType'], stdout=subprocess.PIPE)
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
    MemorySpeedOut=subprocess.Popen(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe', 'wmic memorychip get Speed'], stdout=subprocess.PIPE)
    MemorySpeedRaw=[]
    for line in MemorySpeedOut.stdout:
        MemorySpeedRaw.append(line.decode('utf-8'))
    MemorySpeed=MemorySpeedRaw[1][:4]
    Memory["Speed"]=MemorySpeed
    
    #calculate memory size
    MemorySizeOut=subprocess.Popen(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe', 'wmic memorychip get Capacity'], stdout=subprocess.PIPE)
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