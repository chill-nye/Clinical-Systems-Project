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
import datetime
from datetime import datetime

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

class MainWindowFrame(tk.Frame):

    def updatePatientUI(self):
        patient=PatientList.current()
        patient_summary_string=''

        #dob Formatting
        formatted_DOB = datetime.strptime(patient['dob'],"%Y-%m-%dT%H:%M:%S.%fZ")
        for_DOB = datetime.strftime(formatted_DOB, "%Y-%m-%d")
        ageInYears=(datetime.now().year - formatted_DOB.year)
        
        self.patientNameLabel.configure(text=patient['name']+ 
                                            '\nGender: '+patient['gender']+ 
                                            "\nDOB: "+for_DOB+" ("+str(ageInYears) + ")"+
                                            "\nEmail: " + patient['contact']['eMail']+
                                            "\nAddress: " + patient['contact']['address']['street'] + ", "+ patient['contact']['address']['city']+
                                            "\nCell Number: " + patient['contact']['cell']+
                                            "\nTelephone Number: " + patient['contact']['telephone'] +
                                            "\nAllergies: " + str(patient['allergies']).replace('[','').replace(']','').replace('\'',''))

        self.openImageFileButton.configure(state="enabled")
        #patient object is a dictionary
        #to test value can use:
        if 'photo' in patient:
            setLabelImage(self.patientPhotoLabel,patient["photo"])
        else: setLabelImage(self.patientPhotoLabel,None)
        
        #list providers
        patient_summary_string+="Providers:\n"
        if "providers" in patient:
            for prov in patient["providers"]:
                empl_rec= getEmployeeRecordByIEN(prov["IEN"])
                patient_summary_string+='   '+empl_rec["full_name"]+", " +prov["type"]+"\n"
            patient_summary_string+="\n"


        #list problems
        self.problemsListbox.delete(0,self.problemsListbox.size()-1)
        patient_summary_string+="Problems:\n"
        if "problem_list" in patient:
            for prob in patient["problem_list"]:
                query_result=MiniEMRMongo.db.ICD10.find_one({'code': prob['code']})
                if (query_result == None):
                    self.problemsListbox.insert('end', prob['code'])
                else:
                    self.problemsListbox.insert('end',"ICD10 Code: " + query_result["code"]+ " Desc: " +query_result["desc"])
                    patient_summary_string+="    "+query_result["desc"]+"\n"
            patient_summary_string+="\n"

        #list meds
        self.medsListbox.delete(0,self.medsListbox.size()-1)
        patient_summary_string+="Medications:\n"
        if "orders" in patient:
            if "medications" in patient["orders"]:
                for med in patient["orders"]["medications"]:
                    query_result=MiniEMRMongo.db.drug_formulary.find_one({'DIN': med['DIN']})
                    if (query_result == None):
                        self.medsListbox.insert('end', med['DIN'])
                    else:
                        self.medsListbox.insert('end',"DIN: " + query_result["DIN"]+ " Desc: " +query_result["TRADENAME"].replace("&amp;", '&'))
                        patient_summary_string+="    "+ query_result["TRADENAME"].replace("&amp;", '&') +"\n" 
                patient_summary_string+="\n"        
       
        #list Lab orders
        self.LabsListbox.delete(0,self.LabsListbox.size()-1)
        patient_summary_string+="Labs: \n" 
        if "orders" in patient:
            if "tests" in patient["orders"]:
                for lab in patient["orders"]["tests"]:
                    query_result=MiniEMRMongo.db.labs.find_one({'LOINC_NUM': lab['LOINC_NUM']})
                    if (query_result == None):
                        self.LabsListbox.insert('end', lab['LOINC_NUM'])
                    else:
                        self.LabsListbox.insert('end',"LOINC: " + query_result["LOINC_NUM"]+ " Desc: " +query_result["Shortname"].replace("\"", ''))
                        patient_summary_string+="    "+query_result["Shortname"].replace("\"", '') +"\n" 
                patient_summary_string+="\n"  

        #do other things, like show records components in other tabs objects
        self.summaryScrolledText.replace('1.0','end',patient_summary_string)

    def clearPatientUI(self):
        setLabelImage(self.patientPhotoLabel,None)
        self.summaryScrolledText.delete('1.0','end')
        self.patientNameLabel.configure(text="")
        self.openImageFileButton.configure(state="disabled")

    def openImageFileDialog(self):
        filename=filedialog.askopenfilename(initialdir= ".",title ="Open file",
            filetypes = (("png file","*.png"),("any file","*.*")))
        print("File selected:",filename)
        setLabelImage(self.patientPhotoLabel,filename)
        if filename!=():
            PatientList.updateCurrentPatientPhoto(filename)
            self.summaryScrolledText.replace('1.0','end',PatientList.current())

    def debugMsg(self,msg):
        self.debugScrolledText.insert('end',"Test debug message")

    def createWidgets(self):
        #top banner
        self.topBannerFrame=tk.Frame(self.master)
        self.topBannerFrame.pack(side="top", expand=0,fill="x")
        #photo label
        self.patientPhotoLabel=ttk.Label(self.topBannerFrame, text="?")
        setLabelImage(self.patientPhotoLabel,None)
        self.patientPhotoLabel.grid(column=0,row=0,rowspan=3,sticky='w')
        #photo label image select button
        self.openImageFileButton = ttk.Button(self.topBannerFrame, state="disabled", text="Photo...", command=self.openImageFileDialog)
        self.openImageFileButton.grid(column=0,row=3)
        #patient name label
        self.patientNameLabel = ttk.Label(self.topBannerFrame, text="")
        self.patientNameLabel.grid(column=1,row=1)
        #Patient DOB label
        self.patientDOBLabel = ttk.Label(self.topBannerFrame, text="")
        self.patientDOBLabel.grid(column=1,row=2)

        #tab controls
        tabControl = ttk.Notebook(self.master)

        #summary tab and scrolled text control
        tab1 = ttk.Frame(tabControl)
        tabControl.add(tab1, text='Summary')
        self.summaryScrolledText = scrolledtext.ScrolledText(tab1, wrap=tk.WORD)
        self.summaryScrolledText.pack(fill='both', side='left', expand=True)
        #rest of tabs
        tab2 = ttk.Frame(tabControl)
        tabControl.add(tab2, text='Problems')
        self.problemsListbox = Listbox(tab2)
        self.problemsListbox.config(width=80,height=20)        
        self.problemsListbox.pack(fill = 'both', expand=True)  

        tab3 = ttk.Frame(tabControl)
        tabControl.add(tab3, text='Meds')
        self.medsListbox = Listbox(tab3)
        self.medsListbox.config(width=80,height=20)
        self.medsListbox.pack(fill = 'both', expand=True)  

        tab4 = ttk.Frame(tabControl)
        tabControl.add(tab4, text='Orders')        
        tab5 = ttk.Frame(tabControl)
        tabControl.add(tab5, text='Notes')        
        tab6 = ttk.Frame(tabControl)
        tabControl.add(tab6, text='Consults')        
        tab7 = ttk.Frame(tabControl)
        tabControl.add(tab7, text='D/C Summ')        
        tab8 = ttk.Frame(tabControl)

        tabControl.add(tab8, text='Labs')
        self.LabsListbox = Listbox(tab8)
        self.LabsListbox.config(width=80,height=20)
        self.LabsListbox.pack(fill = 'both', expand=True)       
        tab9 = ttk.Frame(tabControl)

        tabControl.add(tab9, text='Reports')

        # debug tab and scrolled Text control
        tab10 = ttk.Frame(tabControl)
        tabControl.add(tab10, text='DEBUG')
        self.debugScrolledText = scrolledtext.ScrolledText(tab10, wrap=tk.WORD)#width=scrolW, height=scrolH,
        self.debugScrolledText.pack(fill='both', side='left', expand=True)
        self.debugMsg("This is a test debug message")

        tabControl.pack(expand=1, fill="both")

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

