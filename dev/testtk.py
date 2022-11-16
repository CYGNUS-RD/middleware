'''
Created on Aug 2, 2018

@author: pgnanesh
'''


import paramiko
from datetime import datetime
import matplotlib
from matplotlib import pyplot as plt
from pip._vendor.html5lib.filters.sanitizer import allowed_protocols
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
try:
    from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
except ImportError:
    from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import tkinter as tk
from threading import Thread

style.use('ggplot')

fields = 'HOSTNAME', 'USERNAME', 'PASSWORD'
sel_fields = 'CPU','RAM','SWAP','IO Transfer', 'Process/Context Switch', 'Network Interface', 'Sockets'
button_function_list = ['cpu', 'ram', 'swap', 'io', 'pcswitch', 'net_interface', 'sockets']
button_animate_list = ['cpu_animate', 'ram_animate', 'swap_animate', 'io_animate', 'pcswitch_animate', \
                       'net_interface_animate', 'sockets_animate']

f = plt.figure(figsize=(5,5), dpi=100)
#a = f.add_subplot(111)
time =[]
system_cpu = []
user_cpu = []
idle_cpu = []
free_mem = []
used_mem = []
buffer_mem = []
cached_mem = []

def gather_detail(disp, sel_buttons1):
    print(sel_buttons1)
    selected_button_list = [sel_buttons1[i].get() for i in range(len(sel_buttons1))]
    print(selected_button_list)
    client = paramiko.SSHClient()
    if disp:
        if not "us.oracle.com" in StartPage.ent_values[0].get():
            s = StartPage.ent_values[0].get()
            s += ".us.oracle.com"
            StartPage.ent_values[0].set(s)
            try:
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.load_system_host_keys()
                client.connect(StartPage.ent_values[0].get(), 22, StartPage.ent_values[1].get(), StartPage.ent_values[2].get())
            except Exception as e:
                print("Connection not established "+ e.args[0])
        #while(True):
        for i in range(len(selected_button_list)):
            if selected_button_list[i]:
                print(button_function_list[i])
                f1= eval(button_function_list[i])
                f1(client, disp)

def cpu(client, disp):
    if disp:
        while True:
            command = 'sar -u 3 1| grep -v -E "CPU|Average|^$"'
            stdin_,stdout_, stderr_ = client.exec_command(command)
            data = stdout_.readlines()[0].split()
            time.append(datetime.strptime(data[0], '%H:%M:%S'))
            user_cpu.append(data[2])
            system_cpu.append(data[4])
            idle_cpu.append(data[7])
    else:
        client.close()

def ram(client, disp):
    if disp:
        while True:
            command = 'sar -r 3 1 | grep -v -E "^[a-zA-Z]|kbmem"'
            stdin_,stdout_, stderr_ = client.exec_command(command)
            data = stdout_.readlines()[0].split()
            time.append(datetime.strptime(data[0], '%H:%M:%S'))
            free_mem.append(str((int(data[1])/1024)+(int(data[4])/1024)+(int(data[5])/1024)))
            used_mem.append(str((int(data[2])/1024)-(int(data[4])/1024)-(int(data[5])/1024)))
            buffer_mem.append(str(int(data[4])/1024))
            cached_mem.append(str(int(data[5])/1024))
    else:
        client.close()       

def cpu_animate(a,i):
    a.clear()
    print(time + user_cpu +  system_cpu)
    a.yaxis.set_major_locator(plt.MaxNLocator(10))
    a.plot(time, user_cpu, label = 'User %', color = 'r', antialiased=True)
    a.plot(time, system_cpu, label = 'System %', color = 'b', antialiased=True)
    a.plot(time, idle_cpu, label = 'Idle %', color = 'g', antialiased=True)
    plt.title("CPU usage of the host - ")
    plt.xlabel('Time',fontstyle='italic')
    plt.ylabel('CPU Utilization',fontstyle='italic')
    a.legend(loc='best', prop={'size':'small'})

def ram_animate(a,i):
    a.clear()
    print(time + user_cpu +  system_cpu)
    a.yaxis.set_major_locator(plt.MaxNLocator(10))
    a.plot(time, free_mem, label = 'Free Memory', color = 'r', antialiased=True)
    a.plot(time, used_mem, label = 'Used Memory', color = 'b', antialiased=True)
    a.plot(time, buffer_mem, label = 'Buffered Memory', color = 'g', antialiased=True)
    a.plot(time, cached_mem, label = 'Cached Memory', color = 'c', antialiased=True)
    plt.title("RAM usage Graph ")
    plt.xlabel('Time',fontstyle='italic')
    plt.ylabel('Memory (MB)',fontstyle='italic')
    a.legend(loc='best', prop={'size':'small'})

