import unittest
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox



def setUpModule():
        print("----- TkInter GUI simple apps unitest Suite begins")
def tearDownModule():        
        print("\n-----  TkInter GUI simple apps unitest Suite ends")

class TestClass_tkinter_GUI_simple(unittest.TestCase):        
  #Literature resource: Python GUI Programming Cookbook.pdf
  def test_case01_first_gui_app(self):
    #create the main window of the GUI application and get a reference to the window object     
    main_win = tk.Tk()
    main_win.title("Python GUI")

    #what size for the window?
    #https://yagisanatode.com/2018/02/23/how-do-i-change-the-size-and-position-of-the-main-window-in-tkinter-and-python-3/
    main_win.geometry("500x100+500+300")

    #setting up properties of the main window: resizing, position, etc.; 
    #how? read reference literature, try things out; figure what works, what look good  
    #main_win.resizable(0, 0)     #no resizing?

    #stupid, annoying, weird, window location
    # here is a possible fix: https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens  

    #create a label widget on the main window, give it a text
    aLabel=ttk.Label(main_win, text="A Label")
    #set label location
    aLabel.grid(column=0, row=0) 

    #define a button click callback function; it will run when button is clicked
    #when creating a button, set its command property value to this function
    def youClickedMe():
      #button.configure(text="** I have been Clicked! **")
      aLabel.configure(foreground='red')
      button.configure(text='Hello ' + textBox.get())
      
    #add a new button to the main window
    button = ttk.Button(main_win, text="Click Me!", command=youClickedMe)
    button.grid(column=1, row=0)


    def youAlsoClickedMe():
        aLabel.configure(foreground='green')
        button2.configure(text='Also Hello ' + textBox.get())
              
    button2 = ttk.Button(main_win, text="Also Click Me!", command=youAlsoClickedMe)
    button2.grid(column=2, row=0)

    #add a Textbox Entry widget so we can enter some text
    textBox = tk.StringVar()
    nameEntered = ttk.Entry(main_win, width=12, textvariable=textBox)
    nameEntered.grid(column=0, row=1) 
    
    #start the main GUI window main loop (this is the app entry point) 
    main_win.mainloop()
          
  def test_case02_gui_app_oo_style_v1(self):
    #https://python-textbok.readthedocs.io/en/1.0/Introduction_to_GUI_Programming.html
    class MyFirstGUI:
        def __init__(self, master):
            self.master = master
            master.title("A simple GUI")

            self.label = ttk.Label(master, text="This is our first GUI!")
            self.label.pack()

            self.greet_button = ttk.Button(master, text="Greet", command=self.greet)
            self.greet_button.pack()

            self.close_button = ttk.Button(master, text="Close", command=master.quit)
            self.close_button.pack()

        def greet(self):
            messagebox.showinfo("Greetings","Hello from a simple TkIntr GUI app!")
            print("Greetings!")

    main_win = tk.Tk()
    my_gui = MyFirstGUI(main_win)
    main_win.mainloop()

  def test_case03_gui_app_oo_style_v2(self):
    #https://pythonprogramming.net/object-oriented-programming-crash-course-tkinter/

    LARGE_FONT= ("Verdana", 12)

    class SeaofBTCapp(tk.Tk):
        def __init__(self, *args, **kwargs):
            
            tk.Tk.__init__(self, *args, **kwargs)
            container = tk.Frame(self)

            container.pack(side="top", fill="both", expand = True)

            container.grid_rowconfigure(0, weight=1)
            container.grid_columnconfigure(0, weight=1)

            self.frames = {}

            frame = StartPage(container, self)

            self.frames[StartPage] = frame

            frame.grid(row=0, column=0, sticky="nsew")

            self.show_frame(StartPage)

        def show_frame(self, cont):
            frame = self.frames[cont]
            frame.tkraise()
            
    class StartPage(tk.Frame):
        def __init__(self, parent, controller):
            tk.Frame.__init__(self,parent)
            label = tk.Label(self, text="Start Page", font=LARGE_FONT)
            label.pack(pady=10,padx=10)

    app = SeaofBTCapp()
    app.mainloop()

  def test_case04_gui_app_oo_style_v3(self):
    #https://stackoverflow.com/questions/17466561/best-way-to-structure-a-tkinter-application/17470842
    class MainApplicationFrame(tk.Frame):
        def say_hi(self):
            print("hi there, everyone!")

        def createWidgets(self):
          #create and setup QUIT button in separate steps
            self.QUIT = ttk.Button(self)
            self.QUIT["text"] = "QUIT"
            self.QUIT["command"] =  self.quit
            self.QUIT.pack({"side": "left"})
            
          #create and setup Hello button in one line
            self.hi_there = ttk.Button(self, text="Hello", command=self.say_hi)
            self.hi_there.pack({"side": "left"})


        def __init__(self, master=None):
            tk.Frame.__init__(self, master)
            self.pack()
            self.createWidgets()
            

    main_win = tk.Tk()
    main_app_frame = MainApplicationFrame(master=main_win)
    main_win.mainloop()


if __name__ == '__main__': unittest.main()