import tkinter as tk
from tkinter import ttk, messagebox, Listbox, Scrollbar, filedialog, font
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Patch

"""
Klasa Application predstavlja glavnu aplikaciju koja sadrži različite stranice. Svaka stranica je instanca neke druge klase koja predstavlja dio sučelja; 
stranica za prijavu (LoginUI), biljke (Page_plant), formular za biljke (Form_plant) i detalje o loncima (Pot_details).
Za svaku stranicu poziva se metoda place, koja stranicu postavlja na određenu lokaciju unutar prozora aplikacije, i place_forget, 
koja stranicu skriva dok ne bude potrebna. Metoda self.show_page("login") prikazuje stranicu za prijavu kao početnu stranicu kada se aplikacija pokrene.
"""

class Application(tk.Tk):
    def __init__(self, submit_login_data, flora_data, sensors_values, plant_save_callback, plant_update_callback, plant_delete_callback,):
        tk.Tk.__init__(self)
        self.login = LoginUI(self, submit_login_data)
        self.flora_data = flora_data
        self.plant = Page_plant(self)
        self.plant_form = Form_plant(self, self.plant, flora_data, plant_save_callback, plant_update_callback, plant_delete_callback,)
        self.pot_details = Pot_details(self, flora_data, sensors_values)
        self.sensors_values = sensors_values
        self.pages = {
            "login": self.login,
            "plant_page": self.plant,
            "plant_form": self.plant_form,
            "pot_details": self.pot_details
        }
        self.plant_save_callback = plant_save_callback
        self.plant_update_callback = plant_update_callback   
        self.plant_delete_callback = plant_delete_callback

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


        for page in self.pages.values():
            page.grid(row=0, column=0, sticky='nsew')
            page.grid_remove()

        
        self.show_page("login")


    def show_page(self, page_name, event=None, plant_data=None):
        for name, page in self.pages.items():
            if name == page_name:
                if name == 'plant_details' and plant_data is not None:
                    page.show_details(*plant_data)
                page.pack(side="top", fill="both", expand=True)
            else:
                page.pack_forget() 

        self.update_idletasks()


