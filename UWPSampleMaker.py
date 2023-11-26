import json
import UWPScanner

#掃描標準 UWP 並記錄
result=UWPScanner.ScanUWP()

with open("refDB.json", "w") as outfile: 
    json.dump(result, outfile,indent=4)
    
    
    
    
