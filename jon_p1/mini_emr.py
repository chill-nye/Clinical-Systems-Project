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
from modINFO74000.emr_vitals import *

from datetime import datetime
from datetime import timedelta

from tk_html_widgets import HTMLLabel
DB_DATE_TIME_FORMAT="%Y-%m-%d"

class MainWindowFrame(tk.Frame):
        
    def updatePatientUI(self):
        
        def clear_space():
            self.frametest.fig.clear(True)



        patient=PatientList.current()
        patientSummary = ""
        DB_DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
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
                self.ordersListbox.insert('end', query_result["LOINC_NUM"]+': '+query_result["Shortname"].replace('"','')+', by '+query_result_doc['full_name']+', on '+ test["result"]["Time"])
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
        patientSummary += "</ul>"
        
        #vitals last updated data
        patientSummary+= '<br/><b><u>Last Vitals Values</u></b>:<ul>'
        self.updateVitalsUI()        
        LastMeasuredVitalStr=""
        for vt in self.vital_data_series:
            serieslength = len(self.vital_data_series[vt])
            if serieslength >0:
                idx=VITAL_TYPE_LIST.index(vt)
                LastVal = self.vital_data_series[vt][serieslength-1]
                LastMeasuredVitalStr += "<li>" + VITAL_TYPE_LABELS[idx]+ " " +str(LastVal["value"])+" measured on: " + LastVal["datetime"].strftime("%D-%H:%m:%S") + "</li>"
        patientSummary+= LastMeasuredVitalStr + '<ul>'
        patientSummary += "</ul>"

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

        vaccineData = ""
        vaccineData += '<b><u>Vaccination Information</u></b>:<ul>'
        try:
            if len(patient['vaccine_event']) > 0:
                for i in patient['vaccine_event']:
                    vaccineData += "Event Details:<ul>"
                    vaccineData += "<li>Vaccination Date: {}</li>".format(i['date_administered'])
                    vaccine_name = MiniEMRMongo.db.vaccines.find_one({"Control_Number":i['vaccine_id']})
                    vaccineData += "<li>Vaccine Type: {}</li>".format(vaccine_name['Brand_Name'])
                    vaccineData += "<li>Location: {}</li>".format(i['location'])
                    vaccineData += "<li>Dose: {}</li>".format(i['dose'])
                    vaccineData += "<li>Adverse?: {}</li>".format(i['adverse'])
        except:
            vaccineData += '<li>No vaccination data found</li>'
        self.vaccine_label.set_html(vaccineData)


    def updateVitalsUI(self):
        patient=PatientList.current()        
        self.summaryScrolledText.replace('1.0','end',patient["name"]+"\n")
        #Moved this from beneath the if statement
        self.vital_data_series={} #dictionary for compiling all vital measurement by type, in a data series  
        if 'vitals' in patient:
         

            self.summaryScrolledText.insert('end',"List vitals data by date/time:\n")
            #list all vitals by recording date      
            for vitals_object in patient['vitals']:   
                #dealing with datetime and author metadata
                record_date_time=datetime.strptime((vitals_object['datetime']),DATE_TIME_FORMAT)
            
                # using a list comprehension to filter only the vital types available in the object
                # note that the object contains the date time stamp and author field (they are NOT vital type data)        
                recorded_vital_types=[vt for vt in vitals_object if vt in VITAL_TYPE_LIST]
            
                for vt in recorded_vital_types:
                    idx=VITAL_TYPE_LIST.index(vt)
                    #initializes the vital data series dictionary  if needed
                    if not vt in self.vital_data_series: self.vital_data_series[vt]=[] 
                    #adds the vital type recording to the appropriate data series
                    self.vital_data_series[vt].append({"datetime":record_date_time,"value":vitals_object[vt]})
                    #adds vital record data to the output UI
                    self.summaryScrolledText.insert('end',VITAL_TYPE_LABELS[idx]+':'+str(vitals_object[vt])+'\n')
            
            #adds author and date time to the output UI
                self.summaryScrolledText.insert('end','Recorded by IEN='+str(vitals_object["AuthIEN"])+' on: '
                    +record_date_time.strftime(DATE_TIME_FORMAT)
                    +'\n------------------------------------\n')

            self.summaryScrolledText.insert('end',"List vitals data by type:\n")        
            #lists all vitals by vital type (data series)
            
            #for vt in VITAL_TYPE_LIST: <-- this created a bug
            #BUG description: iterating by all types in VITAL_TYPE_LIST was a bug
            #if a certain vital type was not in vital_data_series the code would fail
            #the fix was using if vt in vital_data_series, or better yet,
            #just iterate through the vital types that ARE in the vital_data_series object

            for vt in self.vital_data_series: #this is better, no more "if" statement needed!
                strVitalSeries=""
                for value in self.vital_data_series[vt]: 
                    strVitalSeries+=value["datetime"].strftime(DATE_TIME_FORMAT)+", value:"+str(value["value"])+'\n'          
                self.summaryScrolledText.insert('end',vt+'\n'+strVitalSeries+'\n')

            #here we list the last measured vitals. 
            LastMeasuredVitalStr=""
            for vt in self.vital_data_series:
                serieslength = len(self.vital_data_series[vt])
                if serieslength >0:
                    idx=VITAL_TYPE_LIST.index(vt)
                    LastVal = self.vital_data_series[vt][serieslength-1]
                    LastMeasuredVitalStr += VITAL_TYPE_LABELS[idx]+ " " +str(LastVal["value"])+" measured on: " + LastVal["datetime"].strftime("%Y%M%D%H%M%S") + "\n"
            self.summaryScrolledText.insert('end',"Last Measured Vitals:\n" + LastMeasuredVitalStr)


    def clear_vitalsUI(self):
        print('clearing the vitals UI')
        for c in self.frametest.winfo_children():
            c.pack_forget()

    def clearPatientUI(self):
        setLabelImage(self.patientPhotoLabel,None)
        self.html_lable.set_html("")
        self.patientNameLabel.configure(text="")
        self.openImageFileButton.configure(state="disabled")
        self.clear_vitalsUI()

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
        self.problemsListbox.pack(fill='both', expand=True)

        tab3 = ttk.Frame(tabControl)
        tabControl.add(tab3, text='Meds')
        self.medsListbox = Listbox(tab3)
        self.medsListbox.pack(fill="both", expand=True)

        tab4 = ttk.Frame(tabControl)
        tabControl.add(tab4, text='Orders')
        self.ordersListbox = Listbox(tab4)
        self.ordersListbox.pack(fill="both", expand=True)

        tab6 = ttk.Frame(tabControl)
        tabControl.add(tab6, text='Reports')
        self.adminListbox = Listbox(tab6)
        self.adminListbox.pack(fill="both", expand=True)

        tab7 = ttk.Frame(tabControl)
        tabControl.add(tab7, text='VitalsReport')
        self.summaryScrolledText = scrolledtext.ScrolledText(tab7)
        self.summaryScrolledText.pack(fill="both", expand=True)

        tab8 = ttk.Frame(tabControl)
        tabControl.add(tab8, text='Vaccination Record')
        self.vaccine_label = HTMLLabel(tab8)
        self.vaccine_label.pack(fill="both", expand=True)
        self.vaccine_label.fit_height()

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

        def addNewPatientFn():
            self.addpatient_win=AddNewPatient(master=self)
            self.addpatient_win.show()

        def EditPatientFn():
            self.editpatient_win=EditPatient(master=self)
            self.editpatient_win.show()

        def recordVitalsTab():
            def refreshPatientListAndUpdateUICallback():
                PatientList.refresh()
                self.main_frame.updatePatientUI()

          #before creating the vitals record dialog, I must figure out current provider IEN
            if NO_LOGON_TESTING: 
                currentProviderIEN=DEFAULT_AUTH_IEN
            else: 
                currentProviderIEN=CurrentProvider.Record["IEN"]

            vitals_win=VitalsWriteDialog(master=self,
                patient=PatientList.current(), #current patient object
                providerIEN=currentProviderIEN,  #logged on provider IEN
                callback=refreshPatientListAndUpdateUICallback) #callback for refreshing patient data and updating UI 

            vitals_win.show()       
            
        def vitals_graph():
            self.vg_win = VitalsGraphing(master=self)
            self.vg_win.show()

        def vaccinateFn():
            self.vaccine_win=OrderVaccine(master=self)
            self.vaccine_win.show()       

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
        viewMenu.add_command(label="Add new patient", command=addNewPatientFn)
        viewMenu.add_command(label="Edit patient", command=EditPatientFn)
        viewMenu.add_command(label="Select patient", command=selectPatient)

        #tools menu
        toolsMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="Tools", menu=toolsMenu)    
        toolsMenu.add_command(label="Change Password", command=changePassword)
        toolsMenu.add_command(label="Order Vaccine", command=vaccinateFn)                
        toolsMenu.add_command(label="Record New Vitals", command=recordVitalsTab)
        toolsMenu.add_command(label="Graph Vitals", command=vitals_graph)            
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
            #what to put here?
            PatientList.selectPatientByMRN(MRN)
            #maybe here you have to do something to update the UI with the current patient?
            self.main_frame.updatePatientUI()


        def onIENBarcodeRead(IEN):
            print("employee IEN scanned:",IEN)
            #updated Mar 18, 2020
            if CurrentProvider.Record!=None:
                if IEN==CurrentProvider.Record['IEN']:
                    messagebox.showinfo( APP_NAME,'Employee badge scanned as '+CurrentProvider.Record['full_name'])
                    logoutUser()
                else:
                    logoutUser()
            #lookup username - some already implemented this as getProviderByIEN()
            employeeRecord=MiniEMRMongo.db.employees.find_one({"IEN":IEN})            
            if employeeRecord!=None and 'username' in employeeRecord:
                self.login_win.loginUIFrame.UserNameTextBox.insert('end',employeeRecord["username"])
                self.login_win.loginUIFrame.PasswordTextBox.focus()
            else:
                print('no employee found in database')
                self.login_win.loginUIFrame.UserNameTextBox.focus()
                

        def onDINBarcodeRead(DIN):
            print("drug DIN scanned:",DIN)
            patient=PatientList.current()
            drug_order=None
            if 'orders' in patient and 'medications' in patient['orders']:
                for med in patient['orders']['medications']:
                    #assume DIN field exists in the drug order or else it blows up
                    if med['DIN']==DIN:
                        drug_order=med
                        break
            
            drug_info=MiniEMRMongo.db.drug_formulary.find_one({"DIN":DIN})            
            if not drug_info:
                messagebox.showerror(title="Drug barcode scan error ",message="Drug with DIN: {0} not found in the database".format(DIN))
            else:
                if drug_order:
                    if messagebox.askokcancel(title="Confirm administration",message="{0}, dose:{1} is to be administered to {2}, MRN{3}".format(\
                        drug_info['TRADENAME'],drug_order['Freq'], patient['name'],patient['id'])):
                        #add administration record to patient record
                        from datetime import datetime
                        current_dt_iso=datetime.utcnow()
                        drug_admin_info= {
                                "DIN":          DIN,
                                "ProviderIEN":  CurrentProvider.Record['IEN'],
                                "patientMRN":   patient["id"],
                                "Time":         current_dt_iso.isoformat()+'Z'
                                }
                        drug_order_index=patient['orders']['medications'].index(drug_order)
                        PatientList.updateCurrentPatientDrugAdministrationRecord(drug_order_index,drug_admin_info)
                else:
                    messagebox.showwarning(title="Do NOT give!",message="{0} is not in the list of medications for {1}, MRN:{2}".format(\
                        drug_info['TRADENAME'], patient['name'], patient['id']))
                    #add administration attempt to patient record or to some log for audit, analysis, etc?
                #since database was updated, a patient list refresh and UI update are necessary
                PatientList.refresh()
                self.main_frame.updatePatientUI()

        def onLOINBarcodeRead(LOINC):
            print("test LOINC scanned:",LOINC)
            patient=PatientList.current()

            LOINC_info=MiniEMRMongo.db.loinc.find_one({"LOINC_NUM":LOINC})

            if not LOINC_info:
                messagebox.showerror(title="Test barcode scan error ",message="Test with LOINC: {0} not found in the database".format(LOINC))
            else:
                if LOINC_info:
                    if messagebox.askokcancel(title="Confirm test order",message="{0}, has been ordered to {1}, MRN{2}".format(\
                        LOINC_info['Shortname'], patient['name'], patient['id'])):
                        #add administration record to patient record
                        from datetime import datetime
                        current_dt_iso=datetime.utcnow()
                        test_admin_info = {
                                "LOINC_NUM":    LOINC,
                                "ProviderIEN":  CurrentProvider.Record['IEN'],
                                "patientMRN":   str(patient['id']), 
                                "result":      {"value": "Positive", "Time": current_dt_iso.isoformat()+'Z'}
                                }
                        print(test_admin_info)
                        PatientList.updateCurrentPatientTestRecord(test_admin_info)
                else:
                    messagebox.showwarning(title="Confirm test order",message="{0}, has been ordered to {1}, MRN{2}".format(\
                        LOINC_info['Shortname'], patient['name'], patient['id']))

                #since database was updated, a patient list refresh and UI update are necessary
                PatientList.refresh()
                self.main_frame.updatePatientUI()  

        self.bScanner=BarcodeScanner(self,onMRNBarcodeRead,onIENBarcodeRead,onDINBarcodeRead,onLOINBarcodeRead)
    
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

if NO_LOGON_TESTING:
    #must have default provider, when no logon testing, or drug admin and vital recording will crash
    CurrentProvider.Record=MiniEMRMongo.db.employees.find_one({'IEN':'80'})

#retrieves the list of patients
PatientList.refresh()

main_win.mainloop()
#disconnect from mongodb after main loop finishes
MiniEMRMongo.disconnect()