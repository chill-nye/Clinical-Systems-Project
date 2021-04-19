
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
from tkinter import messagebox
from tkinter import Listbox
from tkinter import Button

from modINFO74000.emr_misc_ui import TopDialogWindow
from modINFO74000.emr_db import MiniEMRMongo
from datetime import datetime

DATE_TIME_FORMAT="%Y-%m-%dT%H:%M:%S.%fZ"
DEFAULT_AUTH_IEN=7 #test                

VITAL_TYPE_LIST=  ['Wkg',       'Hcm',    'P',      'R',          "POX",        'PN',       'BP']
VITAL_TYPE_LABELS=['Weight',    'Height', 'Pulse',  'Respiration','Oxygen sat.','Pain',     'Blood pressure']
VITAL_TYPE_DATA=  [tk.DoubleVar,tk.IntVar,tk.IntVar,tk.IntVar,    tk.IntVar,    tk.IntVar,  tk.StringVar]
VITAL_TYPE_MIN=   [0,           0,        0,        0,            0,            0,          '']

        
class VitalsWriteDialog(TopDialogWindow):

  def __init__(self,master=None,patient=None,providerIEN=None,callback=None):

    TopDialogWindow.__init__(self, master)   

    #vitalsReadVars holds the tk.*Var objects of various types in a list
    self.vitalsReadVars=[]
    for vt in VITAL_TYPE_LIST:
      idx=VITAL_TYPE_LIST.index(vt)
      ttk.Label(self.mainFrame, text=VITAL_TYPE_LABELS[idx]).grid(column=0, row=idx, sticky='W')
      #creates an instance of the tk.*Var object of the appropriate type
      readVar=VITAL_TYPE_DATA[idx]()
      self.vitalsReadVars.append(readVar)
      ttk.Entry(self.mainFrame, width=12, textvariable=readVar).grid(column=1, row=idx,sticky='W') 

    def clickSaveVitals():
      #new vitals object is initially an empty dictionary 
      vitals_object={}
      
      for vt in VITAL_TYPE_LIST:
        idx=VITAL_TYPE_LIST.index(vt)
        try:
          vital_value=self.vitalsReadVars[idx].get()
          if vital_value!=VITAL_TYPE_MIN[idx]:
            #BP needs special treatment because it is a string that needs parsing 
            #also, BP values are saved as an object
            if vt=="BP":
              try:
                bpVal=vital_value.split('/')
                #if str.isnumeric(bpVal[0]) and str.isnumeric(bpVal[1]): 
                vitals_object[vt]={"sys":int(bpVal[0]),"dia":int(bpVal[1])}
                messagebox.showerror("BP values error. ")
              except Exception as ex:
                messagebox.showerror("BP value parsing error",
                  message='Expecting two numeric values in format [systolic]/[diastolic]\n'+str(ex))
            else:
              vitals_object[vt]=vital_value
        except Exception as ex:
          messagebox.showerror(VITAL_TYPE_LABELS[idx]+" vital data ("+vt+") error",message=ex)


      #checking if vitals object dictionary has any vitals data by counting keys added to it
      if len(vitals_object.keys())>0:
        #at least one vital type has data that needs saving
        vitals_object["AuthIEN"]=providerIEN
        vitals_object["datetime"]=datetime.utcnow().isoformat()+'Z'
        #updates current patient record by pushing the vitals object into the vitals array/list         
        #patient=PatientList.current()
        if not patient==None:
          updateRes=MiniEMRMongo.db.patients.update_one(
                  {'_id':patient['_id']},
                  {'$push':{'vitals':vitals_object}})
          #to see of the update was succesful
          print("update result",updateRes)
          #quick hack to refresh patient list, data objects and the UI!   
        if callback!=None: callback()
        self.hide()
    #cannot use state="disabled"
    self.vitals_save_button = ttk.Button(self.mainFrame, text="Update", command=clickSaveVitals)
    self.vitals_save_button.grid(column=0, row=len(VITAL_TYPE_LIST)+2)

