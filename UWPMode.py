#UWPMode.py
#架構：掃描 UWP 應用程式清單，比對 Windows 預設清單，產生 UWP 應用程式清單

#匯入模組
import os
import json
import subprocess

#執行Powershell指令並且擷取輸出字串
process = subprocess.Popen(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe', 'Get-AppxPackage'], stdout=subprocess.PIPE)

for line in process.stdout:
    print(line.decode('utf-8'))
