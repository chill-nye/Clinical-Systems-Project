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
from tkinter import filedialog
from tkinter import Menu
from tkinter import scrolledtext

from modINFO74000.emr_db import MiniEMRMongo
from modINFO74000.emr_misc_ui import *
from modINFO74000.emr_provider import *
from modINFO74000.emr_patient import *
from modINFO74000.emr_const import *
from modINFO74000.emr_automation import BarcodeScanner

from datetime import datetime
from datetime import timedelta

from tk_html_widgets import HTMLLabel

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

DB_DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

class MainWindowFrame(tk.Frame):
    def updatePatientUI(self):
        patient=PatientList.current()
        patientSummary = ""

        #dob
        dob = datetime.strptime(patient['dob'], DB_DATE_TIME_FORMAT)
        age_years = (datetime.today()-dob)//timedelta(days=365.2425)

        #contact information
        patientSummary += "<b><u>Contact Information</u></b>:<ul>"
        if len(patient['contact']['person']['name']) > 0:
            patientSummary += "Emergency Contact:<ul>"
            patientSummary += "<li>Name: {}</li>".format(patient['contact']['person']['name'])
            patientSummary += "<li>Relation: {}</li>".format(patient['contact']['person']['relation'])
            patientSummary += "<li>Phone: {}</li>".format(patient['contact']['person']['phone'])
        else:
            patientSummary += '<li>No contact information available.</li>'
        patientSummary += "</ul>"

        #contact email
        if len(patient['contact']['eMail']) > 0:
            patientSummary += "Email: {}".format(patient['contact']['eMail'])
        else:
            patientSummary += "<li>No email address found.</li>"

        #address
        patientSummary += "<br/>Address: {}".format(patient['contact']['address']['street'], patient['contact']['address']['city']) 

        #phone 
        if len(patient['contact']['telephone']) > 0:
            patientSummary += "<br/>Telephone: {}".format(patient['contact']['telephone'])
        else:
            patientSummary += "<li>No telephone number listed</li>"
        if len(patient['contact']['cell']) > 0:
            patientSummary += "<br/>Cell: {}".format(patient['contact']['cell'])
        else:
            patientSummary += "<li>No cell number listed</li>"
        patientSummary += "</ul>"

        #allergies
        patientSummary += "<b><u>Allergies</u></b>:<ul>"
        if len(patient['allergies']) > 0:
            for i in patient['allergies']:
                patientSummary += '<li>{}</li>'.format(i)
        else:
            patientSummary += '<li>No known allergies</li>'
        patientSummary += "</ul>"

        #medications + populate Meds tab
        patientSummary += '<b><u>Medications</u></b>:<ul>'
        self.medsListbox.delete(0,self.medsListbox.size()-1)
        if len(patient['orders']['medications']) > 0:
            for med in patient['orders']['medications']:
                query_result=MiniEMRMongo.db.drug_formulary.find_one({'DIN': med['DIN']})
                self.medsListbox.insert('end', query_result["DIN"]+': '+query_result["TRADENAME"].replace("    ","") + ", Dose: "+ med["Freq"]) 
                patientSummary += '<li>{}</li>'.format(query_result['TRADENAME'].replace("    ",""))
        else:
            orders_meds = '<li>No current medications found</li>'
        patientSummary += "</ul>"

        #lab tests + populate Orders tab
        patientSummary += '<b><u>Lab Tests</u></b>:<ul>'
        self.ordersListbox.delete(0,self.ordersListbox.size()-1)
        if len(patient['orders']['tests']) > 0:
            for test in patient["orders"]["tests"]:
                query_result=MiniEMRMongo.db.loinc.find_one({'LOINC_NUM': test['LOINC_NUM']})
                query_result_doc=MiniEMRMongo.db.employees.find_one({'IEN': test['ProviderIEN']})
                self.ordersListbox.insert('end', query_result["Shortname"]+', '+query_result["LOINC_NUM"]+', by '+query_result_doc['full_name']+', on '+ test["result"]["Time"])
                patientSummary += '<li>{}</li>'.format(query_result['Shortname'])
        else:
            orders_labs = '<li>No current labs found</li>'
        patientSummary += "</ul>"

        #problems + populate Problems tab
        patientSummary+="<br/><b><u>Problems</u></b>:<ul>"
        self.problemsListbox.delete(0,self.problemsListbox.size()-1)
        if"problems" in patient:
            for prob in patient["problems"]:                
                query_result=MiniEMRMongo.db.icd10.find_one({"code":prob["ICD10code"]})
                if (query_result==None):
                    self.problemsListbox.insert('end',prob["ICD10code"])
                else:
                    self.problemsListbox.insert('end',query_result["desc"])                    
                    patientSummary+="<li>"+query_result["desc"]+"</li>"        

        #administration + popoulate Report tab
        patientSummary += '<br/><b><u>Administration Events</u></b>:<ul>'
        self.adminListbox.delete(0,self.adminListbox.size()-1)
        if len(patient['orders']['administration']) > 0:
            for i in patient['orders']['administration']:
                query_result_med=MiniEMRMongo.db.drug_formulary.find_one({'DIN': i['DIN']})
                query_result_doc=MiniEMRMongo.db.employees.find_one({'IEN': i['ProviderIEN']})
                self.adminListbox.insert('end', query_result_med["TRADENAME"].replace("     ","")+', by '+query_result_doc["full_name"]+', on '+i["Time"]) 
                patientSummary += '<li>{}</li>'.format(query_result_med["TRADENAME"])
        else:
            orders_meds = '<li>No current medications found</li>'
        patientSummary += "</ul>"

        self.html_lable.set_html(patientSummary)

        self.patientNameLabel.configure(text='Patient ID: '+str(patient['id'])+'\nName: '+patient['name']+'\nGender: '+patient['gender']+'\nDOB: '+dob.strftime("%Y-%m-%d")+' ('+str(age_years)+' years old)')
        self.openImageFileButton.configure(state="enabled")
        #patient object is a dictionary
        #to test value can use:
        if 'photo' in patient:
            setLabelImage(self.patientPhotoLabel,patient["photo"])
        else: setLabelImage(self.patientPhotoLabel,None)
        #list meds
        # self.medsListbox.delete(0,self.medsListbox.size()-1)
        # for med in patient["orders"]["medications"]:
        #     self.medsListbox.insert('end', med["TRADENAME"]+', '+med["DIN"])

        f = Figure(figsize=(5,5), dpi=100)
        a = f.add_subplot(111)
        x = []
        y = []
        for i in patient['vitals']:
            if i['type'] == 'BP':
                x.append(i['dtf'])
                y.append(int(i['value']['sys']))
        a.plot(x,y)

        canvas = FigureCanvasTkAgg(f, self.frametest)
        canvas.get_tk_widget().pack(expand=True)
        canvas.draw()

        # reports = ""

        # reports += "<b><u>Administration Events</u></b>:<ul>"
        # if len(patient['orders']['administration']) > 0:
        #     for i in patient['orders']['administration']:
        #         query_result=MiniEMRMongo.db.drug_formulary.find_one({'DIN': i['DIN']})
        #         reports += '<li>Drug: {}, by {}, on {}</li>'.format(query_result['TRADENAME'], i['ProviderIEN'], i['Time'])
        # else:
        #     orders_meds = '<li>No administration events found</li>'
        # reports += "</ul>"

        # self.reportsHTML.set_html(reports)


    def clearPatientUI(self):
        setLabelImage(self.patientPhotoLabel,None)
        self.html_lable.set_html("")
        self.patientNameLabel.configure(text="")
        self.openImageFileButton.configure(state="disabled")

    def openImageFileDialog(self):
        filename=filedialog.askopenfilename(initialdir= ".",title ="Open file",
            filetypes = (("png file","*.png"),("any file","*.*")))
        print("File selected:",filename)
        setLabelImage(self.patientPhotoLabel,filename)
        if filename!=():
            PatientList.updateCurrentPatientPhoto(filename)

    def createWidgets(self):
        #top banner
        self.topBannerFrame=tk.Frame(self.master)
        self.topBannerFrame.pack(side="top", expand=0,fill="x")
        self.topBannerFrame.configure(bg="#24d9f8")

        #photo label
        self.patientPhotoLabel=ttk.Label(self.topBannerFrame, text="?")
        setLabelImage(self.patientPhotoLabel,None)
        self.patientPhotoLabel.grid(column=0,row=0,rowspan=3,sticky='w')

        #photo label image select button
        self.openImageFileButton = ttk.Button(self.topBannerFrame, state="disabled", text="Upload Photo", command=self.openImageFileDialog)
        self.openImageFileButton.grid(column=0,row=3)

        #patient name label
        self.patientNameLabel = ttk.Label(self.topBannerFrame, text="")
        self.patientNameLabel.grid(column=1,row=1)

        #tab controls
        tabControl = ttk.Notebook(self.master)

        #summary tab and scrolled text control
        tab1 = ttk.Frame(tabControl)
        tabControl.add(tab1, text='Summary')
        self.html_lable = HTMLLabel(tab1)
        self.html_lable.pack(fill="both", expand=True)
        self.html_lable.fit_height()

        #rest of tabs
        tab2 = ttk.Frame(tabControl)
        tabControl.add(tab2, text='Problems')
        self.problemsListbox = Listbox(tab2)
        self.problemsListbox.pack(expand=True)

        tab3 = ttk.Frame(tabControl)
        tabControl.add(tab3, text='Meds')
        self.medsListbox = Listbox(tab3)
        self.medsListbox.pack(fill="both", expand=True)

        tab4 = ttk.Frame(tabControl)
        tabControl.add(tab4, text='Orders')
        self.ordersListbox = Listbox(tab4)
        self.ordersListbox.pack(fill="both", expand=True)

        tab5 = ttk.Frame(tabControl)
        tabControl.add(tab5, text='Vitals')
        self.frametest = tk.Frame(tab5)
        self.frametest.pack(fill="both", expand=True)

        tab6 = ttk.Frame(tabControl)
        tabControl.add(tab6, text='Reports')
        self.adminListbox = Listbox(tab6)
        self.adminListbox.pack(fill="both", expand=True)

        # tab6 = ttk.Frame(tabControl)
        # tabControl.add(tab6, text='Reports')
        # self.reportsHTML = HTMLLabel(tab6)
        # self.reportsHTML.pack(fill="both", expand=True)
        # self.reportsHTML.fit_height()

        tabControl.pack(expand=1, fill="both")

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

