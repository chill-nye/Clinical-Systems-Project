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

from modINFO74000.emr_misc_ui import TopDialogWindow
from modINFO74000.emr_db import MiniEMRMongo

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

    @classmethod
    def updateCurrentPatientDrugAdministrationRecord(cls,drug_order_index,drug_admin_info):
        patient=PatientList.current()
        if patient!=None:
            #https://docs.mongodb.com/manual/reference/operator/update/positional/
            update_result=MiniEMRMongo.db.patients.update_one(
                    {'_id':patient['_id']},
                    {'$push':{'orders.medications.{0}.admin'.format(drug_order_index):drug_admin_info}})