class MainWindow(tk.Tk):

    def createWidgets(self):
        menuBar = Menu(self.master)
        self.config(menu=menuBar)
        fileMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="File", underline=0, menu=fileMenu)

        def selectPatient():
            patient_select_win=PatientSelectDialog(master=self,callback=self.main_frame.updatePatientUI)
            patient_select_win.show()  
        #patient select menu
        fileMenu.add_command(label="Select patient...", command=selectPatient)
            
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
            #annoying....
            #answer = messagebox.askyesno("Exit "+APP_NAME, "Are you sure you want to quit?")
            #print(answer)
            #if answer==True: 
                self.quit()
        #exit menu
        fileMenu.add_command(label="Exit", command=exitMenuSelected)
        
        viewMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="View", menu=viewMenu)    

        toolsMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="Tools", menu=toolsMenu)    
                
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
            #put some code in here that selects patient whose MRN was scanned
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
        #hiding main window DOES NOT WORK ON WINDOWS!        
        if not NO_LOGON_TESTING:
            self.login_win=LoginWindowDialog(master=self)
            self.login_win.show()    


main_win = MainWindow()
#connect to mongodb just before main loop
MiniEMRMongo.connect()

#retrieves the list of patients
PatientList.refresh()

#retrieves the list of Drugs
MedList.refresh()

#retrieves the list of Labs
LabList.refresh()

main_win.mainloop()
#disconnect from mongodb after main loop finishes
MiniEMRMongo.disconnect()