class MainWindow(tk.Tk):
    def createWidgets(self):
        menuBar = Menu(self.master)
        self.config(menu=menuBar)
        self.configure(bg="black")
        fileMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="File", underline=0, menu=fileMenu)

        def changePassword():
            self.password_win=UpdateCurrentProviderPassword(master=self)
            self.password_win.show()

        def selectPatient():
            patient_select_win=PatientSelectDialog(master=self,callback=self.main_frame.updatePatientUI)
            patient_select_win.show()
            
        def logoutUser():
            self.title(APP_NAME+" (logged out)")
            #may want to clear/reset all UIs elements
            self.main_frame.clearPatientUI()
            CurrentProvider.logout()
            PatientList.clearCurrentSelection()
            self.login_win.show()
        
        #logout menu
        if not NO_LOGON_TESTING:
            fileMenu.add_command(label="Log out", underline=0, command=logoutUser)

        fileMenu.add_separator()

        def exitMenuSelected():
                self.quit()
        #exit menu
        fileMenu.add_command(label="Exit", command=exitMenuSelected)
        
        viewMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="View", menu=viewMenu)    
        #patient select menu
        viewMenu.add_command(label="Select patient", command=selectPatient)
        viewMenu.add_command(label="Add new patient", command=selectPatient)

        toolsMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="Tools", menu=toolsMenu)    
        toolsMenu.add_command(label="Change Password", command=changePassword)
                
        helpMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="Help", menu=helpMenu)    

        def aboutMenuSelected():
            messagebox.showinfo('About', APP_NAME+' application prototype\n 2019, Stefan V. Pantazi, MD, PhD')

        helpMenu.add_command(label="About", command=aboutMenuSelected)
        
        def licenseMenuSelected():
            lic_win=LicenseWindow(master=self)
            lic_win.show()    

        helpMenu.add_command(label="License", command=licenseMenuSelected)

        self.main_frame = MainWindowFrame(master=self)
        xpos=self.winfo_screenwidth() // 2 - MAIN_WIN_WIDTH // 2 
        ypos=self.winfo_screenheight() // 2 - MAIN_WIN_HEIGHT // 2 
        self.geometry(str(MAIN_WIN_WIDTH)+'x'+str(MAIN_WIN_HEIGHT)+'+'+str(xpos)+'+'+str(ypos))      

        #setting up barcode scanner
        def onMRNBarcodeRead(MRN):
            print("patient MRN scanned:",MRN)
            PatientList.selectPatientByMRN(MRN)
            self.main_frame.updatePatientUI()
            
        def onIENBarcodeRead(IEN):
            print("employee IEN scanned:",IEN)
            if CurrentProvider.Record['IEN']!=IEN:
                logoutUser()
            
            providerRecord = getEmployeeRecordByIEN(IEN)
            if providerRecord!=None:

                provider_username = providerRecord['username']
                print(provider_username)
                #We need to do code that will target the username box and insert the scanned IENs username
                self.login_win.loginUIFrame.UserNameTextBox.insert("end",provider_username)
                self.login_win.loginUIFrame.PasswordTextBox.focus()

        def onDINBarcodeRead(DIN):
            print("drug DIN scanned:",DIN)
            MedList.findDrugbyDIN(DIN)
            record_query_result = MiniEMRMongo.db.drug_formulary.find_one({'DIN': (DIN)})
            if record_query_result == None:
                messagebox.showinfo('ERROR',' The scanned medication is not in the system\nDO NOT ADMINISTER')

            else:
                print("drug scanned; DIN:", MedList.current()["DIN"] , ' TRADENAME: ' , MedList.current()["TRADENAME"])
                if "medications" in PatientList.current()["orders"]:
                    is_in_list = False
                    for med in PatientList.current()["orders"]["medications"]:
                        if med["DIN"] == DIN:
                            messagebox.showinfo('Alert', ' This Medication is in the patient\'s current medication list')
                            is_in_list = True
                            # add administration recording with date + time and IEN
                            break
                        else:
                            continue
                    if is_in_list == False:
                        messagebox.showinfo('Critical Alert',' The scanned medication is not prescribed to the current patient\nDO NOT ADMINISTER')
        
        self.bScanner=BarcodeScanner(self,onMRNBarcodeRead,onIENBarcodeRead,onDINBarcodeRead)
    
    def __init__(self):
        tk.Tk.__init__(self,None)
        self.title(APP_NAME)
        self.createWidgets()
        if not NO_LOGON_TESTING:
            self.login_win=LoginWindowDialog(master=self)
            self.login_win.show() 

main_win = MainWindow()
#connect to mongodb just before main loop
MiniEMRMongo.connect()

#retrieves the list of patients
PatientList.refresh()

main_win.mainloop()
#disconnect from mongodb after main loop finishes
MiniEMRMongo.disconnect()
