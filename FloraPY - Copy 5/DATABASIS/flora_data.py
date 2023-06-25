import sqlite3

class AppDatabase:

    def __init__(self, database_name, sensor, sensor_ext, user, plant_table, pot_table):
        self.database_name = database_name
        self.sensor_table = sensor
        self.sensor_ext_table = sensor_ext
        self.user_table = user
        self.plant_table = plant_table
        self.pot_table = pot_table

        self.create_pot_table() #Posude su hardkodirane 
        hardcoded_pots = ["Kitchen window 1", "Kitchen window 2", "Kitchen window 3",
                          "Balcony 1", "Balcony 2", "Balcony 3",
                           "Balcony 4", "Balcony 5", "Balcony 6",
                            "Garden"]  
        for pot in hardcoded_pots:
            if not self.pot_exists(pot):
                self.add_pot(pot)

    def pot_exists(self, pot_name):
        query = f'SELECT COUNT(*) FROM {self.pot_table} WHERE pot_name = ?;'
        result = self._fetch_query(query, (pot_name,))
        return result[0][0] > 0

    def add_pot(self, pot_name):
        query = f'INSERT INTO {self.pot_table} (pot_name) VALUES (?);'
        self._execute_queries([query], (pot_name,))

    
# KREIRANJE TABELA ZA SENZORE, USERA, BILJKE I POSUDE
    def create_sensors(self):
            sensor_table_query = """CREATE TABLE IF NOT EXISTS {} (
                                id INTEGER PRIMARY KEY,
                                light INTEGER,
                                substrate INTEGER
                            );""".format(self.sensor_table)

            sensor_ext_table_query = """CREATE TABLE IF NOT EXISTS {} (
                                    id INTEGER PRIMARY KEY,
                                    temp_ext REAL NOT NULL,
                                    hum_ext REAL NOT NULL
                                );""".format(self.sensor_ext_table)

            queries = [sensor_table_query, sensor_ext_table_query]

            self._execute_queries(queries)


    def create_user_table(self):
        user_table_query = """CREATE TABLE IF NOT EXISTS {table_name} (
                        user_id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        surname TEXT NOT NULL,
                        username TEXT NOT NULL,
                        pin INTEGER NOT NULL
                        );
                """.format(table_name=self.user_table)

        self._execute_queries([user_table_query])

    # Add methods for plant and plant pot tables
    
    def create_plant_table(self):
        plant_table_query = """CREATE TABLE IF NOT EXISTS {table_name} (
                        plant_id INTEGER PRIMARY KEY,
                        plant_name TEXT NOT NULL,
                        temperature INTEGER,
                        path TEXT NOT NULL,
                        humidity INTEGER NOT NULL,
                        light INTEGER NOT NULL,
                        substrate INTEGER NOT NULL,
                        pot_id INTEGER,
                        FOREIGN KEY(pot_id) REFERENCES {pot_table}(id)                    
                        );
                """.format(table_name=self.plant_table, pot_table=self.pot_table)


        self._execute_queries([plant_table_query])


    def create_pot_table(self):   
        pot_table_query =  """CREATE TABLE IF NOT EXISTS {table_name} (
                        id INTEGER PRIMARY KEY,
                        pot_name TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT "available"                      
                        );
                """.format(table_name=self.pot_table)

        self._execute_queries([pot_table_query])

    
    def _execute_queries(self, queries, params=None):
        connection = None
        try:
            connection = sqlite3.connect(self.database_name)
            cursor = connection.cursor()
            for query in queries:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
            connection.commit()
        except sqlite3.Error as e:
            print('Database error', e)
            return False
        finally:
            if connection:
                connection.close()
        return True


    def _fetch_query(self, query, params=None):
        connection = None
        result = None
        try:
            connection = sqlite3.connect(self.database_name)
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
        except sqlite3.Error as e:
            print('Database error:', e)
        finally:
            if connection:
                connection.close()
        return result



    #METODE VEZANE UZ USERA
    def save_data(self, name, surname, username, pin):
        query = f'INSERT INTO {self.user_table} (name, surname, username, pin) VALUES (?, ?, ?, ?);'
        return self._execute_queries([query], (name, surname, username, pin))
    
    def add_or_update_user(self, old_name, old_surname, new_name, new_surname, new_username, new_pin):
        user = self.get_user_by_name(old_name, old_surname)
        if user:
            query = """
            UPDATE {table}
            SET name = ?, surname = ?, username = ?, pin = ?
            WHERE name = ? AND surname = ?;
            """.format(table=self.user_table)
            params = (new_name, new_surname, new_username, new_pin, old_name, old_surname)
        else:
            query = 'INSERT INTO {table} (name, surname, username, pin) VALUES (?, ?, ?, ?);'.format(table=self.user_table)
            params = (new_name, new_surname, new_username, new_pin)

        return self._execute_queries([query], params)


    def admin_exists(self):
        query = f'SELECT * FROM {self.user_table} WHERE name = "Admin" AND surname = "Admin" AND username = "Admin" AND pin = 1234;'
        result = self._fetch_query(query)
        return len(result) > 0

    def add_admin(self):
        if not self.admin_exists():
            self.save_data('Admin', 'Admin', "Admin", 1234)


    def check_login_data(self, name, surname, username, password):
        query = f"SELECT * FROM {self.user_table} WHERE name=? AND surname=? AND username=? AND pin=?"
        result = self._fetch_query(query, (name, surname, username, password))

        return result is not None and len(result) > 0


    #METODE VEZANE UZ BILJKE 

    def save_plant(self, plant_name, temperature, path, humidity, light, substrate):
        insert_query = f'INSERT INTO {self.plant_table} (plant_name, temperature, path, humidity, light, substrate) VALUES (?, ?, ?, ?, ?,?);'
        id_query = "SELECT last_insert_rowid();"
        
        connection = None
        try:
            connection = sqlite3.connect(self.database_name)
            cursor = connection.cursor()

            # Execute the insert query
            cursor.execute(insert_query, (plant_name, temperature, path, humidity, light, substrate))
            # Now get the id of the last inserted row
            cursor.execute(id_query)
            plant_id = cursor.fetchone()[0]

            connection.commit()
            cursor.close()

            return plant_id
        except sqlite3.Error as e:
            print('Database error', e)
            return None
        finally:
            if connection:
                connection.close()

    def update_plant(self, plant_id, plant_name, temperature, path, humidity, light, substrate):
        query = '''UPDATE {table}
                SET plant_name = ?, temperature = ?, path = ?, humidity = ?, light = ?, substrate = ?
                WHERE plant_id = ?;'''.format(table=self.plant_table)
        return self._execute_queries([query], (plant_name, temperature, path, humidity, light, substrate, plant_id))

    
    def delete_plant(self, plant_id):
        query = '''DELETE FROM {table}
                WHERE plant_id = ?;'''.format(table=self.plant_table)
        return self._execute_queries([query], (plant_id,))
    

    def get_all_plants(self):
        query = f'SELECT * FROM {self.plant_table};'
        return self._fetch_query(query)
    

    def assign_pot_to_plant(self, plant_id, pot_id):
        update_pot_query = f"UPDATE {self.pot_table} SET status = 'taken' WHERE id = ?;"
        self._execute_queries([update_pot_query], (pot_id,))
        
        update_plant_query = f"UPDATE {self.plant_table} SET pot_id = ? WHERE plant_id = ?;"
        self._execute_queries([update_plant_query], (pot_id, plant_id))


