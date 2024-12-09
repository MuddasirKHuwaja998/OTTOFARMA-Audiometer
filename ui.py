import tkinter as tk
import tkinter.ttk as ttk
import threading
from tkinter import messagebox, filedialog
import ttkbootstrap as tb
from PIL import Image, ImageTk
import os
import csv
import time
import random
from .instructions import *
from .config import *
from PIL import Image


class App(tb.Window):

    def __init__(self, familiarization_func:callable, program_funcs:dict, calibration_funcs:list, progress_func:callable):
        """Creats Main application window. Contains all pages and controls the flow of the program.

        Args:
            familiarization_func (function): function to be called for familiarization
            audiogram_func (function): function to be called for creating audiogram
            program_funcs (dict of str:function): function(s) to be called for the main program
            calibration_funcs (list function): list of function(s) for calibration in this order: start, next, repeat, stop, set_level
        """
        themename = self.get_theme()
        super().__init__(themename=themename)

        # General theme settings
        self.title("Sound Player")
        self.geometry(GEOMETRY)
        self.minsize(650,650)
        self.attributes('-fullscreen', True)
        self.bind("<Escape>", self.exit_fullscreen)

        self.save_path = os.path.join(os.getcwd())
        
        # Ensure the default save path exists
        os.makedirs(self.save_path, exist_ok=True)

        self.set_icon("otofarmaspa_logo.png") #change the icon maybe? #TODO
        
        # Dictionary to store all pages
        self.program_funcs = program_funcs
        self.frames = {}
        self.binaural_test = False

        # Interactive Pages
        for F in (MainMenu, FamiliarizationPage, ProgramPage, ResultPage):
            frame = F(self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Calibration separately to give it its functions
        frame = CalibrationPage(self, calibration_funcs)
        self.frames[CalibrationPage] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        # View during familiarization
        frame = DuringFamiliarizationView(self, familiarization_func, progress_func)
        self.frames[DuringFamiliarizationView] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        # View during programs
        for name, program_func in program_funcs.items():
            frame = DuringProcedureView(self, 
                                        program_func, progress_func,
                                        text="Programm is  running....")
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show MainMenu first
        self.show_frame(MainMenu)

        # Create menubar
        self.create_menubar()

        # Variable for threading
        self.process_done = False

        # Override the close button protocol
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def create_menubar(self):
        """Creates a menubar with options for changing the theme and exiting the program.
        """
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Pagina iniziale", command=lambda: self.show_frame(MainMenu))
        file_menu.add_command(label="Cambia posizione di archiviazione", command=self.change_save_path)

        ChangeTheme = tk.Menu(file_menu, tearoff=0)
        ChangeTheme.add_command(label="light", command=lambda: self.change_theme(LIGHT_THEME))
        ChangeTheme.add_command(label="dark", command=lambda: self.change_theme(DARK_THEME))
        
        file_menu.add_cascade(label="Cambia tema", menu=ChangeTheme)
        file_menu.add_separator()
        file_menu.add_command(label="Chiudere il software Audiometer?", command=self.on_closing)
        
        menubar.add_cascade(label="Impostazioni", menu=file_menu)

    def change_theme(self, theme_name:str):
        """Changes to the specified theme.

        Args:
            theme_name (str): name of the theme to change
        """
        current_theme = self.style.theme_use()

        if current_theme == theme_name:
            messagebox.showwarning("Oops..", "Questo tema è già in uso.")
        else:
            self.style.theme_use(theme_name)

            # change in settings.csv file
            filename = "settings.csv"
            fieldnames = ['file path', 'theme']

            # Read all rows from the settings.csv file
            with open(filename, mode='r', newline='') as file:
                dict_reader = csv.DictReader(file)
                rows = list(dict_reader)

            # Update the relevant row
            rows[0]['theme'] = theme_name

            # Write all rows back to the CSV file
            with open(filename, mode='w', newline='') as file:
                dict_writer = csv.DictWriter(file, fieldnames=fieldnames)
                dict_writer.writeheader()
                dict_writer.writerows(rows)
    
    def get_theme(self):
        """Gets currently selected theme from settings.csv file.

        Returns:
            str: name of light theme or name of dark theme
        """    
        file_name = "settings.csv"

        with open(file_name, mode='r') as file:
            reader = csv.DictReader(file)
            settings = next(reader)
            if settings['theme'] == LIGHT_THEME:
                return LIGHT_THEME
            elif settings['theme'] == DARK_THEME:
                return DARK_THEME
            else:
                return LIGHT_THEME  

    def exit_fullscreen(self, event=None):
        """Exits fullscreen mode.
        """
        self.attributes('-fullscreen', False)

    def set_icon(self, path):
        """Sets the window icon using Pillow.
        """
        img = Image.open(path)
        photo = ImageTk.PhotoImage(img)
        self.iconphoto(False, photo)          

    def show_frame(self, page):
        """Shows frame for the given page name.

        Args:
            page(class): class of the page to be shown
        """
        frame = self.frames[page]
        frame.tkraise()

    def wait_for_process(self, process, callback):
        """Starts a process in a new thread and calls a callback function when the process is done.

        Args:
            process (function): function to be called
            callback (function): function to be called when process is done
        """
        t = threading.Thread(target=self.run_process, args=(process, callback))
        t.daemon = True
        t.start()

    def run_process(self, process, callback):
        """Runs a process and calls a callback function when the process is done.

        Args:
            process (function): function to be called
            callback (function): function to be called when process is done
        """
        process()
        self.process_done = True
        self.after(100, callback)

    def change_save_path(self):
        """Asks the user to select a folder to save the files. Changes settings.csv file accordingly.
        """
        new_path = filedialog.askdirectory(title="Select Folder to Save Files")
        if new_path:

            # change in settings.csv file
            filename = "settings.csv"
            fieldnames = ['file path', 'theme']

            # Read all rows from the settings.csv file
            with open(filename, mode='r', newline='') as file:
                dict_reader = csv.DictReader(file)
                rows = list(dict_reader)

            # Update the relevant row
            rows[0]['file path'] = new_path

            # Write all rows back to the CSV file
            with open(filename, mode='w', newline='') as file:
                dict_writer = csv.DictWriter(file, fieldnames=fieldnames)
                dict_writer.writeheader()
                dict_writer.writerows(rows)
            
            self.save_path = new_path

            messagebox.showinfo("Speicherort geändert", f"Neuer Speicherort: {self.save_path}")

    def on_closing(self):
        """Asks for confirmation before closing the program.
        """
        if messagebox.askyesno(title="Esentato", message="Vuoi davvero uscire dal programma?"):
            self.destroy()

    def get_images_in_path(self, directory, image_extensions=[".png", ".jpg", ".jpeg", ".gif", ".bmp"]):
        """Gets a list of image files in the specified directory.

        Args:
        directory (str): The path to the directory to check.
        image_extensions (list): List of image file extensions to check for.

        Returns:
        list: List of image file paths if any image files are found, False otherwise.
        """
        if not os.path.exists(directory):
            return False

        image_files = [os.path.join(directory, file) for file in os.listdir(directory) if any(file.lower().endswith(ext) for ext in image_extensions)]
        return image_files if image_files else False


class MainMenu(ttk.Frame):

    def __init__(self, parent):
        """Creates the Main menu page.
        """
        super().__init__(parent)
        self.parent = parent
        self.button_width = 25
        self.start_button = None
        self.binaural_test = tk.BooleanVar()
        self.use_calibration = tk.BooleanVar(value=True)
        self.selected_option = None
        self.proband_number = ""
        self.create_widgets()

    def create_widgets(self):
        """Creates the widgets for the page.
        """
        self.proband_number_label = ttk.Label(self, text="Numero ID del paziente:",font=(FONT_FAMILY, TEXT_SIZE))
        self.proband_number_label.pack(padx=10, pady=10)
        self.proband_number_entry = ttk.Entry(self,width=self.button_width+1)
        self.proband_number_entry.pack(padx=10, pady=10)

        self.gender_label = ttk.Label(self, text="Genere (facoltativo):", font=(FONT_FAMILY, TEXT_SIZE))
        self.gender_label.pack(padx=10, pady=10)
        self.gender_dropdown = ttk.Combobox(self, values=["Maschio", "Femmina", "Diverso", "Non specificato"], state="readonly", width=self.button_width - 1)
        self.gender_dropdown.set("Genere...")
        self.gender_dropdown.pack(padx=10, pady=10)

        self.age_label = ttk.Label(self, text="Età (facoltativo):", font=(FONT_FAMILY, TEXT_SIZE))
        self.age_label.pack(padx=10, pady=10)
        self.age_entry = ttk.Entry(self, width=self.button_width+1)
        self.age_entry.pack(padx=10, pady=10)

        self.label = ttk.Label(self, text="\nSeleziona un Programma", font=(FONT_FAMILY, TEXT_SIZE))
        self.label.pack(pady=10)

        # Dropdown menu
        options = list(self.parent.program_funcs.keys())
        self.dropdown = ttk.Combobox(self, values=options, state="readonly", width=self.button_width - 1)
        self.dropdown.set("Select test...")
        self.dropdown.pack(pady=10)
        self.dropdown.bind("<<ComboboxSelected>>", self.on_option_selected)

        self.binaural_button = ttk.Checkbutton(self, 
                                         text="Test Binaurale (entrambi gli orecchi)", 
                                         variable=self.binaural_test)
        self.binaural_button.pack(pady=10)

        # Use calibration button
        self.cal_button = ttk.Checkbutton(self, 
                                         text="Utilizzare i valori dell'ultima calibrazione", 
                                         variable=self.use_calibration)
        self.cal_button.pack(pady=10, side="bottom")

        # Headphone selection
        self.headphone_dropdown = ttk.Combobox(self, values=self.get_headphone_options(), state="readonly", width=self.button_width - 1)
        self.headphone_dropdown.set("Sennheiser_HDA200")
        self.headphone_dropdown.pack(padx=10, pady=10, side="bottom")
        self.headphone_label = ttk.Label(self, text="Cuffie:", font=(FONT_FAMILY, TEXT_SIZE))
        self.headphone_label.pack(padx=10, pady=10, side="bottom")

    def get_headphone_options(self):
        """Reads all possible headphone models from retspl.csv file.

        Returns:
            list of str: all headphone models listed in retspl.csv
        """
        file_name = 'retspl.csv'
        
        # Check if the CSV file exists
        if not os.path.isfile(file_name):
            messagebox.showwarning("Attenzione", 'il file "{file_name}" non è stato trovato.')
            return
        
        headphone_options = []

        try:
            with open(file_name, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    headphone_options.append(row['headphone_model'])
                    headphone_options = list(set(headphone_options))
                    headphone_options.append("AirPods")  # Add AirPods option
                    headphone_options.append("Altra")    # Add Other option

            return headphone_options
        except Exception as e:
            messagebox.showwarning("Warning", f'Error reading file "{file_name}": {e}')
            return

    def on_option_selected(self, event):
        """Changes state of buttons and show start button depending on procedure selected.
        """
        self.selected_option = self.dropdown.get()
        self.show_start_button()
        if self.selected_option == "calibrazione":
            self.cal_button.config(state=tk.DISABLED)
            self.binaural_button.config(state=tk.DISABLED)
            self.gender_dropdown.config(state=tk.DISABLED)
            self.proband_number_entry.config(state=tk.DISABLED)
        else:
            self.cal_button.config(state=tk.NORMAL)
            self.binaural_button.config(state=tk.NORMAL)
            self.gender_dropdown.config(state=tk.NORMAL)
            self.proband_number_entry.config(state=tk.NORMAL)    

    def show_start_button(self):
        """Shows start button if not already visible.
        """
        if self.start_button is None:
            self.start_button = ttk.Button(self,
                                           text="Inizia il test",
                                           command=self.go_to_next_page,
                                           width=self.button_width)
            self.start_button.pack(pady=10)


    def go_to_next_page(self):
        """Go to next page depending on selected options.
        """
        if self.selected_option == "calibration":
            self.parent.show_frame(CalibrationPage)
            
        else:
            self.proband_number = self.proband_number_entry.get()
            if not self.proband_number:
                messagebox.showwarning("Attenzione", "Inserisci un ID paziente.")
                return
            
            # check if valide age is entered
            if self.age_entry.get():
                try:
                    i = int(self.age_entry.get())
                    if i > 110 or i < 0:
                        messagebox.showwarning("Attenzione", "Inserisci un numero valido per l'età o niente")
                        return
                except:
                    messagebox.showwarning("Attenzione", "Inserisci un numero valido per l'età o niente")
                    return

            proband_folder = os.path.join(self.parent.save_path, self.proband_number)
            pics = self.parent.get_images_in_path(proband_folder)
            if pics:
                if messagebox.askyesno("L'argomento esiste", "Ci sono già risultati per questo numero di argomento. Vuoi visualizzarli?"):
                    results_page = self.parent.frames[ResultPage]
                    results_page.display_images(self.proband_number)
                    self.parent.show_frame(ResultPage)
                    return

            self.parent.show_frame(FamiliarizationPage)


class FamiliarizationPage(ttk.Frame):

    def __init__(self, parent):
        """Creates Page for starting the familiarization process.

        Args:
            parent (App): parent application
        """
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()


    def create_widgets(self):
        """Creates the widgets for the page.
        """
        button_width = 25 

        self.label = ttk.Label(self, text=text_Familiarization, font=(FONT_FAMILY, SUBHEADER_SIZE))
        self.label.pack(padx=10, pady=10)
        self.play_button = ttk.Button(self, 
                                      text="Inizia l'Acclimatamento", 
                                      command=self.run_familiarization, 
                                      width=button_width)
        self.play_button.pack(padx=10, pady=10)
        self.go_back_button = ttk.Button(self, 
                                         text="Indietro", 
                                         command=lambda: self.parent.show_frame(MainMenu), 
                                         width=button_width)
        self.go_back_button.pack(padx=10, pady=10)

        for widget in self.winfo_children():
            widget.pack_configure(anchor='center')

    def run_familiarization(self):
        """Runs the familiarization process and goes to the next page.
        """
        self.use_calibration = self.parent.frames[MainMenu].use_calibration.get()
        self.parent.show_frame(DuringFamiliarizationView)
        
        gender = self.parent.frames[MainMenu].gender_dropdown.get()
        if gender == "Geschlecht..." or gender == "Not specified":
            gender = ""

        age = self.parent.frames[MainMenu].age_entry.get()

        self.parent.wait_for_process(lambda: self.parent.frames[DuringFamiliarizationView].program(id=self.parent.frames[MainMenu].proband_number, 
                                                                                                   calibrate=self.use_calibration, 
                                                                                                   gender=gender,
                                                                                                   age=age), 
                                     lambda: self.parent.show_frame(ProgramPage))
        time.sleep(0.001)
        self.update()
       
        counter = 3000 # set a high value so that progress bar is updated once at the beginning
        sleep_time = random.uniform(0.1, 0.5) # random time in seconds between 0.1 and 0.5 to update progress bar
        
        while self.parent.frames[DuringFamiliarizationView].progress_var.get() < 100 and not self.parent.process_done:
            progress = int(self.parent.frames[DuringFamiliarizationView].get_progress() * 100)
            if counter >= sleep_time * 1000:
                self.parent.frames[DuringFamiliarizationView].progress_var.set(progress)
                counter = 0
            time.sleep(0.001)
            counter += 1
            self.update()
        
        self.parent.process_done = False


class ProgramPage(ttk.Frame):

    def __init__(self, parent):
        """Creates Page for starting the main program.

        Args:
            parent (App): parent application
        """
        super().__init__(parent)
        self.parent = parent
        self.selected_option = None 
        self.create_widgets()

    def create_widgets(self):
        """Creates the widgets for the page.
        """
        self.start_button = ttk.Button(self, text="Inizia il processo", command=self.run_program)
        self.start_button.pack(padx=10, pady=200)
    
        for widget in self.winfo_children():
            widget.pack_configure(anchor='center')

    def run_program(self):
        """Runs the main program.
        """
        self.selected_option = self.parent.frames[MainMenu].selected_option
        self.binaural_test = self.parent.frames[MainMenu].binaural_test.get()
        self.use_calibration = self.parent.frames[MainMenu].use_calibration.get()
        self.parent.show_frame(self.selected_option)

        self.parent.wait_for_process(lambda: self.parent.frames[self.selected_option].program(self.binaural_test), self.show_results)

        
        time.sleep(0.001)
        self.update()
        
        counter = 3000 # set a high value so that progress bar is updated once at the beginning
        sleep_time = random.uniform(1, 2.5) # random time in seconds between 1 and 2.5 to update progress bar
        
        while self.parent.frames[self.selected_option].progress_var.get() < 100 and not self.parent.process_done:
            progress = int(self.parent.frames[self.selected_option].get_progress() * 100)
            if counter >= sleep_time * 1000:
                self.parent.frames[self.selected_option].progress_var.set(progress)
                counter = 0
            time.sleep(0.001)
            counter += 1
            self.update()
        
        self.parent.process_done = False

    def show_results(self):
        """Shows the results page with (all) images.
        """
        proband_number = self.parent.frames[MainMenu].proband_number
        results_page = self.parent.frames[ResultPage]
        results_page.display_images(proband_number)
        self.parent.show_frame(ResultPage)


class DuringFamiliarizationView(ttk.Frame):

    def __init__(self, parent, familiarization_func, progress_func):
        """Creates View during familiarization process.
        
        Args:
            parent (App): parent application
            familiarization_func (function): function to be called for familiarization
            progress_func (function): function to get the progress of the current process
        """
        
        super().__init__(parent)
        self.parent = parent
        self.program = familiarization_func
        self.get_progress = progress_func 
        self.text = "L'ambientamento è in corso..."
        self.create_widgets()


    def create_widgets(self):
        """Creates the widgets for the view.
        """
        self.info = ttk.Label(self, text=self.text)
        self.info.pack(padx=10, pady=10)
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100, length=300)
        self.progress_bar.pack(padx=10, pady=100)


class DuringProcedureView(ttk.Frame):

    def __init__(self, parent, program_func, progress_func, text):
        """Creates View during main program.

        Args:
            parent (App): parent application
            program_func (function): function to be called for the main program
            progress_func (function): function to get the progress of the current process
            text (str): text to be displayed
        """
        super().__init__(parent)
        self.parent = parent
        self.program = program_func
        self.get_progress = progress_func  
        self.text = text
        self.create_widgets()

    def create_widgets(self):
        """Creates the widgets for the view.
        """
        self.info = ttk.Label(self, text=self.text)
        self.info.pack(padx=10, pady=10)
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100, length=300)
        self.progress_bar.pack(padx=10, pady=100)