def animate(i):
    global f
    selected_button_list = [StartPage.sel_buttons[i].get() for i in range(len(StartPage.sel_buttons))]
    button_len = sum(selected_button_list)
    sel_indices = [i for i, x in enumerate(selected_button_list) if x]
    '''for n in range(button_len):
        if n%2==0:
            ax = f.add_subplot(n/2,2, sharex = True)
            if n == 2:
                button_animate_list[sel_indices[0]](ax[0],i)
                button_animate_list[sel_indices[1]](ax[1],i)
            else:
                index = 0
                for j in range(n/2):
                    for k in range(n/2):
                        button_animate_list[sel_indices[index]](ax[j][k],i)
                        index +=1
                    index +=1
        else:
            if n == 1:
                ax = f.add_subplot()
                button_animate_list[sel_indices[0]](ax,i)
            else:
                ax = f.add_subplot(n%2,2, sharex = True)
                index = 0
                for j in range(n/2):
                    for k in range(n/2):
                        button_animate_list[sel_indices[index]](ax[j][k],i)
                        index +=1
                    index +=1
    '''
    cols = 3
    total_subplot = button_len
    rows = total_subplot // cols
    rows += total_subplot % cols
    position = range(1, total_subplot +1)
    ind = 0
    for k in range(total_subplot):
        ax = f.add_subplot(rows, cols, position[k])
        f1 = eval(button_animate_list[sel_indices[ind]])
        ani = animation.FuncAnimation(f, f1, interval = 1000)
        plt.show()
        #f1(ax, i)
        ind += 1

class GUI(tk.Tk):
    frames = {}
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Live Monitoring Tool")

        container = tk.Frame(self)
        container.master.geometry('1024x650')
        container.pack(side='top', fill='both', expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)


        #self.frames = {}
        for frame in (StartPage, PageOne):
            f = frame(container, self)
            self.frames[frame] = f
            f.grid(row = 0, column = 0, sticky = 'nsew')

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise() 
        
    def start_threading():
        t1 = Thread(target = gather_detail, args =(True,StartPage.sel_buttons))
        t1.setDaemon(True)
        t1.start()

class StartPage(tk.Frame):
    ent_values =[]
    sel_buttons = []
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, background = 'ivory2')
        label = tk.Label(self, text = "Provide the following inputs to start monitoring", font=("Helvetica", 25), fg = 'turquoise')
        label.pack()

        self.ents = self.makeform(self, fields)
        self.bind('<Return>', (lambda event, e= self.ents: self.fetch(e)))

        self.butents = self.makechkbutton(self, sel_fields)
        self.bind('<Return>', lambda event, e=self.butents: self.fetch(e))

        B1 = tk.Button(self, text = "Quit", command = self.quit)
        B1.pack(side = 'right', padx = 10, pady = 10)

        B2 = tk.Button(self, text = "Next", command = lambda : self.show_frame(PageOne, controller))
        B2.pack(side = 'right', padx = 10, pady =10)

    def fetch(self, entries):
        for entry in entries:
            field = entry[0]
            text = entry[1].get()
            print("%s: %s" %(field, text))

    def makeform(self, master, field):
        entries = []
        for entry in field:
            v = tk.StringVar()
            row = tk.Frame(master)
            label = tk.Label(row, text = entry, width = 15, anchor = 'w', fg='azure',bg='medium sea green')
            ent = tk.Entry(row,bg = 'gray89', bd = 3, fg = 'purple1', textvariable = v, \
                           font = ("Helvetica", 15) )
            StartPage.ent_values.append(v)
            row.pack(side='top', fill='both')
            label.pack(side='left', padx = 25, pady =10)
            ent.pack(side='left', fill='both', expand = True, padx = 5, pady = 5)
            entries.append((entry,ent))
        return entries

    def makechkbutton(self, master, field):
        entries = []
        for entry in field:
            v = tk.BooleanVar()
            row = tk.Frame(master)
            chk = tk.Checkbutton(row, text = entry, var = v, relief = 'groove', height = 2, width = 20,\
                                 font = ('MS Sans Serif', 10))
            StartPage.sel_buttons.append(v)
            row.pack(side='top', fill='both')
            chk.pack()
            entries.append((entry,chk))
        return entries

    def show_frame(self, page, cont):
        page.display_graph(page, True)

class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, background = 'ivory2')
        L1 = tk.Label(self, text = "Graph Monitoring")
        L1.pack()

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill='both', expand = True)

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill = tk.BOTH, expand = True)

        B1 = tk.Button(self, text = "Quit", command = self.exit)
        B1.pack(side = 'right', padx = 10, pady =10)

        B2 = tk.Button(self, text = "Back", command = lambda: controller.show_frame(StartPage))
        B2.pack(side='right', padx = 10, pady=10)

    def display_graph(self, disp):
        frame = GUI.frames[PageOne]
        frame.tkraise()
        #t1 = Thread(target = gather_detail, args =(True,StartPage.sel_buttons))
        #t1.setDaemon(True)
        #t1.start()
        if not disp:
            gather_detail(False)

    def exit(self):
        self.display_graph(False)
        self.quit()        
        

        


app = GUI()
#ani = animation.FuncAnimation(f, animate, interval=1000)
app.mainloop()