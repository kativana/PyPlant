
import tkinter as tk
from tkinter import messagebox
from GUI.gui import Application
from DATABASIS.flora_data import AppDatabase
from SENSORS.sensors import SensorsValues


def plant_save_callback(form_plant, page_plant, plant_name, temperature, path, humidity, light, substrate, pot_name):
    """
    Callback funkcija koja sprema podatke o biljci uključujući i ID i ime posude koja joj je dodjeljena, a unešene putem formulara. 
    Ako je uspješno spremljeno u bazu podataka, uz success poruku pojavi se i novi frame na stranici koja prikazuje sve spremljene bijke. 
    Biljci dodjeljuje ID posude u kojoj se nalazi.   
    """
    plant_name = form_plant.name_entry.get()
    temperature = int(form_plant.temperature_entry.get())
    path = form_plant.photo_path
    humidity = int(form_plant.humidity_entry.get())
    light = int(form_plant.light_entry.get())
    substrate = int(form_plant.substrate_entry.get())
    selected_pot_id = int(form_plant.selected_pot_id)
    pot_name = form_plant.flora_data.get_pot_name(selected_pot_id)
    plant_id = form_plant.flora_data.save_plant(plant_name, temperature, path, humidity, light, substrate)
    if plant_id:
        messagebox.showinfo("Success", "Plant data saved successfully")
        page_plant.add_plant_frame(plant_id, plant_name, temperature, path, humidity, light, substrate, pot_name)
        form_plant.flora_data.assign_pot_to_plant(plant_id, selected_pot_id) 
        form_plant.refresh_listbox()
    else:
        messagebox.showwarning("Error", "Error saving plant data")


def plant_update_callback(form_plant, app):
    plant_id = form_plant.selected_plant_id
    plant_name = form_plant.name_entry.get()
    temperature = form_plant.temperature_entry.get()
    path = form_plant.photo_path
    humidity = form_plant.humidity_entry.get()
    light = form_plant.light_entry.get()
    substrate = form_plant.substrate_entry.get()
    success = form_plant.flora_data.update_plant(plant_id, plant_name, temperature, path, humidity, light, substrate)
    if success:
        messagebox.showinfo("Success", "Plant data updated successfully")
        form_plant.refresh_listbox()
        app.pages["plant_page"].refresh()
    else:
        messagebox.showwarning("Error", "Error updating plant data")


def plant_delete_callback(form_plant, app):
    plant_id = form_plant.selected_plant_id
    pot_id = form_plant.selected_pot_id
    plant_name = form_plant.name_entry.get()
    temperature = form_plant.temperature_entry.get()
    path = form_plant.photo_path
    humidity = form_plant.humidity_entry.get()
    light = form_plant.light_entry.get()
    substrate = form_plant.substrate_entry.get()
    success = form_plant.flora_data.delete_plant(plant_id)
    if success:
        messagebox.showinfo("Success", "Plant data deleted successfully")
        form_plant.refresh_listbox()
        form_plant.flora_data.update_pot_status(pot_id, "available")
        form_plant.name_entry.delete(0, 'end')
        form_plant.temperature_entry.delete(0, 'end')
        form_plant.humidity_entry.delete(0, 'end')
        form_plant.light_entry.delete(0, 'end')
        form_plant.substrate_entry.delete(0, 'end')
        form_plant.photo_display.config(image=None)
        form_plant.photo_path = None
        app.pages["plant_page"].refresh()
        form_plant.refresh_listbox()
    else:
        messagebox.showwarning("Error", "Error deleting plant data")
   
def main():

    """
    Stvaranje instance klase AppDatabase povezane s bazom podataka s potrebnim tablicama. 
    Stvaranje instance klase SensorsValues, koja je povezana s istom bazom podataka.
    Provjera podataka za prijavu korisnika
    Stvaranje instance klase Application, proslijeđujući različite funkcije i objekte.
    Dohvaćanje sve biljaka iz baze podataka.
    Za svaku biljku dohvaća se ime lonca u kojem je posađena i dodaje se u aplikaciju.
    """

    db = AppDatabase("flora.db", "sensor", "sensor_ext", "user", "plant_table", "pot_table")
    db.create_user_table()
    db.add_admin()
    db.create_plant_table()
    db.create_pot_table()
    db.create_sensors()
   
    sensors_values = SensorsValues("flora.db")

    
    def submit_login_data(name, surname, username, password):
            return db.check_login_data(name, surname, username, password)

    app = Application(submit_login_data, db, sensors_values, 
                lambda *args: plant_save_callback(*args), 
                lambda *args: plant_update_callback(*args), 
                lambda *args: plant_delete_callback(*args, app))
    
    
    plants = db.get_all_plants()
    for plant in plants:
        plant_id, plant_name, temperature, path, humidity, light, substrate, pot_id = plant
        pot_name = db.get_pot_name(pot_id)
        app.plant.add_plant_frame(plant_id, plant_name, temperature, path, humidity, light, substrate, pot_name)

    app.mainloop()
  

if __name__ == "__main__":
    main()