class ResultPage(ttk.Frame):

    def __init__(self, parent):
        """Creates Page for showing the results of the program.

        Args:
            parent (App): parent application
        """
        super().__init__(parent)
        self.parent = parent

        self.create_widgets()

    def create_widgets(self):
        """Creates the widgets for the view.
        """
        self.info = ttk.Label(self, text="L'ambientamento è in corso...", font=(FONT_FAMILY, HEADER_SIZE))
        self.info.pack(padx=10, pady=10)

        # Set the title on the parent window
        self.parent.title("Audiogram")

        # Create a frame for the images
        self.image_frame = ttk.Frame(self)
        self.image_frame.pack(anchor="center")   #,fill="both", expand=True)

        # Button to go back to the main menu
        self.BackToMainMenu = ttk.Button(self, text="Torna alla", command=lambda: self.parent.show_frame(MainMenu))
        self.BackToMainMenu.pack(padx=10, pady=10)

    def display_images(self, folder_name):
        """Display all images in the given folder.
        
        Args:
            folder_name (str): name of the folder containing the images
        """
        folder_path = os.path.join(self.parent.save_path, folder_name)
        for widget in self.image_frame.winfo_children():
            widget.destroy()
        
        pics = self.parent.get_images_in_path(folder_path)
        if pics:
            for file in pics:
                img = Image.open(file)
                photo = ImageTk.PhotoImage(img)

                label = ttk.Label(self.image_frame, image=photo)
                label.image = photo
                label.pack(padx=10, pady=10, side="left")

    def back_to_MainMenu(self):
        """Goes back to main menu.
        """
        self.parent.show_frame(MainMenu)


