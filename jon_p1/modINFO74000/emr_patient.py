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
from tkinter import scrolledtext
from tkinter import Listbox
from tkinter import Button
from tkinter import messagebox

from modINFO74000.emr_misc_ui import TopDialogWindow
from modINFO74000.emr_db import MiniEMRMongo

import random
from datetime import datetime
from datetime import timedelta

class PatientList():
    CurrentPatientIndex=None
    Patients=[]

    @classmethod
    def current(cls):
        if cls.CurrentPatientIndex==None: return None
        else: 
            return cls.Patients[cls.CurrentPatientIndex]

    @classmethod
    def clearCurrentSelection(cls):
        cls.CurrentPatientIndex=None

    @classmethod
    def updateCurrentPatientPhoto(cls,filename):
        patient=PatientList.current()
        if patient!=None:
            newFileOId=MiniEMRMongo.uploadGridFSFile(filename)
            patient["photo"]=newFileOId
            patient_collection=MiniEMRMongo.db.patients
            patient_collection.update_one(
                                    {'_id':patient['_id']},
                                    {'$set':{'photo':newFileOId}})
    @classmethod
    def updateCurrentPatientMedicationList(cls,medObj):
        patient=PatientList.current()
        if patient!=None:
            patient_collection=MiniEMRMongo.db.patients
            #update the patient record (database) by append/push a new object into the medication order list
            patient_collection.update_one(
                                    {'_id':patient['_id']},
                                    {'$push':{'orders.medications':medObj}})
                                    
    @classmethod
    def refresh(self):
        PatientList.Patients.clear()
        query_result=MiniEMRMongo.db.patients.find()
        if query_result!=None:
            for p in query_result: 
                PatientList.Patients.append(p)
        
    @classmethod
    def selectPatientByMRN(cls, MRN):
        patient_collection=MiniEMRMongo.db.patients
        query_result=patient_collection.find_one({"id":int(MRN)})
        if query_result==None:
            #move this to the debug tab or as a pop up
            print("Could not find the patient with MRN:", MRN)
        else:
            print("patient record found:")
            PatientList.CurrentPatientIndex=PatientList.Patients.index(query_result)
    @classmethod
    def updateCurrentPatientDrugAdministrationRecord(cls,drug_order_index,drug_admin_info):
        patient=PatientList.current()
        if patient!=None:
            #https://docs.mongodb.com/manual/reference/operator/update/positional/
            update_result=MiniEMRMongo.db.patients.update_one(
                    {'_id':patient['_id']},
                    {'$push':{'orders.medications.{0}.admin'.format(drug_order_index):drug_admin_info}})

    @classmethod
    def updateCurrentPatientTestRecord(cls, test_admin_info):
        patient=PatientList.current()
        if patient!=None:
            #https://docs.mongodb.com/manual/reference/operator/update/positional/
            update_result=MiniEMRMongo.db.patients.update_one(
                    {'_id':patient['_id']},
                    {'$addToSet':{'orders.tests':test_admin_info}})

class PatientSelectDialog(TopDialogWindow):
    def getPatientList(self):
        for p in PatientList.Patients: 
            self.patientListbox.insert('end', p["name"])

    def __init__(self,master=None,callback=None):
        TopDialogWindow.__init__(self, master)
        self.patientListbox = Listbox(self.mainFrame)
        self.patientListbox.pack()
        def ok():
            PatientList.CurrentPatientIndex=self.patientListbox.curselection()[0]
            print('selected patient index:',PatientList.CurrentPatientIndex)
            self.hide()
            if callback!=None: callback()
        #self.patientListbox.bind("<Double-Button-1>", ok) - not working too well
        self.okButton=ttk.Button(self.mainFrame,text="OK", command=ok)
        self.okButton.pack()        
        self.getPatientList()



