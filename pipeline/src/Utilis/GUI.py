import ntpath
import datetime
from tkinter import *
from tkinter import filedialog
from tkinter import ttk


class GUI:
    def __init__(self, master: Tk) -> None:
        """
        Initializes an instance of GUI.

        :param Tk master: instance of Tk (main window).
        """
        # Default entries
        self.year = datetime.datetime.now().year
        self.month = datetime.datetime.now().month
        self.product_paths = []
        self.reviews_paths = []
        self.output_dir = 'C:/'

        # GUI Construction
        self.master = master

        # Title of the window
        master.title("KPI Builder")

        # LabelFrame containing the date widgets
        self.date_frame = ttk.LabelFrame(master=self.master, text='Date Selection', width=1000)
        # Label
        ttk.Label(master=self.date_frame, text=str('Select current date month/year:'), width=64).grid(row=0, column=0,
                                                                                                      padx=10)
        # Combobox for the month
        self.month_str = StringVar(master=self.date_frame, value=self.month)
        self.month_cbb = ttk.Combobox(master=self.date_frame,
                                      values=list(range(1, 13)),
                                      textvariable=self.month_str,
                                      state='readonly',
                                      width=6)
        # Combobox for the year
        self.year_str = StringVar(master=self.date_frame, value=self.year)
        self.year_cbb = ttk.Combobox(master=self.date_frame,
                                     values=list(range(2000, 2050)),
                                     textvariable=self.year_str,
                                     state='readonly',
                                     width=10)
        # Adding the widgets for the date
        self.month_cbb.grid(row=0, column=1, padx=10, pady=10)
        self.year_cbb.grid(row=0, column=2, padx=10, pady=10)
        self.date_frame.grid(row=0, column=0, columnspan=5, padx=10, pady=10)

        # LabelFrame for the Product Catalogues files
        self.label_frame_pc = AddingFilesPanel(self.master, text='Product Catalogues')
        self.label_frame_pc.grid(row=1, column=0, columnspan=5, padx=10, pady=10)

        # LabelFrame for the Ratings and Reviews files
        self.label_frame_rr = AddingFilesPanel(self.master, text='Ratings and Reviews')
        self.label_frame_rr.grid(row=2, column=0, columnspan=5, padx=10, pady=10)

        # LabelFrame for the Output directory
        self.label_frame_op = OutputPanel(self.master, text='Output Directory')
        self.label_frame_op.grid(row=3, column=0, columnspan=5, padx=10, pady=10)

        # Button Frame
        self.buttons_frame = ttk.Frame(self.master)
        # Run Button
        self.run_button = ttk.Button(master=self.buttons_frame, text='Run', command=self.run)
        # Exit button
        self.exit_button = ttk.Button(master=self.buttons_frame, text='Exit', command=self.quit)
        # Adding the widgets for the buttons
        self.buttons_frame.grid(row=4, column=0, columnspan=5, padx=10, pady=10)
        self.run_button.grid(row=0, column=1, pady=15)
        self.exit_button.grid(row=0, column=2, pady=15)

    def quit(self) -> None:
        """
        Destroys the window.
        """
        self.master.destroy()

    def run(self) -> None:
        """
        Gets the inputs from the different widgets and destroys the window.
        """
        # Getting the month
        self.month = self.month_str.get()
        # Getting the year
        self.year = self.year_str.get()
        # Getting Product Catalogues paths and file types
        for path_panel in self.label_frame_pc.path_pannels:
            if path_panel.path != '':
                self.product_paths.append((path_panel.path, path_panel.type_str.get()))
        # Getting Ratings and Reviews paths and file types
        for path_panel in self.label_frame_rr.path_pannels:
            if path_panel.path != '':
                self.reviews_paths.append((path_panel.path, path_panel.type_str.get()))
        # Getting the Output
        self.output_dir = self.label_frame_op.output_str.get()
        # Destroy the Window
        self.master.destroy()


