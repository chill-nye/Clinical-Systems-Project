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
from tkinter import Menu
from tkinter import scrolledtext

from modINFO74000.emr_db import MiniEMRMongo
from modINFO74000.emr_patient import *
from modINFO74000.emr_provider import *
from modINFO74000.emr_const import *
from datetime import datetime
from modINFO74000.emr_vitals import *

class MainWindow(tk.Tk):

  def updateVitalsUI(self):
    patient=PatientList.current()        
    self.summaryScrolledText.replace('1.0','end',patient["name"]+"\n")
       
    if 'vitals' in patient:
      vital_data_series={} #dictionary for compiling all vital measurement by type, in a data series   

      self.summaryScrolledText.insert('end',"List vitals data by date/time:\n")
      #list all vitals by recording date      
      for vitals_object in patient['vitals']:   
        #dealing with datetime and author metadata
        record_date_time=datetime.strptime((vitals_object['date_time']),DATE_TIME_FORMAT)
        
        # using a list comprehension to filter only the vital types available in the object
        # note that the object contains the date time stamp and author field (they are NOT vital type data)        
        recorded_vital_types=[vt for vt in vitals_object if vt in VITAL_TYPE_LIST]
        
        for vt in recorded_vital_types:
          idx=VITAL_TYPE_LIST.index(vt)
          #initializes the vital data series dictionary  if needed
          if not vt in vital_data_series: vital_data_series[vt]=[] 
          #adds the vital type recording to the appropriate data series
          vital_data_series[vt].append({"date_time":record_date_time,"value":vitals_object[vt]})
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

      for vt in vital_data_series: #this is better, no more "if" statement needed!
        strVitalSeries=""
        for value in vital_data_series[vt]: 
          strVitalSeries+=value["date_time"].strftime(DATE_TIME_FORMAT)+", value:"+str(value["value"])+'\n'          
        self.summaryScrolledText.insert('end',vt+'\n'+strVitalSeries+'\n')

  def createWidgets(self):
      menuBar = Menu(self.master)
      self.config(menu=menuBar)
      fileMenu = Menu(menuBar, tearoff=0)
      menuBar.add_cascade(label="File", underline=0, menu=fileMenu)

      self.summaryScrolledText = scrolledtext.ScrolledText(self.master, wrap=tk.WORD)
      self.summaryScrolledText.pack(side="top", fill="both", expand = True)
                  
      def selectPatient():
        def updateUICallback():
          self.updateVitalsUI()
          #enables the vital recording menu
          fileMenu.entryconfig("Record vitals...", state="normal")

        patient_select_win=PatientSelectDialog(master=self,callback=updateUICallback)
        patient_select_win.show()

      #patient select menu
      fileMenu.add_command(label="Select patient...", command=selectPatient)      

      def recordVitals():
          #because the database was updated, a refresh of patient list is needed
          def refreshPatientListAndUpdateUICallback():
            PatientList.refresh()
            self.updateVitalsUI()

          #before creating the vitals record dialog, I must figure out current provider IEN
          if NO_LOGON_TESTING: currentProviderIEN=DEFAULT_AUTH_IEN
          else: currentProviderIEN=CurrentProvider.Record["IEN"]

          vitals_win=VitalsWriteDialog(master=self,
            patient=PatientList.current(), #current patient object
            providerIEN=currentProviderIEN,  #logged on provider IEN
            callback=refreshPatientListAndUpdateUICallback) #callback for refreshing patient data and updating UI 

          vitals_win.show()        

      #vitals recording menu, by default is disabled until a patient is selected
      fileMenu.add_command(label="Record vitals...", state="disabled", command=recordVitals)      

      helpMenu = Menu(menuBar, tearoff=0)
      menuBar.add_cascade(label="Help", menu=helpMenu)    

      def aboutMenuSelected():
          messagebox.showinfo('About', APP_NAME+' application prototype\n 2019, Stefan V. Pantazi, MD, PhD')

      helpMenu.add_command(label="About", command=aboutMenuSelected)
      
      xpos=self.winfo_screenwidth() // 2 - MAIN_WIN_WIDTH // 2 
      ypos=self.winfo_screenheight() // 2 - MAIN_WIN_HEIGHT // 2 
      self.geometry(str(MAIN_WIN_WIDTH)+'x'+str(MAIN_WIN_HEIGHT)+'+'+str(xpos)+'+'+str(ypos))   

  def __init__(self):
        tk.Tk.__init__(self,None)
        self.title(APP_NAME)       
        self.createWidgets()

        if not NO_LOGON_TESTING:
          self.login_win=LoginWindowDialog(master=self)
          self.login_win.show()    

       

APP_NAME+=' (Vitals v2)' 
main_win = MainWindow()
#connect to mongodb just before main loop
MiniEMRMongo.connect()
PatientList.refresh()
main_win.mainloop()
#disconnect from mongodb after main loop finishes
MiniEMRMongo.disconnect()
