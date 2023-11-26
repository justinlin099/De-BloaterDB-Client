import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import ImageTk, Image
import DBDBERes
import base64
import UWPMode

#建立模式選擇視窗
def GenerateSelectionWindow():
    #建立視窗
    global root 
    root = ttk.Window(themename="darkly")

    desktopAppIcon= ImageTk.PhotoImage(data= base64.b64decode(DBDBERes.desktopAppIcon))
    uwpAppIcon= ImageTk.PhotoImage(data= base64.b64decode(DBDBERes.uwpAppIcon))
    
    #設定視窗標題
    root.title("De-Bloater DB 資料庫編輯器")

    #按鈕 Frame
    btnFrame = ttk.Frame(root)
    btnFrame.pack(fill=tk.X, pady=30, padx=30)

    #新增標題標籤
    title = ttk.Label(btnFrame, text="De-Bloater DB 資料庫編輯器", font=("微軟正黑體", 20), anchor=tk.W)
    title.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.E, pady=20, padx=5)

    #選擇模式按鈕桌面程式編輯器
    desktopDataBaseBtn = ttk.Button(btnFrame, image=desktopAppIcon, text="桌面程式資料庫編輯器", compound=tk.TOP, bootstyle="Primary")
    desktopDataBaseBtn.grid(row=1, column=0, ipady=30, ipadx=50,padx=5, pady=5)

    #選擇模式按鈕UWP程式編輯器
    uwpDataBaseBtn = ttk.Button(btnFrame, image=uwpAppIcon, text="UWP程式資料庫編輯器", compound=tk.TOP, bootstyle="Primary", command=selectUWPMode)
    uwpDataBaseBtn.grid(row=1, column=1, ipady=30, ipadx=50,padx=5, pady=5)

    root.mainloop()

def selectUWPMode():
    UWPMode.UWPScanner.ScanUWP()
    root.destroy()
    
def selectDesktopMode():
    root.destroy()

GenerateSelectionWindow()