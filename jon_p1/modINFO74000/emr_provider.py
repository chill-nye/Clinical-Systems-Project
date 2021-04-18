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
from modINFO74000.emr_crypto import *

class CurrentProvider():
    Record=None
    provider_details = []

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
            if cls.Record!=None and check_salt_password(cls.Record["password"],passw): return True
            else: return False

    @classmethod
    def selectProviderByIEN(cls, IEN):
        employee_collection=MiniEMRMongo.db.employees
        query_result=employee_collection.find_one({"IEN":str(IEN)})
        if query_result==None:
            #move this to the debug tab or as a pop up
            print("Could not find the provider with IEN:", IEN)
        else:
            print("Provider record found:")
            for i in query_result:
                if i == 'IEN':
                    CurrentProvider.provider_details.append(query_result['IEN'])
                if i == 'full_name':
                    CurrentProvider.provider_details.append(query_result['full_name'])

class DrugList():
    drug_details = []

    @classmethod
    def selectDrugByDIN(cls, DIN):
        drug_collection=MiniEMRMongo.db.drug_formulary
        query_result=drug_collection.find_one({"DIN":str(DIN)})
        if query_result==None:
            #move this to the debug tab or as a pop up
            print("Could not find the drug with DIN:", DIN)
        else:
            print("Drug details found:")
            for i in query_result:
                if i == 'DIN':
                    DrugList.drug_details.append(query_result['DIN'])
                if i == 'TRADENAME':
                    DrugList.drug_details.append(query_result['TRADENAME'])

class administration_details():
    admin_details = []

    @classmethod
    def queryadministrationdata(cls, MRN):
        administration_collection=MiniEMRMongo.db.D_administration
        query_result=administration_collection.find({"patientMRN":int(MRN)})
        if query_result==None:
            print('Could not find drug administration events')
        else:
            print('Found event(s):')
            query_result = list(query_result)
            for i in query_result:
                print(query_result[i])

class CurrentProviderPhoto():
    @classmethod
    def updateCurrentProviderPhoto(cls,filename):
        Record = CurrentProvider.Record
        newFileOId=MiniEMRMongo.uploadGridFSFile(filename)
        Record["photo"]=newFileOId
        employee_collection=MiniEMRMongo.db.employees
        employee_collection.update_one(
                                    {'_id':Record['_id']},
                                    {'$set':{'photo':newFileOId}})

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
        try:
            setLabelImage(logo_label,PATH_TO_IMAGE_FILES+'/conestoga_college_logo.png',2)
        except:
            try:
                setLabelImage(logo_label,CH_PATH_TO_IMAGE_FILES+'/conestoga_college_logo.png',2)
            except:
                setLabelImage(logo_label,ST_PATH_TO_IMAGE_FILES+'/conestoga_college_logo.png',2)
        
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

    def openImageFileDialog(self):
        filename=filedialog.askopenfilename(initialdir= ".",title ="Open file",
            filetypes = (("png file","*.png"),("any file","*.*")))
        print("File selected:",filename)
        setLabelImage(self.employeePhotoLabel,filename)
        if filename!=():
            CurrentProviderPhoto.updateCurrentProviderPhoto(filename)
            self.summaryScrolledText.replace('1.0','end',CurrentProvider.Record())

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


class passwordChangeUIFrame(tk.Frame):
    def createWidgets(self):
        self.oldpassword = tk.StringVar()    
        self.newpassword = tk.StringVar()
        self.confirmnewpassword = tk.StringVar()

        oldpasswordLabel=ttk.Label(self, text="Current Password:")
        oldpasswordLabel.grid(column=0, row=0, sticky='E')             
        newpasswordLabel=ttk.Label(self, text="Enter new password:")
        newpasswordLabel.grid(column=0, row=1, sticky='E')
        confirmnewpasswordLabel=ttk.Label(self, text="Retype new password:")
        confirmnewpasswordLabel.grid(column=0, row=2, sticky='E')

        self.oldpasswordTextBox = ttk.Entry(self,width=24, textvariable = self.oldpassword, show='*')
        self.oldpasswordTextBox.grid(column=1, row=0,padx=2,pady=2)
        self.newPasswordTextBox = ttk.Entry(self,width=24, textvariable = self.newpassword, show='*')
        self.newPasswordTextBox.grid(column=1, row=1,padx=2,pady=2)
        self.confirmnewPasswordTextBox = ttk.Entry(self,width=24, textvariable = self.confirmnewpassword, show='*')
        self.confirmnewPasswordTextBox.grid(column=1, row=2,padx=2,pady=2)

        self.confirm_button = ttk.Button(self, width=16, text="Change Password", command=self.master.update_password)
        self.confirm_button.grid(column=1, row=3,padx=2,pady=2)

    def clear(self):
        #clear textboxes
        self.oldpasswordTextBox.delete(0,'end')
        self.newPasswordTextBox.delete(0,'end')
        self.confirmnewPasswordTextBox.delete(0,'end')
        self.oldpasswordTextBox.focus()

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

class UpdateCurrentProviderPassword(TopDialogWindow):
    def __init__(self, master=None):
        TopDialogWindow.__init__(self, master)
        self.passwordChangeUI = passwordChangeUIFrame(self)
        self.passwordChangeUI.pack(side="top", fill="both", expand = True)
        self.title(APP_NAME+" Change Password")
        self.protocol("WM_DELETE_WINDOW", self.on_close)      
        def enter_press(event):
            self.update_password()
        self.bind('<Return>', enter_press)#allows pressing Enter to logon

    def update_password(self):
        oldpasswordvar = self.passwordChangeUI.oldpassword.get()
        newpasswordvar = self.passwordChangeUI.newpassword.get()
        confirmnewpasswordvar = self.passwordChangeUI.confirmnewpassword.get()
        if check_salt_password(CurrentProvider.Record['password'], oldpasswordvar) == True and newpasswordvar == confirmnewpasswordvar:
            employee_collection = MiniEMRMongo.db.employees
            hashed_salted_password = hash_salt_password(newpasswordvar)
            employee_collection.update_one(
                                    {'_id':CurrentProvider.Record['_id']},
                                    {'$set':{'password':hashed_salted_password}})
            self.hide()
            messagebox.showinfo("Updated Password","Password has been successfully changed.")
        else:
            messagebox.showerror("Update error","Incorrect password or new passwords do not match.")
            self.passwordChangeUI.clear()            

    def on_close(self):
        self.destroy()
    
    def show(self):
        super(UpdateCurrentProviderPassword, self).show()
        self.passwordChangeUI.clear()    