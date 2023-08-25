import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk

from datetime import datetime, date
from sqlalchemy import create_engine, text


class DatabaseManager:
    def __init__(self):

        server = ''
        database = ''

        username = ''
        password = ''

        conn_str = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=SQL Server'

        self.engine = create_engine(conn_str)

    def connect_database(self):
        self.connection = self.engine.connect()

    def check_array_exists(self, p_array, a_array):

        p_query = text("SELECT * FROM Array WHERE ArrayID= :p")
        p_result = self.connection.execute(p_query, p=p_array)
        queried_result_p = p_result.fetchall()

        a_query = text("SELECT * FROM Array WHERE ArrayID = :a")
        a_result = self.connection.execute(a_query, a=a_array)
        queried_result_a = a_result.fetchall()

        self.engine.dispose()

        if (queried_result_p is None or queried_result_a is None) or (
                len(queried_result_p) == 0 or len(queried_result_a) == 0):
            returned_result = None

        else:
            returned_result = 0

        return returned_result

    def check_sensor_cart_id_exists(self, sensor_cart_id):

        sensor_cart_id_query = text("SELECT * FROM SensorCartAssembly WHERE SensorCartID= :id")
        sensor_cart_id_result = self.connection.execute(sensor_cart_id_query, id=sensor_cart_id)
        queried_result_sensor_cart_id = sensor_cart_id_result.fetchall()

        self.engine.dispose()

        if (queried_result_sensor_cart_id is None) or (len(queried_result_sensor_cart_id) == 0):
            returned_result = None

        else:
            returned_result = queried_result_sensor_cart_id

        return returned_result


