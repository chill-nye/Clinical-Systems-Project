'''
    Copyright (C) 2019 Stefan V. Pantazi (svpantazi@gmail.com)    
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see http://www.gnu.org/licenses/.
'''
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from modINFO74000.emr_db import MiniEMRMongo
from modINFO74000.emr_misc_ui import *
from modINFO74000.emr_const import *

def getEmployeeRecordByIEN(IEN):
    empl_rec=MiniEMRMongo.db.employees.find_one({'IEN':str(IEN)})            
    return empl_rec

class CurrentProvider():
    Record=None

    @classmethod
    def logout(cls):
        print('[{0}] has logged out!'.format(cls.Record["full_name"]))        
        cls.Record=None

    @classmethod
    def login(cls,user,passw):
        if NO_LOGON_TESTING: return True
        else:
            EMPLOYEE_QUERY={'username':user}
            employee_collection = MiniEMRMongo.db.employees
            cls.Record=employee_collection.find_one(EMPLOYEE_QUERY)            
            if cls.Record!=None and cls.Record["password"]==passw: return True
            else: return False


class LoginWindowDialogFrame(tk.Frame):

    def createWidgets(self):
        #username and password UI variables 
        self.userNameVar = tk.StringVar()    
        self.userPassVar = tk.StringVar()        
        #username and password labels
        userNameLabel=ttk.Label(self, text="User name:")
        userNameLabel.grid(column=0, row=0, sticky='E')             
        userPassLabel=ttk.Label(self, text="Password:")
        userPassLabel.grid(column=0, row=1, sticky='E')
        #username and password entry boxes
        self.UserNameTextBox = ttk.Entry(self,width=24, textvariable = self.userNameVar)
        self.UserNameTextBox.grid(column=1, row=0,padx=2,pady=2)
        self.PasswordTextBox = ttk.Entry(self,width=24, textvariable = self.userPassVar, show='*')
        self.PasswordTextBox.grid(column=1, row=1,padx=2,pady=2)
        #login button
        self.login_button = ttk.Button(self, width=12, text="Login", command=self.master.try_login)
        self.login_button.grid(column=1, row=2,padx=2,pady=2)
        #institution logo        
        logo_label=ttk.Label(self,text="Institution Logo")
        logo_label.grid(column=2,row=0,rowspan=2)
        setLabelImage(logo_label,PATH_TO_IMAGE_FILES+'/conestoga_college_logo.png',2)
        

    def clear(self):
        #clear textboxes
        self.UserNameTextBox.delete(0,'end')
        self.PasswordTextBox.delete(0,'end')
        self.UserNameTextBox.focus()#refocus username textbx

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()    
                
class LoginWindowDialog(TopDialogWindow):

    def __init__(self, master=None):
        TopDialogWindow.__init__(self, master)
        self.loginUIFrame = LoginWindowDialogFrame(self)
        self.loginUIFrame.pack(side="top", fill="both", expand = True)
        self.title(APP_NAME+" Login")
        self.protocol("WM_DELETE_WINDOW", self.on_close)      
        def enter_press(event):
            self.try_login()
        self.bind('<Return>', enter_press)#allows pressing Enter to logon      

    def on_close(self):
        self.destroy()
        #destroy master as well
        self.master.destroy()

    def show(self):
        super(LoginWindowDialog, self).show()
        self.loginUIFrame.clear()

    def try_login(self):
        user=self.loginUIFrame.userNameVar.get()        
        passw=self.loginUIFrame.userPassVar.get()
        print("\nTrying to log on as [{0}]!".format(user))

        if CurrentProvider.login(user,passw):
            print('Login success. Welcome [{0}, ({1})]!'.format(user,CurrentProvider.Record["full_name"]))
            self.hide()#hide login
            self.master.title("Mini-EMR (logged on as: {0})".format(CurrentProvider.Record["full_name"]))
        else:
            print('Login fail. Buzz off [{0}]!'.format(user))
            messagebox.showerror("Login error","Invalid user name or password.")
            self.loginUIFrame.clear()#clear UI