#METODE VEZANE UZ POSUDE 

    def get_all_pots(self):
        query = f'SELECT * FROM {self.pot_table};'
        return self._fetch_query(query)

    def get_pot_name(self, pot_id):
        query = f'SELECT pot_name FROM {self.pot_table} WHERE id = ?;'
        result = self._fetch_query(query, (pot_id,))
        if result:
            return result[0][0]
        return None
    
    def get_pot_status(self, pot_id):
        query = f'SELECT status FROM {self.pot_table} WHERE id = ?;'
        result = self._fetch_query(query, (pot_id,))
        if result:
            return result[0][0]
        return None

    def get_plant_by_pot(self, pot_id):
        query = f'SELECT * FROM {self.plant_table} WHERE pot_id = ?;'
        result = self._fetch_query(query, (pot_id,))
        if result:
            return result[0]
        return None

    def update_pot_status(self, pot_id, status):
        query = f'UPDATE {self.pot_table} SET status = ? WHERE id = ?;'
        return self._execute_queries([query], (status, pot_id,))




def main():
    database = AppDatabase('app.db')
    #database.create_sensor_tables()
    database.create_user_table()
    # Create other tables as needed
    #database.create_plant_table()
    # database.create_plant_pot_table()

if __name__ == '__main__':
    main()