class SensorCartridgeAssembly:
    def __init__(self, theme="breeze"):
        self.window = ThemedTk(theme=theme)
        self.window.title("GUI")
        self.window.geometry()

        self.db_manager = DatabaseManager()

        self.build_widgets()
        self.window.mainloop()

    def build_widgets(self):
        bold_font = ('Arial', 10, 'bold')
        title_label = ttk.Label(self.window, text="MEGA Sensor Cartridge Assembly", font=bold_font)
        title_label.pack(pady=10)

        self.notebook = ttk.Notebook(self.window)

        self.barcode_frame = ttk.Frame(self.notebook)
        self.build_barcode_frame()
        self.notebook.add(self.barcode_frame, text="Barcode")

        self.observation_frame = ttk.Frame(self.notebook)
        self.build_observation_frame()
        self.notebook.add(self.observation_frame, text="Observations")

        self.notebook.pack(pady=10, expand=True, fill='both')

    def build_barcode_frame(self):
        barcode_frame = ttk.LabelFrame(self.barcode_frame, text="Barcode")
        barcode_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        notes_frame = ttk.LabelFrame(self.barcode_frame, text="Notes")
        notes_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        submit_frame = ttk.LabelFrame(self.barcode_frame, text="Update Database")
        submit_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        p_label = ttk.Label(barcode_frame, text="p Array")
        p_label.grid(row=0, column=0, padx=5, pady=5)
        self.p_entry = ttk.Entry(barcode_frame)
        self.p_entry.grid(row=0, column=1, padx=5, pady=5)

        a_label = ttk.Label(barcode_frame, text="a Array")
        a_label.grid(row=1, column=0, padx=5, pady=5)
        self.a_entry = ttk.Entry(barcode_frame)
        self.a_entry.grid(row=1, column=1, padx=5, pady=5)

        ok_button = ttk.Button(barcode_frame, text="Check Array", command=self.check_arrays_in_database)
        ok_button.grid(row=2, column=0, sticky="NESW", padx=10, pady=10, columnspan=2)

        self.notes_pre_label = ttk.Label(notes_frame, text="Notes")
        self.notes_pre_label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.notes_pre_entry = ttk.Entry(notes_frame)
        self.notes_pre_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.initial_label = ttk.Label(submit_frame, text="Operator Initial")
        self.initial_label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.initial_entry_barcode = ttk.Entry(submit_frame)
        self.initial_entry_barcode.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.submit_button = ttk.Button(submit_frame, text="Generate ID", command=self.generate_sensor_cart_id, state='disabled')
        self.submit_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        reset_button_barcode = ttk.Button(submit_frame, text="Reset", command=self.reset_form)
        reset_button_barcode.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.p_entry.bind("<KeyRelease>", lambda e: self.update_submit_button_state())
        self.a_entry.bind("<KeyRelease>", lambda e: self.update_submit_button_state())
        self.initial_entry_barcode.bind("<KeyRelease>", lambda e: self.update_submit_button_state())

    def update_submit_button_state(self):
        p_field = self.p_entry.get().strip()
        a_field = self.a_entry.get().strip()
        initial_field = self.initial_entry_barcode.get().strip()

        if p_field and a_field and initial_field:
            self.submit_button.state(['!disabled'])
        else:
            self.submit_button.state(['disabled'])

    def check_arrays_in_database(self):
        p_array = self.p_entry.get()
        a_array = self.a_entry.get()

        if p_array[-1] != 'P' or a_array[-1] != 'A':
            messagebox.showerror("Error", "Incorrect Barcode, Please Rescan the Barcode")

        else:
            try:
                self.db_manager.connect_database()
                queried_rows = self.db_manager.check_array_exists(p_array, a_array)
                if not queried_rows is None:
                    messagebox.showinfo(title="Success",
                                        message="Arrays Exist in the Database, Click Submit Button to Generate "
                                                "SensorCartID")
                else:
                    messagebox.showerror("Error", "p Array or a Array not Found in the Database!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def check_sensor_cart_id_in_database(self):
        sensor_cart_id = self.SensorCartID_entry.get()

        try:
            self.db_manager.connect_database()
            queried_rows = self.db_manager.check_sensor_cart_id_exists(sensor_cart_id)

            if not queried_rows is None:
                messagebox.showinfo(title="Success",
                                    message="SensorCartID Exists in the DB \n \n \
                                    \n Datetime: {} \n \
                                    \n SensorCartID: {} \n \
                                    \n pArrayBarcode: {} \n \
                                    \n aArrayBarcode: {} \n \
                                    \n Leak: {} \n \
                                    \n Flow: {} \n \
                                    \n Rebuilt: {} \n \
                                    \n Weight: {} \n \
                                    \n Notes: {} \n \
                                    \n Initial: {}".format(queried_rows[0][0],
                                                           queried_rows[0][1],
                                                           queried_rows[0][2],
                                                           queried_rows[0][3],
                                                           queried_rows[0][4],
                                                           queried_rows[0][5],
                                                           queried_rows[0][6],
                                                           queried_rows[0][7],
                                                           queried_rows[0][8],
                                                           queried_rows[0][9]))
            else:
                messagebox.showerror("Error", "SensorCartID not Found in the Database!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ordinal_dates(self):
        today = date.today()
        year = str(today.year)[-2:]
        day_of_year = str(today.timetuple().tm_yday)

        self.ordinal_date = year + day_of_year
        return self.ordinal_date

    def build_observation_frame(self):
        SensorCartID_frame = ttk.LabelFrame(self.observation_frame, text="SensorCartID")
        SensorCartID_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.SensorCartID_label, self.SensorCartID_entry = self.create_disabled_entry(SensorCartID_frame,
                                                                                      "SensorCartID", 0)
        ok_button = ttk.Button(SensorCartID_frame, text="Check SensorCartID",
                               command=self.check_sensor_cart_id_in_database)
        ok_button.grid(row=1, column=0, sticky="NESW", padx=10, pady=10, columnspan=2)

        observation_frame = ttk.LabelFrame(self.observation_frame, text="Observations")
        observation_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.leak_label, self.leak_entry = self.create_disabled_entry(observation_frame, "Leak", 0)
        self.flow_label, self.flow_combobox = self.create_disabled_combobox(observation_frame, "Flow", ["Pass", "Fail"],
                                                                            1)
        #         self.flow_combobox.config(state='readonly')
        self.rebuilt_label, self.rebuilt_combobox = self.create_disabled_combobox(observation_frame, "Rebuilt",
                                                                                  ["Yes", "No"], 2)
        #         self.rebuilt_combobox.config(state='readonly')
        self.weight_label, self.weight_entry = self.create_disabled_entry(observation_frame, "Weight", 3)
        self.notes_label, self.notes_entry = self.create_disabled_entry(observation_frame, "Notes", 4)

        submit_frame = ttk.LabelFrame(self.observation_frame, text="Update Database")
        submit_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.initial_label = ttk.Label(submit_frame, text="Operator Initial")
        self.initial_label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.initial_entry_observation = ttk.Entry(submit_frame)
        self.initial_entry_observation.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.update_button = ttk.Button(submit_frame, text="Update", command=self.add_sensor_cart_id_details, state='disabled')
        self.update_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        reset_button_observation = ttk.Button(submit_frame, text="Reset", command=self.reset_form)
        reset_button_observation.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.SensorCartID_entry.bind("<KeyRelease>", lambda e: self.update_update_button_state())
        self.leak_entry.bind("<KeyRelease>", lambda e: self.update_update_button_state())
        self.flow_combobox.bind('<<ComboboxSelected>>', lambda e: self.update_update_button_state())
        self.rebuilt_combobox.bind('<<ComboboxSelected>>', lambda e: self.update_update_button_state())
        self.weight_entry.bind("<KeyRelease>", lambda e: self.update_update_button_state())
        self.notes_entry.bind("<KeyRelease>", lambda e: self.update_update_button_state())
        self.initial_entry_observation.bind("<KeyRelease>", lambda e: self.update_update_button_state())

    def update_update_button_state(self):
        sensor_cart_id_field = self.SensorCartID_entry.get().strip()
        leak_field = self.leak_entry.get().strip()
        flow_field = self.flow_combobox.get().strip()
        rebuilt_field = self.rebuilt_combobox.get().strip()
        weight_field = self.weight_entry.get().strip()
        notes_field = self.notes_entry.get().strip()
        initial_field = self.initial_entry_observation.get().strip()

        if sensor_cart_id_field and (leak_field or flow_field or rebuilt_field or weight_field or notes_field or initial_field):
            self.update_button.state(['!disabled'])
        else:
            self.update_button.state(['disabled'])

    def create_disabled_entry(self, frame, label_text, row):
        label = ttk.Label(frame, text=label_text)
        label.grid(row=row, column=0, padx=5, pady=5)
        label.config(state="!disabled")

        entry = ttk.Entry(frame)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        entry.config(state="!disabled")

        return label, entry

    def create_disabled_combobox(self, frame, label_text, values, row):
        label = ttk.Label(frame, text=label_text)
        label.grid(row=row, column=0, padx=5, pady=5)
        label.config(state="!disabled")

        combobox = ttk.Combobox(frame, values=values)
        combobox.grid(row=row, column=1, sticky="NESW", padx=5, pady=5)
        combobox.config(state="!disabled")

        return label, combobox

    def reset_form(self):
        for entry in [self.initial_entry_barcode,
                      self.initial_entry_observation,
                      self.notes_pre_entry,
                      self.SensorCartID_entry,
                      self.p_entry,
                      self.a_entry,
                      self.leak_entry,
                      self.weight_entry,
                      self.flow_combobox,
                      self.rebuilt_combobox,
                      self.notes_entry]:
            entry.delete(0, tk.END)

        for combobox in [self.flow_combobox, self.rebuilt_combobox]:
            combobox.delete(0, tk.END)

        self.update_submit_button_state()
        self.update_update_button_state()

    def reset_fields(self):
        if self.leak_entry['state'] != 'disabled':
            self.leak_entry.delete(0, 'end')

        if self.flow_combobox['state'] != 'disabled':
            self.flow_combobox.set('')

        if self.rebuilt_combobox['state'] != 'disabled':
            self.rebuilt_combobox.set('')

        if self.weight_entry['state'] != 'disabled':
            self.weight_entry.delete(0, 'end')

        if self.notes_entry['state'] != 'disabled':
            self.notes_entry.delete(0, 'end')

        if self.initial_entry_observation['state'] != 'disabled':
            self.initial_entry_observation.delete(0, 'end')

    def generate_sensor_cart_id(self):

        self.reset_fields()

        ordinal_date = self.ordinal_dates()

        self.db_manager.connect_database()

        query = text("SELECT * FROM SensorCartAssembly WHERE SensorCartID LIKE :sensor_cart_id ORDER BY Datetime DESC")
        result = self.db_manager.connection.execute(query, sensor_cart_id='{}%'.format(ordinal_date))
        queried_rows = result.fetchall()

        self.db_manager.engine.dispose()

        if not len(queried_rows) == 0:
            last_sensor_cart_id = int(queried_rows[0][1].split('-')[1])

        else:
            last_sensor_cart_id = 0

        self.db_manager.connect_database()

        sensor_cart_id = '{}-{}'.format(ordinal_date, last_sensor_cart_id + 1)
        p_array = self.p_entry.get()
        a_array = self.a_entry.get()
        flow = self.flow_combobox.get() if self.flow_combobox['state'] != 'disabled' else None
        leak = self.leak_entry.get() if self.leak_entry['state'] != 'disabled' else None
        weight = self.weight_entry.get() if self.weight_entry['state'] != 'disabled' else None
        rebuilt = self.rebuilt_combobox.get() if self.rebuilt_combobox['state'] != 'disabled' else None
        notes = self.notes_pre_entry.get() if self.notes_pre_entry['state'] != 'disabled' else None
        initial = self.initial_entry_barcode.get()

        try:

            self.db_manager.connect_database()
            query_p = text("SELECT * FROM SensorCartAssembly WHERE pArrayBarcode = :p")
            result_p = self.db_manager.connection.execute(query_p, p=p_array)
            queried_rows_p = result_p.fetchall()
            continue_flag = True if len(queried_rows_p) == 0 else False
            p_array_string = p_array if continue_flag == False else ''
            self.db_manager.engine.dispose()

            self.db_manager.connect_database()
            query_a = text("SELECT * FROM SensorCartAssembly WHERE aArrayBarcode = :a")
            result_a = self.db_manager.connection.execute(query_a, a=a_array)
            queried_rows_a = result_a.fetchall()
            continue_flag = True if len(queried_rows_a) == 0 else False
            a_array_string = a_array if continue_flag == False else ''
            self.db_manager.engine.dispose()

            duplicate_array_string = '{} {}'.format(p_array_string, a_array_string)

            if not continue_flag:
                returned_flag = messagebox.askokcancel("Warning",
                                                       "{} Exist in the Database. \n Do You Wish to Proceed?".format(
                                                           duplicate_array_string))

                if returned_flag:
                    continue_flag = True

                else:
                    continue_flag = False

            if continue_flag:
                self.db_manager.connect_database()

                current_time = datetime.now()
                time_sta = current_time.timesta()
                date_time = datetime.fromtimesta(time_sta)

                query = text(
                    "INSERT INTO SensorCartAssembly (Datetime, SensorCartID, pArrayBarcode, aArrayBarcode, "
                    "Leak, Flow, Rebuilt, Weight, Notes, Initial) VALUES (:Datetime, :cart_id, :p, :a, "
                    ":leak, :flow, :rebuilt, :weight, :notes, :initials)")
                self.db_manager.connection.execute(query,
                                                   Datetime=date_time,
                                                   cart_id=sensor_cart_id,
                                                   p=p_array,
                                                   a=a_array,
                                                   leak=leak,
                                                   flow=flow,
                                                   rebuilt=rebuilt,
                                                   weight=weight,
                                                   notes=notes,
                                                   initials=initial)
                messagebox.showinfo("Success", "Data Inserted Successfully \n Generated ID: {}".format(sensor_cart_id))

        except Exception as e:
            print("An error occurred while inserting data:", str(e))
            messagebox.showerror("Error", "An error occurred while inserting data: " + str(e))

        finally:
            self.db_manager.engine.dispose()

    def add_sensor_cart_id_details(self):

        self.db_manager.connect_database()
        sensor_cart_id = self.SensorCartID_entry.get()

        flow = self.flow_combobox.get() if self.flow_combobox['state'] != 'disabled' else None
        leak = self.leak_entry.get() if self.leak_entry['state'] != 'disabled' else None
        weight = self.weight_entry.get() if self.weight_entry['state'] != 'disabled' else None
        rebuilt = self.rebuilt_combobox.get() if self.rebuilt_combobox['state'] != 'disabled' else None
        notes = self.notes_entry.get() if self.notes_entry['state'] != 'disabled' else None
        initial = self.initial_entry_observation.get()

        update_fields = ["DatetimeModified = :DatetimeModified"]

        parameters = {
            'DatetimeModified': datetime.fromtimesta(datetime.now().timesta()),
            'id': sensor_cart_id
        }

        if flow:
            update_fields.append("Flow = :flow")
            parameters["flow"] = flow

        if leak:
            update_fields.append("Leak = :leak")
            parameters["leak"] = leak

        if weight:
            update_fields.append("Weight = :weight")
            parameters["weight"] = weight

        if rebuilt:
            update_fields.append("Rebuilt = :rebuilt")
            parameters["rebuilt"] = rebuilt

        if notes:
            update_fields.append("Notes = :notes")
            parameters["notes"] = notes

        if initial:
            update_fields.append("Initial = :initials")
            parameters["initials"] = initial

        update_query = "UPDATE SensorCartAssembly SET {} WHERE SensorCartID = :id".format(", ".join(update_fields))

        try:
            query = text(update_query)
            self.db_manager.connection.execute(query, **parameters)
            print("Data inserted successfully")
            messagebox.showinfo("Success", "Data inserted successfully")
            self.reset_fields()

        except Exception as e:
            print("An error occurred while inserting data:", str(e))
            messagebox.showerror("Error", "An error occurred while inserting data: " + str(e))

        finally:
            self.db_manager.engine.dispose()


if __name__ == "__main__":
    app = SensorCartridgeAssembly()
