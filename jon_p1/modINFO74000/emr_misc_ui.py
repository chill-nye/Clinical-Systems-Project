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

from modINFO74000.emr_db import MiniEMRMongo
from  modINFO74000.emr_const import *
from bson.objectid import ObjectId 
import gridfs


class TopDialogWindow(tk.Toplevel):

  def __init__(self,master=None):
    tk.Toplevel.__init__(self, master)
    self.resizable(False,False)
    self.mainFrame =ttk.Frame(self)
    self.mainFrame.pack(side="top", fill="both", expand = True)
    self.grab_set()            
    #self.focus_force()
    self.resizable(False,False)
    self.transient(master)

  def show(self):
      self.deiconify()
      self.grab_set()
      self.update()
      xpos=self.winfo_screenwidth() // 2 - self.winfo_width() // 2 
      ypos=self.winfo_screenheight() // 2 - self.winfo_height() // 2 
      self.geometry('+'+str(xpos)+'+'+str(ypos))      

  def hide(self):
      self.withdraw()
      self.grab_release()      

class LicenseWindow(TopDialogWindow):
  def __init__(self,master=None):
    TopDialogWindow.__init__(self, master)
    scrolledText = scrolledtext.ScrolledText(self.mainFrame, wrap=tk.WORD)
    scrolledText.pack(fill='both', side='left', expand=True)
    scrolledText.insert('end', __doc__)

def unknownPhotoImage():
    unknown_photo_img=tk.PhotoImage(file=PATH_TO_IMAGE_FILES+'/Unknown-person.gif')
    #unknown_photo_img.configure(width=64,height=64)
    return unknown_photo_img.subsample(3)#to make the image smaller

def setLabelImage(photoLabel,img_src=None,subsample=1):
    photo_img=None
    if img_src==None:
        photo_img=unknownPhotoImage()
    else:
        if type(img_src)==tk.PhotoImage:
            photo_img=img_src
        elif type(img_src)==str or type(img_src)==tuple:
            if img_src==(): photo_img=unknownPhotoImage()
            else:
                try:
                    f=open(img_src,"br") 
                    img_data=f.read()
                    photo_img=tk.PhotoImage(data=img_data)
                    #to make the image smaller'''
                    if subsample>1: photo_img=photo_img.subsample(subsample)
                except Exception as e:
                    print('error ',e,' attaching image file: ',img_src,' to label')
                finally:
                    f.close()
        elif type(img_src)==ObjectId:
            fs = gridfs.GridFS(MiniEMRMongo.db)
            with fs.get(img_src) as gridfs_img:
                print('Found gridfs image to download ',gridfs_img._id)  
                img_data=gridfs_img.read()
                photo_img=tk.PhotoImage(data=img_data)
                gridfs_img.close()

    photoLabel.configure(image=photo_img)
    photoLabel.photo=photo_img                       

def hide_all_frames(frame):
    for widget in frame.winfo_children():
        widget.destroy()
    frame.pack_forget()