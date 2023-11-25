def UWPScanner():
    import subprocess
    
    rawData = []

    #執行Powershell指令並且擷取輸出字串
    process = subprocess.Popen(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe', 'Get-AppxPackage'], stdout=subprocess.PIPE)

    for line in process.stdout:
        rawData.append(line.decode('utf-8'))

    for line in rawData:
        print(line, end="")
    
if __name__ == '__main__':
    UWPScanner()