#add patient frame
class addPatientUIFrame(tk.Frame):
    def createWidgets(self):
        #patient details
        self.patientName = tk.StringVar()    
        self.dob = tk.StringVar()
        self.gender = tk.StringVar()
        self.eMail = tk.StringVar()
        self.street= tk.StringVar()
        self.city = tk.StringVar()
        self.phone = tk.StringVar()
        self.cell = tk.StringVar()
        #contact details
        self.contactName = tk.StringVar()
        self.contactPhone = tk.StringVar()
        self.contactRelation = tk.StringVar()

        #label
        PatientNameLabel=ttk.Label(self, text="Patient Name:")
        PatientNameLabel.grid(column=0, row=0, sticky='E')             
        dobLabel=ttk.Label(self, text="Date of Birth (yyyy-mm-dd):")
        dobLabel.grid(column=0, row=1, sticky='E')
        genderLabel=ttk.Label(self, text="Gender:")
        genderLabel.grid(column=0, row=2, sticky='E')
        eMailLabel=ttk.Label(self, text="eMail:")
        eMailLabel.grid(column=0, row=3, sticky='E')
        streetLabel=ttk.Label(self, text="Street Address:")
        streetLabel.grid(column=0, row=4, sticky='E')
        cityLabel=ttk.Label(self, text="City:")
        cityLabel.grid(column=0, row=5, sticky='E')
        phonenumberLabel=ttk.Label(self, text="Telephone number:")
        phonenumberLabel.grid(column=0, row=6, sticky='E')
        cellLabel=ttk.Label(self, text="Cellphone number:")
        cellLabel.grid(column=0, row=7, sticky='E')
        contactNameLabel=ttk.Label(self, text="Emergency Contact Name:")
        contactNameLabel.grid(column=0, row=8, sticky='E')
        contactNumberLabel=ttk.Label(self, text="Emergency Contact Number:")
        contactNumberLabel.grid(column=0, row=9, sticky='E')
        contactRelationLabel=ttk.Label(self, text="Emergency Contact Relation:")
        contactRelationLabel.grid(column=0, row=10, sticky='E')

        #text boxes
        self.PatientNameTextBox = ttk.Entry(self,width=24, textvariable = self.patientName)
        self.PatientNameTextBox.grid(column=1, row=0,padx=2,pady=2)
        self.dobTextBox = ttk.Entry(self,width=24, textvariable = self.dob)
        self.dobTextBox.grid(column=1, row=1,padx=2,pady=2)
        self.genderTextBox = ttk.Entry(self,width=24, textvariable = self.gender)
        self.genderTextBox.grid(column=1, row=2,padx=2,pady=2)
        self.eMailTextBox = ttk.Entry(self,width=24, textvariable = self.eMail)
        self.eMailTextBox.grid(column=1, row=3,padx=2,pady=2)
        self.streetTextBox = ttk.Entry(self,width=24, textvariable = self.street)
        self.streetTextBox.grid(column=1, row=4,padx=2,pady=2)
        self.cityTextBox = ttk.Entry(self,width=24, textvariable = self.city)
        self.cityTextBox.grid(column=1, row=5,padx=2,pady=2)
        self.phoneTextBox = ttk.Entry(self,width=24, textvariable = self.phone)
        self.phoneTextBox.grid(column=1, row=6,padx=2,pady=2)
        self.cellTextBox = ttk.Entry(self,width=24, textvariable = self.cell)
        self.cellTextBox.grid(column=1, row=7,padx=2,pady=2)
        self.contactNameTextBox = ttk.Entry(self,width=24, textvariable = self.contactName)
        self.contactNameTextBox.grid(column=1, row=8,padx=2,pady=2)
        self.contactPhoneTextBox = ttk.Entry(self,width=24, textvariable = self.contactPhone)
        self.contactPhoneTextBox.grid(column=1, row=9,padx=2,pady=2)
        self.contactRelationTextBox = ttk.Entry(self,width=24, textvariable = self.contactRelation)
        self.contactRelationTextBox.grid(column=1, row=10,padx=2,pady=2)

        self.confirm_button = ttk.Button(self, width=16, text="Add Patient", command=self.master.add_patient)
        self.confirm_button.grid(column=1, row=11,padx=2,pady=2)

    def clear(self):
        #clear textboxes
        self.PatientNameTextBox.delete(0,'end')
        self.dobTextBox.delete(0,'end')
        self.genderTextBox.delete(0,'end')
        self.eMailTextBox.delete(0,'end')
        self.streetTextBox.delete(0,'end')
        self.cityTextBox.delete(0,'end')
        self.phoneTextBox.delete(0,'end')
        self.cellTextBox.delete(0,'end')
        self.contactNameTextBox.delete(0,'end')
        self.contactPhoneTextBox.delete(0,'end')
        self.contactRelationTextBox.delete(0,'end')
        self.PatientNameTextBox.focus()

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