class OutputPanel(LabelFrame):
    """
    Subclass of LabelFrame containing widgets to get the Output directory.
    """

    def __init__(self, master: Tk, cnf={}, **kw) -> None:
        """
        Initializes an instance of OutputPanel.

        :param Tk master: Tk instance (main windows).
        :param cnf: hereditary parameters from LabelFrame.
        :param kw: hereditary parameters from LabelFrame.
        """
        super().__init__(master=master, cnf=cnf, **kw)
        # Entry for the output directory path
        self.output_str = StringVar()
        self.output_entry = ttk.Entry(master=self, textvariable=self.output_str, width=77)
        self.output_entry.grid(row=0, column=0, padx=10, pady=10)

        # Button to browse directories
        self.browse_button = ttk.Button(master=self, text='Browse...', command=self.get_op_path)
        self.browse_button.grid(row=0, column=1, padx=10, pady=10)

    def get_op_path(self) -> None:
        """
        Pops-up a window to select the output directory path.
        """
        path = filedialog.askdirectory()
        self.output_str.set(path)


class AddingFilesPanel(LabelFrame):
    """
    LabelFrame containing widgets to add input files.
    """

    def __init__(self, master: Tk, cnf={}, **kw) -> None:
        """
        Initializes a new instance of AddingFilesPanel.

        :param Tk master: Tk instance (main windows).
        :param cnf: hereditary parameters from LabelFrame.
        :param kw: hereditary parameters from LabelFrame.
        """
        super().__init__(master=master, cnf=cnf, **kw)
        self.add_button = ttk.Button(master=self, text='Add File', width=20, command=self.add_file)
        self.add_button.grid(row=0, column=0, padx=10, pady=10)
        self.path_pannels = []
        Label(self, width=83).grid(row=100, column=0)

    def add_file(self) -> None:
        """
        Adds a FilePanel to the AddingFilesPanel.
        """
        # Open a pop-up window to browse to the needed file.
        path = filedialog.askopenfilename(initialdir="/", title="Select file",
                                          filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        # If no paths have been selected, nothing happens.
        if path == '':
            return
        # Else we add the FilePanel
        else:
            path_panel = FilePanel(master=self, path=path)
            path_panel.grid(row=len(self.path_pannels) + 4, column=0)
            self.path_pannels.append(path_panel)


class FilePanel(Frame):
    """
    Subclass of Frame that contains widgets about the added files: Label of the path, the type of the file (Cosmetics,
    Skincair) and a button to delete the path.
    """

    def __init__(self, path: str, master: Tk, cnf={}, **kw) -> None:
        """
        Initializes a new instance of FilePanel.

        :param str path: path of the added file.
        :param Tk master: Tk instance (main windows).
        :param cnf: hereditary parameters from LabelFrame.
        :param kw: hereditary parameters from LabelFrame.
        """
        super().__init__(master=master, cnf=cnf, **kw)
        # Path of the added file
        self.path = path
        # Filename of the added file
        self.filename = ntpath.basename(path)

        # Label of the filename of the added file
        self.filename_label = ttk.Label(master=self, text=self.filename, width=50)

        # Combobox containing the type of the added file
        self.type_str = StringVar(master=self, value='Cosmetics')
        self.type_cbb = ttk.Combobox(master=self, values=["Cosmetics", "Skincair"], textvariable=self.type_str,
                                     state='readonly')

        # Delete button
        self.del_button = ttk.Button(master=self, text='Delete', command=self.delete)

        # Adding all the widgets to the grid
        self.filename_label.grid(row=0, column=0, padx=10, pady=1)
        self.type_cbb.grid(row=0, column=1, padx=10, pady=1)
        self.del_button.grid(row=0, column=2, padx=10, pady=1)

    def delete(self) -> None:
        """
        Deletes the added filepath and removes the widget from the grid.
        """
        self.path = ''
        self.type_str.set('')
        self.grid_forget()