class CalibrationPage(ttk.Frame):

    def __init__(self, parent, calibration_funcs):
        """Creates Page for calibrating the audiometer.

        Args:
            parent (App): parent application
            calibration_funcs (list function): list of function(s) for calibration in this order: start, next, repeat, stop, set_level
        """
        super().__init__(parent)
        self.parent = parent
        self.cal_start = calibration_funcs[0]
        self.cal_next = calibration_funcs[1]
        self.cal_repeat = calibration_funcs[2]
        self.cal_stop = calibration_funcs[3]
        self.cal_setlevel = calibration_funcs[4]
        self.create_widgets()
        self.finished = False

    def create_widgets(self):
        """Creates the widgets for the page.
        """
        button_width = 25 

        self.intro = ttk.Label(self, text=text_calibration, font=(FONT_FAMILY, SUBHEADER_SIZE))
        self.intro.pack(padx=10, pady=10)
        
        self.level_label = ttk.Label(self, text="Value in dBHL at which calibration is to be carried out:", font=(FONT_FAMILY, SUBHEADER_SIZE))
        self.level_label.pack(padx=10, pady=10)
        
        self.level_entry_var = tk.StringVar()
        self.level_entry_var.set("10")
        self.level_entry = ttk.Entry(self,width=button_width-10, textvariable=self.level_entry_var)
        self.level_entry.pack(padx=10, pady=10)
        
        self.start_button = ttk.Button(self, 
                                      text="Start calibration", 
                                      command=self.start_calibration, 
                                      width=button_width)
        self.start_button.pack(padx=10, pady=10)
        
        self.next_button = ttk.Button(self, 
                                      text="Next Frequency", 
                                      command=self.next_frequency, 
                                      width=button_width,
                                      state=tk.DISABLED)
        self.next_button.pack(padx=10, pady=10)
        
        self.repeat_button = ttk.Button(self, 
                                         text="Repeat Frequency", 
                                         command=self.repeat_frequency, 
                                         width=button_width,
                                         state=tk.DISABLED)
        self.repeat_button.pack(padx=10, pady=10)
        
        self.stop_button = ttk.Button(self, 
                                         text="Stop playing", 
                                         command=self.stop_playing, 
                                         width=button_width,
                                         state=tk.DISABLED)
        self.stop_button.pack(padx=10, pady=10)
        
        self.back_button = ttk.Button(self, 
                                         text="Back to main menu", 
                                         command=lambda: self.parent.show_frame(MainMenu), 
                                         width=button_width) # TODO Kalibrierung resetten, damit man sie dann wieder von vorne anfangen kann
        self.back_button.pack(padx=10, pady=20)

        self.spacer_frame = tk.Frame(self, width=20, height=80)
        self.spacer_frame.pack()

        self.current_freq_var = tk.StringVar(value="Current frequency:")
        self.current_freq = ttk.Label(self, textvariable=self.current_freq_var, font=(FONT_FAMILY, SUBHEADER_SIZE))
        self.current_freq.pack(padx=10, pady=10)
        
        self.level_expected_var = tk.StringVar(value="sound pressure level (soll):")
        self.level_expected_label = ttk.Label(self, textvariable=self.level_expected_var, font=(FONT_FAMILY, SUBHEADER_SIZE))
        self.level_expected_label.pack(padx=10, pady=10)
        
        self.level_measured_label = ttk.Label(self, text="Measured sound pressure level in dB:", font=(FONT_FAMILY, SUBHEADER_SIZE))
        self.level_measured_label.pack(padx=10, pady=10)
        self.level_measured_var = tk.StringVar()
        self.level_measured_entry = ttk.Entry(self, width=button_width-10, 
                                              font=(FONT_FAMILY, SUBHEADER_SIZE), state=tk.DISABLED,
                                              textvariable=self.level_measured_var)
        self.level_measured_entry.pack(padx=10, pady=10)

        for widget in self.winfo_children():
            widget.pack_configure(anchor='center')

    def start_calibration(self):
        """Starts the calibration process and change state of buttons."""
        try:
            current_freq, current_spl = self.cal_start(float(self.level_entry_var.get()))
        except:
            messagebox.showwarning("Warning", 'Please enter a number.')
            return
        
        self.start_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.NORMAL)
        self.repeat_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        self.level_measured_entry.config(state=tk.NORMAL)

        self.current_freq_var.set("Current frequency:" + str(current_freq) + " Hz")
        self.level_expected_var.set("sound pressure level (soll): " + str(current_spl) + " dB")

    def next_frequency(self):
        """Sets previously entered level, then get next frequency and play it."""
        try:
            if self.level_measured_var.get() != "":
                self.cal_setlevel(float(self.level_measured_var.get()))
            else:
                messagebox.showwarning("Warnung", 'Please enter a number for "measured sound pressure level".')
                return    
        
        except ValueError:
            messagebox.showwarning("Warnung", 'Please enter a number for "measured sound pressure".')
            return
        
        self.level_measured_var.set("")
        more_freqs, current_freq, current_spl = self.cal_next()
       
        # Change Button when last frequency
        if not more_freqs:
            # Grey out all buttons when finished
            if self.finished:
                self.next_button.config(state=tk.DISABLED)
                self.repeat_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.DISABLED)
                self.level_measured_entry.config(state=tk.DISABLED)
                messagebox.showwarning("Calibration completed.", "Calibration completed successfully. File saved as calibration.csv")
                return
            
            self.next_button.config(text="Complete calibration")
            self.finished = True

        self.current_freq_var.set("Current frequency: " + str(current_freq) + " Hz")
        self.level_expected_var.set("sound pressure level (target): " + str(current_spl) + " dB")    

    def repeat_frequency(self):

        """Replays the same frequency."""

        self.cal_repeat()

    def stop_playing(self):
        """Stops playing audio."""
        self.cal_stop()

    def cal_start(self, level):
        # Dummy method to simulate calibration start. Replace with your actual logic.
        return 1000, 40  # Example frequency and SPL

    def cal_setlevel(self, level):
        # Dummy method to simulate setting level. Replace with actual logic.
        pass

    def cal_next(self):
        # Dummy method to simulate getting next frequency. Replace with your actual logic.
        return True, 2000, 30  # Example result (more frequencies, current frequency, current SPL)

    def cal_repeat(self):
        # Dummy method to simulate repeating the frequency. Replace with your actual logic.
        pass

    def cal_stop(self):
        # Dummy method to simulate stopping playback. Replace with actual logic.
        pass

def setup_ui(startfunc, programfuncs, calibrationfuncs, progressfunc):
    """
    Creates tkinter app and return it.
    
    Args:
        startfunc (function): function to be called for familiarization
        programfuncs (dict of str:function): function(s) to be called for the main program
        calibrationfuncs (list function): list of function(s) for calibration in this order: start, next, repeat, stop, set_level
        progressfunc (function): function to get the progress of the current process
    """
    app = App(startfunc, programfuncs, calibrationfuncs, progressfunc)
    return app