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
        else: return cls.Patients[cls.CurrentPatientIndex]

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
    def selectPatientByMRN(cls,MRN):
        patient_collection=MiniEMRMongo.db.patients
        query_results=patient_collection.find_one({'id': int(MRN)})
        if query_results==None:
            print("Could not find the patient with MRN: ", MRN)
        else:
            print("patient record found: ",query_results)
            PatientList.CurrentPatientIndex=PatientList.Patients.index(query_results)
            print("Current patient index: ", PatientList.CurrentPatientIndex)

class PatientSelectDialog(TopDialogWindow):

    def getPatientList(self):
        for p in PatientList.Patients: 
            #self.scrolledText.insert('end', p["name"]+"\n")
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

class MedList():
    CurrentMedIndex=None
    Meds=[]
    
    @classmethod
    def current(cls):
        if cls.CurrentMedIndex==None: return None
        else:
            return cls.Meds[cls.CurrentMedIndex]

    @classmethod
    def clearCurrentSelection(cls):
        cls.CurrentMedIndex=None              

    @classmethod
    def refresh(cls):
        MedList.Meds.clear()
        query_result=MiniEMRMongo.db.drug_formulary.find()
        if query_result!=None:
            for m in query_result: 
                MedList.Meds.append(m)
                
    @classmethod
    def findDrugbyDIN(cls,DIN):
        record_query_result = MiniEMRMongo.db.drug_formulary.find_one({'DIN': (DIN)})
        if record_query_result == None:
            print('I could not find that drug with the DIN: ' + DIN)

        else:
            print('Drug record found: ', record_query_result)
            MedList.CurrentMedIndex= MedList.Meds.index(record_query_result)
            

class MedSelectDialog(TopDialogWindow):

    def getMedsList(self):
        # for m in MedList.Meds:
        #    self.MedListbox.insert('end', m["TRADENAME"])
        patient=PatientList.current()
        for meds in patient["orders"]["medications"]:
            self.medsListbox.insert('end', meds["drug"])

    def __init__(self,master=None,callback=None):
        TopDialogWindow.__init__(self, master)
        self.medsListbox = Listbox(self.mainFrame)
        self.medsListbox.pack()
        def ok():
            PatientList.CurrentMedIndex=self.medsListbox.curselection()[0]
            print('selected patient index:',MedList.CurrentMedIndex)
            self.hide()
            if callback!=None: callback()
        #self.patientListbox.bind("<Double-Button-1>", ok) - not working too well
        self.okButton=ttk.Button(self.mainFrame,text="OK", command=ok)
        self.okButton.pack()        
        self.getMedsList()

class LabList():
    CurrentLabIndex=None
    Labs=[]
#    for d in drugs(formulary):
 #       drugs=MiniEMRMongo.db.drug_formulary.find(formulary)
  #      Meds.append(d)

    
    @classmethod
    def current(cls):
        if cls.CurrentLabIndex==None: return None
        else:
            return cls.Labs[cls.CurrentLabIndex]

    @classmethod
    def clearCurrentSelection(cls):
        cls.CurrentLabIndex=None              

    @classmethod
    def refresh(cls):
        LabList.Labs.clear()
        query_result=MiniEMRMongo.db.labs.find()
        if query_result!=None:
            for l in query_result: 
                LabList.Labs.append(l)
        

    @classmethod
    def findLabID(cls,CompositeRequestID):
        record_query_result = MiniEMRMongo.db.labs.find_one({'Composite Request ID': (CompositeRequestID)})
        if record_query_result == None:
            print('I could not find that Lab with the Composite Request ID: ' + CompositeRequestID)
        else:
            print('Lab record found: ', record_query_result)
            LabList.CurrentLabIndex= LabList.Labs.index(record_query_result)

class LabSelectDialog(TopDialogWindow):

    def getLabsList(self):
        lab=LabList.current()
        for l in lab["Patient_ID"]:
            self.LabsListbox.insert('end', l["code"])

    def __init__(self,master=None,callback=None):
        TopDialogWindow.__init__(self, master)
        self.LabsListbox = Listbox(self.mainFrame)
        self.LabsListbox.pack()
        def ok():
            LabList.CurrentlabIndex=self.LabsListbox.curselection()[0]
            print('selected patient index:',LabList.CurrentLabIndex)
            self.hide()
            if callback!=None: callback()
        #self.patientListbox.bind("<Double-Button-1>", ok) - not working too well
        self.okButton=ttk.Button(self.mainFrame,text="OK", command=ok)
        self.okButton.pack()        
        self.getLabsList()