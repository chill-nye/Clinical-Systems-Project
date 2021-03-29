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

DB_DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

class SampleApp(tk.Tk):
    def createWidgets(self):
        menuBar = Menu(self.master)
        self.config(menu=menuBar)
        fileMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="File", underline=0, menu=fileMenu)

        def refresh():
            self.main_frame.updateEmployeeUI()

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
        viewMenu.add_command(label="Select patient", command=selectPatient)    

        toolsMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="Tools", menu=toolsMenu)
        toolsMenu.add_command(label="Refresh", command=refresh)
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
        
        self.main_frame = StartPage(master=self)
        xpos=self.winfo_screenwidth() // 2 - MAIN_WIN_WIDTH // 2 
        ypos=self.winfo_screenheight() // 2 - MAIN_WIN_HEIGHT // 2 
        self.geometry(str(MAIN_WIN_WIDTH)+'x'+str(MAIN_WIN_HEIGHT)+'+'+str(xpos)+'+'+str(ypos)) 

    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(StartPage, StartPage)
        self.createWidgets()
        if not NO_LOGON_TESTING:
            self.login_win=LoginWindowDialog(master=self)
            self.login_win.show() 

    def switch_frame(self, frame_class, old_frame):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        old_frame = old_frame(self)
        if self._frame is not None:
            self._frame.destroy()
            for widget in old_frame.winfo_children():
                widget.place_forget()
        self._frame = new_frame
        self._frame.pack()

class StartPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Welcome. Please choose an option:").pack(side="top", fill="x", pady=10)
        tk.Button(self, text="Manage patients",
                  command=lambda: master.switch_frame(MainWindowFrame, StartPage)).pack()
        tk.Button(self, text="Edit profile",
                  command=lambda: master.switch_frame(LandingPageFrame, StartPage)).pack()

class MainWindowFrame(tk.Frame):
    def updatePatientUI(self):
        patient=PatientList.current()

        patientSummary = ""

        #dob
        dob = datetime.strptime(patient['dob'], DB_DATE_TIME_FORMAT)
        age_years = (datetime.today()-dob)//timedelta(days=365.2425)

        #contact information
        patientSummary += "<b><u>Contact Information</u></b>:<ul>"
        if len(patient['contact']['knows']) > 0:
            patientSummary += "Emergency Contact(s):<ul>"
            for i in patient['contact']['knows']:
                patientSummary += "<li>{}</li>".format(i)
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

        patientSummary += "<b><u>Allergies</u></b>:<ul>"
        if len(patient['allergies']) > 0:
            for i in patient['allergies']:
                patientSummary += '<li>{}</li>'.format(i)
        else:
            patientSummary += '<li>No known allergies</li>'
        patientSummary += "</ul>"

        patientSummary += '<b><u>Medications</u></b>:<ul>'
        self.medsListbox.delete(0,self.medsListbox.size()-1)
        if len(patient['orders']['medications']) > 0:
            for i in patient['orders']['medications']:
                self.medsListbox.insert('end', i["drug"]+', '+i["dose"]) 
                patientSummary += '<li>{}</li>'.format(i['drug'])
        else:
            orders_meds = '<li>No current medications found</li>'
        patientSummary += "</ul>"
        
        orders_tests = ''
        if len(patient['orders']['tests']) > 0:
            for i in range(len(patient['orders']['tests'])):
                if i == len(patient['orders']['tests'])-1:
                    orders_tests += '{}'.format(patient['orders']['tests'][i])
                else:
                    orders_tests += '{}\n'.format(patient['orders']['tests'][i])
        else:
            orders_tests = 'No current tests'

        patientSummary+="<br/><b><u>Problems</u></b>:<ul>"
        self.problemsListbox.delete(0,self.problemsListbox.size()-1)
        if"problem_list" in patient:
            for prob in patient["problem_list"]:                
                query_result=MiniEMRMongo.db.icd10.find_one({"ICD10code":prob["ICD10code"]})
                if (query_result==None):
                    self.problemsListbox.insert('end',prob["ICD10code"])                    
                else:
                    self.problemsListbox.insert('end',query_result["description"])                    
                    patientSummary+="<li>"+query_result["description"]+"</li>"        

        self.html_lable.set_html(patientSummary)

        self.patientNameLabel.configure(text='Patient ID: '+str(patient['id'])+'\nName: '+patient['name']+'\nGender: '+patient['gender']+'\nDOB: '+dob.strftime("%Y-%m-%d")+' ('+str(age_years)+' years old)')
        self.openImageFileButton.configure(state="enabled")
        #patient object is a dictionary
        #to test value can use:
        if 'photo' in patient:
            setLabelImage(self.patientPhotoLabel,patient["photo"])
        else: setLabelImage(self.patientPhotoLabel,None)
        #list meds
        self.medsListbox.delete(0,self.medsListbox.size()-1)
        for med in patient["orders"]["medications"]:
            self.medsListbox.insert('end', med["drug"]+', '+med["dose"])

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
        self.problemsListbox.pack()

        tab3 = ttk.Frame(tabControl)
        tabControl.add(tab3, text='Meds')
        self.medsListbox = Listbox(tab3)
        self.medsListbox.pack()

        tab4 = ttk.Frame(tabControl)
        tabControl.add(tab4, text='Orders')
        self.ordersListbox = Listbox(tab4)
        self.ordersListbox.pack()

        tab5 = ttk.Frame(tabControl)
        tabControl.add(tab5, text='Notes')
        self.notesHTML = HTMLLabel(tab5)
        self.notesHTML.pack(fill="both", expand=True)
        self.notesHTML.fit_height()

        tab6 = ttk.Frame(tabControl)
        tabControl.add(tab6, text='Consults')
        self.consultsHTML = HTMLLabel(tab6)
        self.consultsHTML.pack(fill="both", expand=True)
        self.consultsHTML.fit_height()

        tab7 = ttk.Frame(tabControl)
        tabControl.add(tab7, text='D/C Summ')
        self.dischargeHTML = HTMLLabel(tab7)
        self.dischargeHTML.pack(fill="both", expand=True)
        self.dischargeHTML.fit_height()

        tab8 = ttk.Frame(tabControl)
        tabControl.add(tab8, text='Labs')
        self.labsHTML = HTMLLabel(tab8)
        self.labsHTML.pack(fill="both", expand=True)
        self.labsHTML.fit_height()

        tab9 = ttk.Frame(tabControl)
        tabControl.add(tab9, text='Reports')
        self.reportsHTML = HTMLLabel(tab9)
        self.reportsHTML.pack(fill="both", expand=True)
        self.reportsHTML.fit_height()

        # debug tab and scrolled Text control
        tab10 = ttk.Frame(tabControl)
        tabControl.add(tab10, text='DEBUG')
        self.debugScrolledText = scrolledtext.ScrolledText(tab10, wrap=tk.WORD)#width=scrolW, height=scrolH,
        self.debugScrolledText.pack(fill='both', side='left', expand=True)
        self.debugMsg("testing")

        tabControl.pack(expand=1, fill="both")

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        tk.Button(self, text="Return to start page",
                  command=lambda: master.switch_frame(StartPage, MainWindowFrame)).pack()

