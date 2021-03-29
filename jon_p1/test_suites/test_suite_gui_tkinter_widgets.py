#WIP - work in progress
#https://www.python-course.eu/tkinter_layout_management.php
#http://effbot.org/tkinterbook/grid.htm

import unittest
import tkinter as tk
from tkinter import ttk

#needs additional imports for fancy widgets
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import messagebox as mBox
from tkinter import Spinbox
from tkinter import PhotoImage
#from PIL import Image
from tkinter import Canvas
#import tooltip as tt   #note: tooltip may need pip install

from tkinter import filedialog

from modINFO74000.misc_func import PATH_TO_IMAGE_FILES

def setUpModule():
        print("----- TkInter GUI widget app unitest Suite begins")
def tearDownModule():        
        print("\n-----  TkInter GUI widget app unitest Suite ends")

class TestClass_tkinter_GUI_complex(unittest.TestCase):        
    #Literature resource: Python GUI Programming Cookbook.pdf
  def test_case01_gui_app_complex_ui(self):    

    win_main = tk.Tk()
    win_main.title("TkInter Python GUI - trying widgets out! ")
    # Change the main windows icon
    #win_main.iconbitmap(PATH_TO_IMAGE_FILES+'/GHouse.png') #does not work!!
    #win_main.resizable(0, 0)     #no resizing?
    #root.withdraw() #to hide it

    #tab widget  style='lefttab.TNotebook'
    tabControl = ttk.Notebook(win_main)
    tab1 = ttk.Frame(tabControl)
    tabControl.add(tab1, text='Tab 1')
    tab2 = ttk.Frame(tabControl)
    tabControl.add(tab2, text='Tab 2')
    tab3 = ttk.Frame(tabControl)
    tabControl.add(tab3, text='Tab 3')
    tabControl.pack(expand=1, fill="both")
    

    # We are creating a container frame to hold all other widgets # 1
    frame1 = ttk.LabelFrame(tab1, text=' Main Frame ')
    frame1.grid(column=0, row=0,padx=8, pady=4)

    #label example
    aLabel=ttk.Label(frame1, text="Enter name:")
    aLabel.grid(column=0, row=0, sticky='W') 

    #button widget example
    #define a button click callback
    def clickMe():
            #button.configure(text="** I have been Clicked! **")
            aLabel.configure(foreground='red')
            button.configure(text='Hello ' + nameString.get()+' '+numberComboBox.get())

    button = ttk.Button(frame1, text="Click Me!", command=clickMe)
    button.grid(column=2, row=0)

    #textbox widget example
    nameString = tk.StringVar()
    nameTextBox = ttk.Entry(frame1, width=12, textvariable=nameString)
    nameTextBox.grid(column=0, row=1) 

    #combobox widget example
    ttk.Label(frame1, text="Choose a number:").grid(column=1, row=0)
    numberString = tk.StringVar()
    #for r/o combobox state='readonly'
    numberComboBox = ttk.Combobox(frame1, width=12, textvariable=numberString)
    numberComboBox['values'] = (1, 2, 4, 42, 100)
    numberComboBox.grid(column=1, row=1)
    numberComboBox.current(0)

    #spinbox widget
    def _spin():
        value = spin.get()
        print(value)
        scrolledText.insert(tk.INSERT, value + '\n')

    spin = Spinbox(frame1, from_=0, to=10, width=5, command=_spin)
    #or spin = Spinbox(monty, values=(1, 2, 4, 42, 100), width=5, ....
    spin.grid(column=0, row=2)

    #  scrolled Text control
    scrolW = 30
    scrolH = 3
    scrolledText = scrolledtext.ScrolledText(frame1, width=scrolW, height=scrolH,wrap=tk.WORD)
    scrolledText.grid(column=0, columnspan=3)


    #-----------------Frame 2
    frame2 = ttk.LabelFrame(tab2, text=' The Snake ')
    frame2.grid(column=0, row=0, padx=8, pady=4)

    #checkbox examples
    chVarDis = tk.IntVar()
    check1 = tk.Checkbutton(frame2, text="Disabled", variable=chVarDis, state='disabled')
    check1.select()
    check1.grid(column=0, row=4, sticky=tk.W) # 5

    chVarUn = tk.IntVar()
    check2 = tk.Checkbutton(frame2, text="UnChecked", variable=chVarUn)
    check2.deselect()
    check2.grid(column=1, row=4, sticky=tk.W) # 9

    chVarEn = tk.IntVar()
    check3 = tk.Checkbutton(frame2, text="Enabled", variable=chVarEn)
    check3.select()
    check3.grid(column=2, row=4, sticky=tk.W) # 13

    # Radiobutton example
    #Globals
    COLOR1 = "Blue"
    COLOR2 = "Gold"
    COLOR3 = "Red"
    # Radiobutton Callback
    def radCall():
        radSel=radVar.get()
        if radSel == 1: frame2.configure(text=COLOR1)
        elif radSel == 2: frame2.configure(text=COLOR2)
        elif radSel == 3: frame2.configure(text=COLOR3)
    # create three Radiobuttons
    radVar = tk.IntVar()
    rad1 = tk.Radiobutton(frame2, text=COLOR1, variable=radVar, value=1, command=radCall)
    rad1.grid(column=0, row=5, sticky=tk.W) # 10
    rad2 = tk.Radiobutton(frame2, text=COLOR2, variable=radVar, value=2, command=radCall)
    rad2.grid(column=1, row=5, sticky=tk.W) # 12
    rad3 = tk.Radiobutton(frame2, text=COLOR3, variable=radVar, value=3, command=radCall)
    rad3.grid(column=2, row=5, sticky=tk.W) # 14


    #label frame
    # Create a container to hold labels
    labelsFrame = ttk.LabelFrame(frame2, text=' Labels in a Frame ') # 1
    labelsFrame.grid(column=0, row=7, padx=20, pady=40)
    # Place labels into the container element # 2
    ttk.Label(labelsFrame, text="Label1 -- sooooo much loooonger...").grid(column=0, row=0)
    ttk.Label(labelsFrame, text="Label2").grid(column=0, row=1)
    ttk.Label(labelsFrame, text="Label3").grid(column=0, row=2)

    #space out the children of frame object
    for child in labelsFrame.winfo_children():
        child.grid_configure(padx=8, pady=4)

    #menu example
    menuBar = Menu(win_main)
    win_main.config(menu=menuBar)
    #adding file menu
    fileMenu = Menu(menuBar, tearoff=1)
    menuBar.add_cascade(label="File", menu=fileMenu)
    #adding view menu
    viewMenu = Menu(menuBar, tearoff=0)
    menuBar.add_cascade(label="View", menu=viewMenu)
    
    def _quit():
        answer = mBox.askyesno("Python Message Dual Choice Box", "Are you sure you really wish to do this?")
        print(answer)
        if answer==True: 
            win_main.quit()

    def open_file():
        filename = filedialog.askopenfilename(initialdir = ".",title = "Open file",filetypes = (("jpeg files","*.jpg"),("any file","*.*")))
        print('Opened file:',filename)

    def save_file():
        filename = filedialog.asksaveasfilename(initialdir = ".",title = "Save file",filetypes = (("jpeg files","*.jpg"),("any file","*.*")))
        print('Saving file:',filename)

    def select_directory():
        filename = filedialog.askdirectory()
        print('Selected directory:',filename)

    fileMenu.add_command(label="New")
    fileMenu.add_command(label="Open file...", command=open_file)
    fileMenu.add_command(label="Save file...", command=save_file)
    fileMenu.add_command(label="Select directory...", command=select_directory)    
    fileMenu.add_separator()
    fileMenu.add_command(label="Exit", command=_quit)

    

    #message box example
    def _msgBox():
        mBox.showinfo('Python Message Info Box', 'A Python GUI created using tkinter:\nThe year is 2018.')
        mBox.showwarning('Python Message Warning Box', 'A Python GUI created using tkinter:\nWarning: There might be a bug in this code.')
        mBox.showerror('Python Message Error Box', 'A Python GUI created using tkinter:\nError: Houston ~ we DO have a serious PROBLEM!')
    # Add another Menu to the Menu Bar and an item

    helpMenu = Menu(menuBar, tearoff=0)
    menuBar.add_cascade(label="Help", menu=helpMenu)
    helpMenu.add_command(label="About", command=_msgBox)

    #tooltip example
    #tt.createToolTip(spin,"this is a spin ctrl")

    #todo, see: canvas page 63,  mathplotlibs, threads, queues, networking, dialog widgets, SQL,

    #image on canvas    
    img=PhotoImage(file=PATH_TO_IMAGE_FILES+'/GHouse.png')
    canvas = Canvas(tab3, width = 300, height = 300)      
    canvas.pack()      
    canvas.create_image(20,20, anchor='nw', image=img)

    #https://pythonspot.com/tk-file-dialogs/

    #focus on textbox widget
    nameTextBox.focus()

    win_main.mainloop()


if __name__ == '__main__': unittest.main()