#add patient function
class AddNewPatient(TopDialogWindow):
    def __init__(self, master=None):
        TopDialogWindow.__init__(self, master)
        self.addPatientUI = addPatientUIFrame(self)
        self.addPatientUI.pack(side="top", fill="both", expand = True)
        self.title("Add New Patient")
        self.protocol("WM_DELETE_WINDOW", self.on_close)      
        def enter_press(event):
            self.add_patient()
        self.bind('<Return>', enter_press)#allows pressing Enter to logon

    def add_patient(self):
        #getting variables from form
        patientNamevar = self.addPatientUI.patientName.get()
        dobvar = self.addPatientUI.dob.get()
        gendervar = self.addPatientUI.gender.get()
        eMailvar = self.addPatientUI.eMail.get()
        streetvar = self.addPatientUI.street.get()
        cityvar = self.addPatientUI.city.get()
        phonevar = self.addPatientUI.phone.get()
        cellvar = self.addPatientUI.cell.get()
        contactNamevar = self.addPatientUI.contactName.get()
        contactPhonevar = self.addPatientUI.contactPhone.get()
        contactRelationvar = self.addPatientUI.contactRelation.get()

        #generating patient id
        patient_id = random.randint(1000,100000)

        #fixing date-time
        adjusted_dob = datetime.strptime(dobvar,'%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        #creating json structure
        patient_data = {
            "id":"{}".format(patient_id), 
            "name":"{}".format(patientNamevar),
            "dob":"{}".format(adjusted_dob),
            "gender":"{}".format(gendervar),        
            "contact":{
                "person":{
                    "name":"{}".format(contactNamevar),
                    "phone":"{}".format(contactPhonevar),
                    "relation":"{}".format(contactRelationvar)
                },
                "eMail":"{}".format(eMailvar),
                "address":{
                    "street":"{}".format(streetvar),
                    "city":"{}".format(cityvar)},
                    "telephone":"{}".format(phonevar),
                    "cell":"{}".format(cellvar)},
            "allergies":[],
            "orders":{
                "medications":[],
                "tests":[],
                "administration":[]  
            },
            "problems":[{"ICD10code":""}],
            "vitals":[]
        }

        if patientNamevar.strip() != '':
            patient_collection = MiniEMRMongo.db.patients
            patient_collection.insert_one(patient_data)
            self.hide()
            messagebox.showinfo("New Patient Added","Patient has been successfully added.")
            PatientList.refresh()
        else:
            messagebox.showerror("Insert error","Please ensure all fields are filled out correctly.")         

    def on_close(self):
        self.destroy()
    
    def show(self):
        super(AddNewPatient, self).show()
        self.addPatientUI.clear()    

class editPatientUIFrame(tk.Frame):
    def createWidgets(self):
        #patient details
        self.allergies = tk.StringVar()    
        self.diagnosis = tk.StringVar()

        #label
        AllergiesLabel=ttk.Label(self, text="Allergies (,):")
        AllergiesLabel.grid(column=0, row=0, sticky='E')             
        diagnosisLabel=ttk.Label(self, text="Diagnosis:")
        diagnosisLabel.grid(column=0, row=1, sticky='E')

        #text boxes
        self.AllergiesTextBox = ttk.Entry(self,width=24, textvariable = self.allergies)
        self.AllergiesTextBox.grid(column=1, row=0,padx=2,pady=2)
        self.diagnosisTextBox = ttk.Entry(self,width=24, textvariable = self.diagnosis)
        self.diagnosisTextBox.grid(column=1, row=1,padx=2,pady=2)

        self.confirm_button = ttk.Button(self, width=16, text="Save Changes", command=self.master.edit_patient)
        self.confirm_button.grid(column=1, row=2,padx=2,pady=2)

    def clear(self):
        #clear textboxes
        self.AllergiesTextBox.delete(0,'end')
        self.diagnosisTextBox.delete(0,'end')
        self.AllergiesTextBox.focus()

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

#add patient function
class EditPatient(TopDialogWindow):
    def __init__(self, master=None):
        TopDialogWindow.__init__(self, master)
        self.EditPatientUI = editPatientUIFrame(self)
        self.EditPatientUI.pack(side="top", fill="both", expand = True)
        self.title("Edit Patient")
        self.protocol("WM_DELETE_WINDOW", self.on_close)      
        def enter_press(event):
            self.edit_patient()
        self.bind('<Return>', enter_press)#allows pressing Enter to logon

    def edit_patient(self):
        #getting variables from form
        allergiesvar = []
        for allergy in self.EditPatientUI.allergies.get().split(','):
            allergiesvar.append(allergy)
        diagnosisvar = self.EditPatientUI.diagnosis.get()

        #parsing icd description           
        query_result=MiniEMRMongo.db.icd10.find_one({"desc":diagnosisvar})
        if (query_result==None) or len(allergiesvar) == 0:
            messagebox.showerror("Update error","Please ensure all fields are filled out correctly.")     
        else:
            emptyList = []
            objectItem = {'ICD10code':query_result['code']}
            emptyList.append(objectItem)
            patient_collection = MiniEMRMongo.db.patients
            patient=PatientList.current()
            if patient!=None:
                patient_collection.update_one(                                     
                    {'_id':patient['_id']},
                    {'$set':{'allergies': allergiesvar,'problems':emptyList}})
                self.hide()
                messagebox.showinfo("Patient file updated","Patient has been successfully updated.")
                PatientList.refresh()    

    def on_close(self):
        self.destroy()
    
    def show(self):
        super(EditPatient, self).show()
        self.EditPatientUI.clear()