# import easygui
#
#
# def get_from_input(text, possible_values):
#     ask = True
#     while ask:
#         val = input(text)
#         ask = not(val in possible_values)
#     return val
#
#
# def get_path(msg=None, title=None, default='*', filetypes=None, multiple=False, to_list=False):
#     path = ''
#     while path == '':
#         path = easygui.fileopenbox(msg=msg, title=title, default=default, filetypes=filetypes, multiple=multiple)
#         if to_list and not isinstance(path, list):
#             return [path]
#     return path
#
#
# def get_dir(msg=None, title=None, default='*'):
#     path = ''
#     while path == '':
#         path = easygui.diropenbox(msg=msg, title=title, default=default)
#     return path
#
#
# import tkinter as tk
#
#
# def write_slogan():
#     print("Tkinter is easy to use!")
#
#
# root = tk.Tk()
# frame = tk.Frame(root)
# frame.pack()
#
# button = tk.Button(frame,
#                    text="QUIT",
#                    fg="red",
#                    command=quit)
# button.pack(side=tk.LEFT)
# slogan = tk.Button(frame,
#                    text="Hello",
#                    command=write_slogan)
# slogan.pack(side=tk.LEFT)

import ntpath
from tkinter import *
from tkinter import filedialog
from tkinter import ttk


class GUI:
    def __init__(self, master):
        self.master = master
        master.title("KPI Builder")

        self.date_frame = ttk.LabelFrame(master=self.master, text='Date Selection', width=1000)
        ttk.Label(master=self.date_frame, text=str('Select current date month/year:'), width=64).grid(row=0, column=0,
                                                                                                      padx=10)
        self.month_str = StringVar(master=self.date_frame, value=1)
        self.month_cbb = ttk.Combobox(master=self.date_frame,
                                      values=list(range(1, 13)),
                                      textvariable=self.month_str,
                                      state='readonly',
                                      width=6)

        self.year_str = StringVar(master=self.date_frame, value=2020)
        self.year_cbb = ttk.Combobox(master=self.date_frame,
                                     values=list(range(2000, 2050)),
                                     textvariable=self.year_str,
                                     state='readonly',
                                     width=10)

        self.month_cbb.grid(row=0, column=1, padx=10, pady=10)
        self.year_cbb.grid(row=0, column=2, padx=10, pady=10)
        self.date_frame.grid(row=0, column=0, columnspan=5, padx=10, pady=10)

        self.label_frame_pc = add_files_panel(self.master, filetype='Products', text='Product Catalogues')
        self.label_frame_pc.grid(row=1, column=0, columnspan=5, padx=10, pady=10)

        self.label_frame_rr = add_files_panel(self.master, filetype='Reviews', text='Ratings and Reviews')
        self.label_frame_rr.grid(row=2, column=0, columnspan=5, padx=10, pady=10)

        self.label_frame_op = output_panel(self.master, text='Output Directory')
        self.label_frame_op.grid(row=3, column=0, columnspan=5, padx=10, pady=10)

        self.buttons_frame = ttk.Frame(self.master)
        self.run_button = ttk.Button(master=self.buttons_frame, text='Run', command=self.run)
        self.exit_button = ttk.Button(master=self.buttons_frame, text='Exit', command=self.quit)

        self.buttons_frame.grid(row=4, column=0, columnspan=5, padx=10, pady=10)
        self.run_button.grid(row=0, column=1, pady=15)
        self.exit_button.grid(row=0, column=2, pady=15)

    def quit(self):
        self.master.destroy()

    def run(self):
        self.month = self.month_str.get()
        self.year = self.year_str.get()
        self.product_paths = []
        for path_pannel in self.label_frame_pc.path_pannels:
            if path_pannel.path != '':
                self.product_paths.append((path_pannel.path, path_pannel.type_str.get()))
        self.reviews_paths = []
        for path_pannel in self.label_frame_rr.path_pannels:
            if path_pannel.path != '':
                self.reviews_paths.append((path_pannel.path, path_pannel.type_str.get()))
        self.output_dir = self.label_frame_op.output_str.get()
        self.master.destroy()


class output_panel(LabelFrame):
    def __init__(self, master, cnf={}, **kw):
        super().__init__(master=master, cnf=cnf, **kw)
        self.output_str = StringVar()
        self.output_entry = ttk.Entry(master=self, textvariable=self.output_str, width=77)
        self.output_entry.grid(row=0, column=0, padx=10, pady=10)

        self.browse_button = ttk.Button(master=self, text='Browse...', command=self.get_op_path)
        self.browse_button.grid(row=0, column=1, padx=10, pady=10)
        self.op_path = ""

    def get_op_path(self):
        path = filedialog.askdirectory()
        self.output_str.set(path)


class add_files_panel(LabelFrame):
    def __init__(self, master, filetype, cnf={}, **kw):
        super().__init__(master=master, cnf=cnf, **kw)
        self.filetype = filetype
        self.add_button = ttk.Button(master=self, text='Add File', width=20, command=self.add_file)
        self.add_button.grid(row=0, column=0, padx=10, pady=10)
        self.path_pannels = []
        Label(self, width=83).grid(row=100, column=0)

    def add_file(self):
        path = filedialog.askopenfilename(initialdir="/", title="Select file",
                                          filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        if path == '':
            return
        else:
            path_pannel = added_file(master=self, path=path)
            path_pannel.grid(row=len(self.path_pannels) + 4, column=0)
            self.path_pannels.append(path_pannel)
            self.path_pannels


class added_file(Frame):
    def __init__(self, path, master=None, cnf={}, **kw):
        super().__init__(master=master, cnf=cnf, **kw)
        self.path = path
        self.filename = ntpath.basename(path)
        self.filename_label = ttk.Label(master=self, text=self.filename, width=50)
        self.type_str = StringVar(master=self, value='Cosmetics')
        self.type_cbb = ttk.Combobox(master=self, values=["Cosmetics", "Skincair"], textvariable=self.type_str,
                                     state='readonly')
        self.del_button = ttk.Button(master=self, text='Delete', command=self.delete)
        self.filename_label.grid(row=0, column=0, padx=10, pady=1)
        self.type_cbb.grid(row=0, column=1, padx=10, pady=1)
        self.del_button.grid(row=0, column=2, padx=10, pady=1)

    def delete(self):
        self.path = ''
        self.type_str.set('')
        self.grid_forget()