class LandingPageFrame(tk.Frame):
    def updateEmployeeUI(self):
            self.openImageFileButton.configure(state="enabled")
            if 'photo' in CurrentProvider.Record:
                setLabelImage(self.employeePhotoLabel,CurrentProvider.Record['photo'])
            else: setLabelImage(self.employeePhotoLabel,None) 

    def openImageFileDialog(self):
        filename=filedialog.askopenfilename(initialdir= ".",title ="Open file",
            filetypes = (("png file","*.png"),("any file","*.*")))
        print("File selected:",filename)
        setLabelImage(self.employeePhotoLabel,filename)
        if filename!=():
            CurrentProviderPhoto.updateCurrentProviderPhoto(filename)

    def createWidgets(self):
        #top banner
        self.topBannerFrame=tk.Frame(self.master)
        self.topBannerFrame.pack(side="top", expand=0,fill="x")

        #photo label
        self.employeePhotoLabel=ttk.Label(self.topBannerFrame, text="?")
        self.employeePhotoLabel.grid(column=0,row=0,rowspan=3,sticky='w')
        setLabelImage(self.employeePhotoLabel,None)

        #photo label image select button
        self.openImageFileButton = ttk.Button(self.topBannerFrame, state="disabled", text="Upload Photo", command=self.openImageFileDialog)
        self.openImageFileButton.grid(column=0,row=3)

        #setting up barcode scanner
        def onMRNBarcodeRead(MRN):
            print("patient MRN scanned:",MRN)
            PatientList.selectPatientByMRN(MRN)
            self.main_frame.updatePatientUI()
            
        def onIENBarcodeRead(IEN):
            print("employee IEN scanned:",IEN)

        def onDINBarcodeRead(DIN):
            print("drug DIN scanned:",DIN)
        
        self.bScanner=BarcodeScanner(self,onMRNBarcodeRead,onIENBarcodeRead,onDINBarcodeRead)

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        tk.Button(self, text="Return to start page",
                  command=lambda: master.switch_frame(StartPage, LandingPageFrame)).pack()

if __name__ == "__main__":
    app = SampleApp()
    MiniEMRMongo.connect()
    PatientList.refresh()
    app.mainloop()
    MiniEMRMongo.disconnect()