class LoginUI(tk.Frame):
    def __init__(self, master, submit_callback):
        super().__init__(master) 
        self.master = master
        self.submit_callback = submit_callback
        self.pin_var = tk.StringVar()

        
        master.title("PyFloraPosuda")
        self.master.geometry("900x900")

        self.main_frame = tk.Frame(self, bg="#94C973")
        self.main_frame.grid(sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.title_label = tk.Label(self.main_frame, text="Welcome to PyFlora!", font=("Arial", 50), fg ="white", bg="#94C973")
        self.title_label.grid(row=3, column=1, columnspan=2, pady=20)
    
        self.login_label = tk.Label(self.main_frame, text="LOG IN", font=("Arial", 30), fg ="white", bg="#94C973")
        self.login_label.grid(row=4, column=2, columnspan=2, pady=10)

        self.spacer1 = tk.Label(self.main_frame, text=" ", bg="#94C973")
        self.spacer1.grid(row=5, column=4, columnspan=2, pady=10)

        self.name_label, self.name_entry = self.create_label_entry_pair("Name:", 6)
        self.surname_label, self.surname_entry = self.create_label_entry_pair("Surname:", 7)
        self.username_label, self.username_entry = self.create_label_entry_pair("Username:", 8)

        self.password_label = tk.Label(self.main_frame, text="Password:", bg="#94C973", font=("Arial", 20), fg="white")
        self.password_label.grid(row=9, column=1, pady=10, sticky=tk.W)

        self.password_entry = tk.Entry(self.main_frame, font=("Arial", 20), show="*")
        self.password_entry.grid(row=9, column=2, columnspan=2, pady=10, sticky=(tk.W))

        self.spacer2 = tk.Label(self.main_frame, text=" ", bg="#94C973")
        self.spacer2.grid(row=10, column=4, columnspan=2, pady=10)

        self.spacer3= tk.Label(self.main_frame, text=" ", bg="#94C973")
        self.spacer3.grid(row=11, column=4, columnspan=2, pady=10)

        self.spacer4= tk.Label(self.main_frame, text=" ", bg="#94C973")
        self.spacer4.grid(row=12, column=5, columnspan=2, pady=10)

        self.submit_button = tk.Button(self.main_frame, text="SUBMIT", bg="#76B947", font=("Arial", 20), fg="white", command=self.submit)
        self.submit_button.grid(row=12, column=2, columnspan=2, pady=20)


    def create_label_entry_pair(self, text, row):
        """
        Funkcija za kreiranje label i entrija koji se učestalo koriste
        """
        label = tk.Label(self.main_frame, text=text, bg="#94C973", font=("Arial", 20), fg="white")
        label.grid(row=row, column=1, pady=10, sticky=tk.W)

        entry = tk.Entry(self.main_frame, font=("Arial", 20))
        entry.grid(row=row, column=2, columnspan=2, pady=10, sticky=(tk.W))

        return label, entry
        

    def submit(self):
        """
        Ovi pozivi metode get() dohvaćaju vrijednosti koje korisnik unese u polja za unos na formularu za prijavu.
        Metoda submit_callback provjerava jesu li uneseni podaci točni. 
        """

        name = self.name_entry.get()
        surname = self.surname_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.submit_callback(name, surname, username, password):
            self.master.show_page("plant_page")
        else:
            messagebox.showerror("Error", "Wrong data entered. Please try again.")
    

class Page_plant(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.page_plant = self
        self.image_labels_data = {}

        self.scrollbar = tk.Scrollbar(self, orient="vertical")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.canvas = tk.Canvas(self, bg="#94C973", yscrollcommand=self.scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.scrollbar.config(command=self.canvas.yview) 

        self.main_frame = tk.Frame(self.canvas, bg="#94C973")
        self.canvas_window = self.canvas.create_window((0,0), window=self.main_frame, anchor='nw')

        self.main_frame.bind("<Configure>", self.update_scrollregion)  

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
    

        self.title_label = tk.Label(self.main_frame, text="PyFlora", font=("Sans serif", 50), fg="white", bg="#94C973")
        self.title_label.grid(row=0, column=0, padx=20, pady=10)

        self.add_plant_label = tk.Label(self.main_frame, text="MY PROFILE", font=("Sans seri", 30), fg="white", bg="#94C973")
        self.add_plant_label.grid(row=0, column=1, columnspan=2, padx=20, pady=60)

        self.add_button = tk.Button(self.main_frame, text="UPDATE", font=("Sans serif", 20), fg="white", bg="#76B947", command=lambda:master.show_page("plant_form"))
        self.add_button.grid(row=0, column=3, padx=20, pady=10)

        self.current_column = 0
        self.current_row = 2
        self.max_column = 5

    def update_scrollregion(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        

    def add_plant_frame(self, plant_id, plant_name, temperature, path, humidity, light, substrate, pot_name):
                
        frame_width = 250 
        frame_height = 410  
        frame_padding = 2  
    
        plant_frame = tk.Frame(self.main_frame, bg="#FF92A5", highlightbackground="pink", highlightthickness=3, width=frame_width, height=frame_height, padx=10, pady=10)
        plant_frame.grid(row=self.current_row, column=self.current_column, padx=frame_padding, pady=frame_padding, sticky="nsew")

        img = Image.open(path)
        img = img.resize((200, 200)) 
        plant_image = ImageTk.PhotoImage(img)

        plant_data = (plant_id,plant_name, temperature, path, humidity, light, substrate)
        
        image_label = tk.Label(plant_frame, image=plant_image)
        image_label.image = plant_image
        image_label.grid(row=2, column=0, padx=30, pady=5)

        image_label.bind("<Button-1>", lambda event, data=plant_data, pot=pot_name: self.open_pot_details(data, pot))


        self.image_labels_data[plant_frame] = (plant_data, pot_name)

        self.update_idletasks()

        color_frame = tk.LabelFrame(plant_frame, bg="#b1d8b7", width=50)
        color_frame.grid(row=3, column=0, padx=10, sticky='w')


        plant_name_label = tk.Label(color_frame, text=plant_name, font=("Sans serif", 12),  bg="#b1d8b7")
        plant_name_label.grid(row=3, column=0, padx=30)

        details_text = f"Humidity: {humidity}\tTemperature: {temperature}\tLight: {light}\nSubstrate: {substrate}"
        plant_details_label = tk.Label(color_frame, text=details_text, font=("Sans serif", 12), bg="#b1d8b7")
        plant_details_label.grid(row=4, column=0, padx=30)

        pot_name_label = tk.Label(color_frame, text=f"Pot: {pot_name}", font=("Sans serif", 12), bg="#b1d8b7")
        pot_name_label.grid(row=5, column=0, padx=30)

        self.current_column += 1
        if self.current_column >= 4:
            self.current_column = 0
            self.current_row += 1
           

        self.update_idletasks()
        self.update_scrollregion() 


    def update_scrollregion(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def open_pot_details(self, plant_data, pot_name):
        plant_id, plant_name, temperature, path, humidity, light, substrate = plant_data
        self.master.pot_details.set_plant_id(plant_id)
        self.master.pot_details.set_pot_name(pot_name)
        self.master.show_page("pot_details", plant_data=plant_data)
        

    def refresh(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.image_labels_data.clear()

        # Resetiranje kolumne i reda
        self.current_column = 0
        self.current_row = 2

        
        self.title_label = tk.Label(self.main_frame, text="PyFlora", font=("Sans serif", 50), fg="white", bg="#94C973")
        self.title_label.grid(row=0, column=0, padx=20, pady=10)

        self.add_plant_label = tk.Label(self.main_frame, text="MY PROFILE", font=("Sans seri", 30), fg="white", bg="#94C973")
        self.add_plant_label.grid(row=0, column=1, columnspan=2, padx=20, pady=60)

        self.add_button = tk.Button(self.main_frame, text="UPDATE", font=("Sans serif", 20), fg="white", bg="#94C973", command=lambda:self.master.show_page("plant_form"))
        self.add_button.grid(row=0, column=3, padx=20, pady=10)

        # Recreate the widgets using the latest data
        all_plants = self.master.flora_data.get_all_plants() 
        for plant in all_plants:
            self.add_plant_frame(*plant)

        # Update the scrollregion
        self.update_scrollregion()


class Form_plant(tk.Frame):  #STRANICA ZA POHRANU PODATAKA
    def __init__(self, master, page_plant, flora_data, plant_save_callback,  plant_update_callback, plant_delete_callback,):
        super().__init__(master)
        self.master = master
        self.master.geometry("900x900")
        self.master.plant_form = self 
        self.page_plant = page_plant    
        self.flora_data = flora_data 
        self.selected_pot_id = None
        self.selected_pot_name = None      


        self.pot_list = flora_data.get_all_pots() #Poziva se metoda unutar objekta flora_data kako bi se dohvatile sve informacije o posudama
        
        # Ovdje se koristi dictionary comprehension da bi se svakom paru vrijednosti iz posude pridružio ID lonca u rječniku
        self.pot_dict = {f"{pot[1]} {pot[2]}": pot[0] for pot in self.pot_list} 
                                                                                    
        self.main_frame = tk.Frame(self, bg="#94C973")
        self.main_frame.grid(sticky='nsew')
        self.grid_rowconfigure(0, weight=2)    
        self.grid_columnconfigure(0, weight=2) 
                
        self.filename = None 
        self.path = None       

        self.title_label = tk.Label(self.main_frame, text="PyFlora", font=("Sans serif", 50), fg ="white", bg="#94C973")
        self.title_label.place(x=20, y=20)
        #self.title_label.grid(row=0, column=2, columnspan=1, pady=20)

        self.add_plant_label = tk.Label(self.main_frame, text="Add a new plant!", font=("Sans serif", 25), fg ="white", bg="#94C973")
        self.add_plant_label.place(x=400, y=50)
        #self.add_plant_label.grid(row=1, column=8, columnspan=2, pady=10)

        self.create_button("PLANTS PAGE",lambda:master.show_page("plant_page"), 750, 45)

        self.frame_label = tk.Label(self.main_frame, text= "Choose the plant pot:", font=("Sans serif", 18), fg ="white", bg="#94C973")
        self.frame_label.place(x=10, y=150)

        self.frame_list = tk.LabelFrame(self.main_frame, highlightbackground="pink", highlightthickness=3, width=350, height=350)
        self.frame_list.place(x=60, y=210)

        self.initialize_listbox() 

    def on_listbox_select(self, event):
        """
        Ova metoda se pokreće kada korisnik odabere stavku iz listbox-a. Prvo dohvaća trenutno odabrani indeks i koristi ga za dohvaćanje odabranog imena posude.
        Metoda dohvaća ID odabrane posude iz rječnika self.pot_dict. Potom se poziva metoda get_pot_status koja dohvaća status posude. 
        Ako je status "taken"  u posudi je biljka, metoda get_plant_by_pot dohvaća podatke o toj biljci. Ove informacije se zatim koriste za 
        ispunjavanje formulara na korisničkom sučelju. Ako posuda nije zauzeta, metoda briše sve informacije iz formulara i uklanja prikazane slike.
        """
        selected_index = self.listbox.curselection()
        if selected_index:
            self.selected_pot_name = self.listbox.get(selected_index)           
            self.selected_pot_id = self.pot_dict[self.selected_pot_name]
            pot_status = self.flora_data.get_pot_status(self.selected_pot_id)
            
            if pot_status.lower() == 'taken':
                
                plant_data = self.flora_data.get_plant_by_pot(self.selected_pot_id)
                if plant_data:
                    self.selected_plant_id, plant_name, temperature, path, humidity, light, substrate, pot_id = plant_data
                    
                    self.name_entry.delete(0, 'end')
                    self.name_entry.insert(0, plant_name)
                    self.temperature_entry.delete(0, 'end')
                    self.temperature_entry.insert(0, str(temperature))
                    self.humidity_entry.delete(0, 'end')
                    self.humidity_entry.insert(0, str(humidity))
                    self.light_entry.delete(0, 'end')
                    self.light_entry.insert(0, str(light))
                    self.substrate_entry.delete(0, 'end')
                    self.substrate_entry.insert(0, str(substrate))
                    
                    img = Image.open(path)
                    img = img.resize((300, 250))
                    label_image = ImageTk.PhotoImage(img)
                    self.photo_display.config(image=label_image)
                    self.photo_display.image = label_image
                    self.photo_path = path
            else:
               
                self.name_entry.delete(0, 'end')
                self.temperature_entry.delete(0, 'end')
                self.humidity_entry.delete(0, 'end')
                self.light_entry.delete(0, 'end')
                self.substrate_entry.delete(0, 'end')
                self.photo_display.config(image=None)
                self.photo_path = None


    def initialize_listbox(self):
        """
        Stvara se listbox koja prikazuje listu posuda s njihovim statusima. 
        Funkcija on_listbox_select koja će se pokrenuti kada se odabere stavka na listi.
        Kreiraju se parovi oznaka i unosa za različite informacije koje se trebaju prikazati ili unositi.
        Stvaraju se widgeti za fotografiju biljke i gumb koji omogućava korisniku da unese fotografiju.
        Dohvaća se ime trenutno odabrane posude.
        """
  
        self.listbox = Listbox(self.frame_list)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

        scrollbar = Scrollbar(self.frame_list, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        scrollbar.config(command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)

        
        for pot in self.pot_list:
            pot_id, pot_name, pot_status = pot 
            self.listbox.insert(tk.END, f"{pot_name} {pot_status}")

        self.create_label_entry_pair("Plant name:", 15, 450)
        self.create_label_entry_pair("Temperature:", 15, 480)
        self.create_label_entry_pair("Humidity:", 15, 510)
        self.create_label_entry_pair("Light:", 15, 540)
        self.create_label_entry_pair("Substrate:", 15, 570)

        self.photo_label = tk.Label(self.main_frame, text="Plant photo:", font=("Sans serif", 18), fg ="white",  bg="#94C973")
        self.photo_label.place(x=400, y=150)

        self.create_button("Upload a photo", self.open_action, 400 , 200)

        self.photo_frame = tk.LabelFrame(self.main_frame, highlightbackground="pink", highlightthickness=2, width=300, height=250)
        self.photo_frame.place(x=580, y=150)

        self.photo_display = tk.Label(self.photo_frame)
        self.photo_display.place(x=0, y=0) 

        selected_pot_name = self.flora_data.get_pot_name(self.selected_pot_id)

        
        self.create_button("SAVE", lambda: self.master.plant_save_callback(self, self.page_plant, self.name_entry.get(),
                                                                    self.temperature_entry.get(), self.photo_path,
                                                                    self.humidity_entry.get(), self.light_entry.get(),
                                                                    self.substrate_entry.get(), self.selected_pot_name), 15,700)
        
        self.create_button("UPDATE", lambda: self.master.plant_update_callback(self, self.master), 200,700)
        self.create_button("DELETE", lambda: self.master.plant_delete_callback(self), 375, 700)

    def open_action(self):
        filename = filedialog.askopenfilename()
        self.filename = filename
        img = Image.open(filename)

        img = img.resize((300, 250))
        label_image = ImageTk.PhotoImage(img)
        self.photo_display.config(image=label_image)
        self.photo_display.image = label_image

        self.photo_path = filename 


    def create_label_entry_pair(self, text, x, y):
        label = tk.Label(self.main_frame, text=text, font=("Arial", 15), fg="white", bg="#94C973")
        label.place(x=x, y=y)

        entry = tk.Entry(self.main_frame, width=40)
        entry.place(x=x+130, y=y)  

        if text == "Plant name:":
            self.name_entry = entry
        elif text == "Temperature:":
            self.temperature_entry = entry
        elif text == "Humidity:":
            self.humidity_entry = entry
        elif text == "Light:":
            self.light_entry = entry
        elif text == "Substrate:":
            self.substrate_entry = entry

        return label, entry

    def create_button(self, text, command, x, y):
        button = tk.Button(self.main_frame, text=text,  bg="#76B947", font=("Arial", 12), fg="white", command=command)
        button.place(x=x, y=y)

        return button
    
    def refresh_pots_list(self):
  
        self.listbox.delete(0, 'end')

        self.pot_list = self.flora_data.get_all_pots()
        self.pot_dict = {f"{pot[1]} {pot[2]}": pot[0] for pot in self.pot_list}

        for pot in self.pot_list:
            pot_id, pot_name, pot_status = pot  
            self.listbox.insert(tk.END, f"{pot_name} {pot_status}")

    def update_and_refresh(self):
        self.master.plant_update_callback(self)
        self.refresh_pots_list()
        self.refresh_plant_frames()

    
    def refresh_listbox(self):
        # Clear existing data
        self.listbox.delete(0, 'end')

        # Get fresh data from the database
        self.pot_list = self.flora_data.get_all_pots()

        # Repopulate the listbox
        for pot in self.pot_list:
            pot_id, pot_name, pot_status = pot 
            self.listbox.insert(tk.END, f"{pot_name} {pot_status}")


# Stranica na kojoj su prikazani detalji o odabranoj posudi
class Pot_details(tk.Frame):
    def __init__(self, master, flora_data, sensors_values, plant_id=None):
        super().__init__(master)
        self.master = master 
        self.master.pot_details = self
        self.flora_data = flora_data
        self.sensors_values = sensors_values
        self.plant_id = plant_id
        self.plot_type = "line"

        self.main_frame = tk.Frame(self, bg="#94C973")
        self.main_frame.grid(sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        
        self.path = None  
        
        self.title_label = tk.Label(self.main_frame, text="PyFlora", font=("Sans serif", 50), fg="white", bg="#94C973")
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="w")

        self.add_plant_label = tk.Label(self.main_frame, text="POT DETAILS", font=("Sans serif", 25), fg="white", bg="#94C973")
        self.add_plant_label.grid(row=1, column=2, columnspan=3, padx=30, pady=10, sticky="w")

        self.my_profile_button = tk.Button(self.main_frame, text="MY PROFILE", font=("Sans serif", 20), fg="white", bg="#76B947", command=lambda:master.show_page("plant_page"))
        self.my_profile_button.grid(row=0, column=3, pady=10, sticky="w")

        self.update_button = tk.Button(self.main_frame, text="UPDATE",font=("Sans serif", 20), fg="white", bg="#76B947", command=lambda:master.show_page("plant_form"))
        self.update_button.grid(row=0, column=4, pady=10, sticky="w")

        self.photo_plant = tk.LabelFrame(self.main_frame, highlightbackground="pink", highlightthickness=3, width=400, height=400)
        self.photo_plant.grid(row=3, column=5, padx=10, sticky="nsew")
        self.photo_plant.grid_rowconfigure(0, weight=1)
        self.photo_plant.grid_columnconfigure(0, weight=1)


        self.pot_name_display = tk.LabelFrame(self.main_frame, highlightbackground="pink", font=("Helvetica", 12, "bold"), highlightthickness=4, width=300, height=100)
        self.pot_name_display.grid(row=2, column=0, padx=10)

        self.sensor_display = tk.LabelFrame(self.main_frame, highlightbackground="pink", highlightthickness=3, width=300, height=300)
        self.sensor_display.grid(row=3, column=0, sticky="nsew")
        self.sensor_display.grid_rowconfigure(0, weight=1)
        self.sensor_display.grid_columnconfigure(0, weight=1)

        #sensor_values_label = tk.Label(self.sensor_display)
        #sensor_values_label.pack(fill="both", expand=True)

        self.sync_button = tk.Button(self.main_frame, text="SYNC", font=("Sans serif", 20), fg="white", bg="#76B947", command=self.update_sensor_display)
        self.sync_button.grid(row=0, column=5, padx=50, pady=10, sticky="w")

        self.pie_button = tk.Button(self.main_frame, text="Pie chart", command=self.show_pie)
        #self.pie_button.grid(row=4, column=1, padx=5)

        self.hist_button = tk.Button(self.main_frame, text="Histogram", command=self.show_hist)
        #self.hist_button.grid(row=4, column=2, padx=5)

        self.line_button = tk.Button(self.main_frame, text="Line", command=self.show_line)
        #self.line_button.grid(row=4, column=3, padx=5)

        self.graph_display = tk.Frame(self.main_frame,  highlightbackground="pink", highlightthickness=2, width=500, height=250)
        self.graph_display.grid(row=5, column=1, columnspan=3)

        """
        Osnove za prikazivanje podataka sa senzora u obliku grafikona.  
        Inicijalizira se rječnik self.sensor_data koji pohranjuje idealne i stvarne vrijednosti za četiri različita senzora.
        Kreira se četiri podgrafikona koristeći matplotlib. Svaki podgrafikon će prikazivati podatke za jedan od senzora.
        """

        self.sensor_data = {
            "light": {"ideal": [], "actual": []},
            "substrate": {"ideal": [], "actual": []},
            "temperature": {"ideal": [], "actual": []},
            "humidity": {"ideal": [], "actual": []},
        }

        self.fig, self.ax = plt.subplots(4, 1, figsize=(6, 4))  

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_display)  
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.master.update_idletasks()

    def update_sensor_display(self):
        # briše se display
        for line in self.sensor_display.winfo_children():
            line.destroy()

        # generiraju se nove vrijednosti sa senzora i akcije u skladu s njima, riječ je o metodi definiranoj u sensors.py
        sensor_actions = self.sensors_values.generate_actions(self.plant_id)

        # Na senzoru s prikazane vrijednosti sa senzora i akcija
        for sensor, (value, action) in sensor_actions.items():
            if sensor == "temperature":
                sensor_values_label = tk.Label(self.sensor_display, text=f"Current {sensor}:\n{value} °C", font=("Helvetica", 12, "bold"))
            else:
                sensor_values_label = tk.Label(self.sensor_display, text=f"Current {sensor}:\n{value} %", font=("Helvetica", 12, "bold"))
                
            sensor_values_label.pack()

            action_label = tk.Label(self.sensor_display, text=f"Action: \"{action}\"", font=("Helvetica", 12, "bold"))
            action_label.pack()

        #Externe vrijednosti povučene s interneta
        ext_temperature, ext_humidity = self.sensors_values.get_ext_values()
        #vrijednosti unešene putem formulara
        ideal_light, ideal_substrate, ideal_temperature, ideal_humidity, _ = self.sensors_values.get_ideal_values(self.plant_id)
        #vrijednosti dobivene simulatorom senzora
        sensor_light, sensor_substrate = self.sensors_values.get_sensor_values()

        #u riječik se dodaju idealne vrijednosti i vrijednosti sa svih senzora
        self.sensor_data["light"]["ideal"].append(ideal_light)
        self.sensor_data["light"]["actual"].append(sensor_light)

        self.sensor_data["substrate"]["ideal"].append(ideal_substrate)
        self.sensor_data["substrate"]["actual"].append(sensor_substrate)

        self.sensor_data["temperature"]["ideal"].append(ideal_temperature)
        self.sensor_data["temperature"]["actual"].append(ext_temperature)

        self.sensor_data["humidity"]["ideal"].append(ideal_humidity)
        self.sensor_data["humidity"]["actual"].append(ext_humidity)

        self.update_graph()


    def show_pie(self):
        self.plot_type = "pie"
        self.update_graph()

    def show_hist(self):
        self.plot_type = "hist"
        self.update_graph()

    def show_line(self):
        self.plot_type = "line"
        self.update_graph()

    #POLJEPŠATI GRAFOVE

    
    def update_graph(self):
        """
        Ova funkcija omogućuje dinamičko ažuriranje grafikona na temelju novih podataka dobivenih od senzora.
        Prvo se briše prethodni sadržaj na grafikonu, a zatim se postavljaju parametri grafikona.
        Ovisno o odabranoj vrsti grafikona funkcija prikazuju se podaci.
        Funkcija dodaje legendu na sliku i prilagođava prostor između podgrafikona za bolju vidljivost.
        """
        legend_patches = [Patch(facecolor='pink', label='Ideal'), Patch(facecolor='green', label='Actual')]

        for i, sensor in enumerate(["light", "substrate", "temperature", "humidity"]):
            self.ax[i].clear()

            self.ax[i].tick_params(direction='out', length=6, width=2, colors='black',
                                grid_color='gray', grid_alpha=0.5)

            # Add minor gridlines
            self.ax[i].grid(True, which='both')

            if self.plot_type == "line":
                self.ax[i].plot(self.sensor_data[sensor]["ideal"], color="pink")  
                self.ax[i].plot(self.sensor_data[sensor]["actual"], color="green")
                self.ax[i].set_ylabel(sensor.capitalize())

                min_val = min(min(self.sensor_data[sensor]["ideal"]), min(self.sensor_data[sensor]["actual"]))
                max_val = max(max(self.sensor_data[sensor]["ideal"]), max(self.sensor_data[sensor]["actual"]))

                if min_val == max_val:
                    min_val -= 0.01  
                    max_val += 0.01  

                self.ax[i].set_ylim([min_val, max_val])


            elif self.plot_type == "pie":
                    ideal = self.sensor_data[sensor]["ideal"][-1]  # Take the last value
                    actual = self.sensor_data[sensor]["actual"][-1]
                    self.ax[i].clear()

                    # Adjust the figure size and subplot arrangement
                    self.fig.set_size_inches(10, 8)
                    self.ax[i].set_position([0.1 + (i % 2) * 0.45, 0.75 - (i // 2) * 0.4, 0.35, 0.3])

                    wedges, texts = self.ax[i].pie([ideal, actual], colors=["pink", "green"])

                    # Increase the font size of the labels
                    for text in texts:
                        text.set_fontsize(10)

                    self.ax[i].set_ylabel(sensor.capitalize(), fontsize=12)


            elif self.plot_type == "hist":
                self.ax[i].hist([self.sensor_data[sensor]["ideal"][:], self.sensor_data[sensor]["actual"][:]],
                                color=["pink", "green"])
                self.ax[i].set_ylabel(sensor.capitalize())

        # Now we add the legend to the figure, not to each individual subplot
        self.fig.legend(handles=legend_patches, loc='upper right', bbox_to_anchor=(1, 1))

        # Adjusting the subplots to provide more space
        self.fig.subplots_adjust(hspace=0.7, bottom=0.15)

        self.canvas.draw()

    
    def set_plant_id(self, plant_id):
        self.plant_id = plant_id

        _, _, _, _, path = self.sensors_values.get_ideal_values(plant_id)
        self.set_plant_image(path)

        self.update_sensor_display()


    def set_plant_image(self, path):

        for photo in self.photo_plant.winfo_children():
            photo.destroy()

        image = Image.open(path)
        image = image.resize((200, 250), Image.ANTIALIAS)  
        tk_image = ImageTk.PhotoImage(image)

        label = tk.Label(self.photo_plant, image=tk_image)
        label.image = tk_image  
        label.pack()

    def set_pot_name(self, pot_name):
        self.pot_name_display.config(text=pot_name)



def main():
    app = Application(submit_login_data, flora_data, plant_save_callback, plant_delete_callback, plant_update_callback)
    app.mainloop()

if __name__ == "__main__":
    main()
