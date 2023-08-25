import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text

import warnings
warnings.filterwarnings("ignore")


class GUI:

    def __init__(self, root):
        self.root = root
        self.root.title('MEGA Barcode Tracker')

        self.tabControl = ttk.Notebook(root)
        self.tab1 = ttk.Frame(self.tabControl, padding=(10, 10, 10, 10))
        self.tab2 = ttk.Frame(self.tabControl, padding=(10, 10, 10, 10))

        self.tab1.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tab2.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.tabControl.add(self.tab1, text='Wafer Preprocessing Tracker')
        self.tabControl.add(self.tab2, text='Barcode Validation')

        self.tabControl.grid(sticky='NESW')

        self.class1 = Tab1Class(self.tab1)
        self.class2 = Tab2Class(self.tab2)


class Tab1Class:

    def __init__(self, main_frame):

        self.main_frame = main_frame

        self.counter = 0

        self.wafer_id_entries = []

        style = ttk.Style()
        style.configure("Small.TButton", padding=(0, 0, 0, 0), font=("Arial", 8))

        self.operator_initial_label = ttk.Label(self.main_frame, text="Operator Initial:")
        self.operator_initial_entry = ttk.Entry(self.main_frame, width=20)

        self.array_type_label = ttk.Label(self.main_frame, text="Array:")
        self.array_type_combobox = ttk.Combobox(self.main_frame, values=["A", "P"], state="readonly", width=18)

        self.pre_processing_step_label = ttk.Label(self.main_frame, text="Pre-processing Step:")
        self.pre_processing_step_combobox = ttk.Combobox(self.main_frame, state="readonly", width=18)

        self.wafer_id_label = ttk.Label(self.main_frame, text="Wafer/Array ID:")

        self.operator_initial_label.grid(column=0, row=1, padx=(0, 10), pady=(0, 10), sticky=tk.W)
        self.operator_initial_entry.grid(column=1, row=1, padx=(0, 10), pady=(0, 10), sticky=tk.W)

        self.array_type_label.grid(column=0, row=2, padx=(0, 10), pady=(0, 10), sticky=tk.W)
        self.array_type_combobox.grid(column=1, row=2, padx=(0, 10), pady=(0, 10), sticky=tk.W)
        self.array_type_combobox.bind("<<ComboboxSelected>>", self.different_preprocessing_steps)

        self.pre_processing_step_label.grid(column=0, row=3, padx=(0, 10), pady=(0, 10), sticky=tk.W)
        self.pre_processing_step_combobox.grid(column=1, row=3, padx=(0, 10), pady=(0, 10), sticky=tk.W)

        self.wafer_array_id_var = tk.StringVar()

        self.wafer_id_radio_button = ttk.Radiobutton(main_frame, text='Wafer ID', variable=self.wafer_array_id_var,
                                                     value="wafer_id", command=self.update_submit_button_state)
        self.array_id_radio_button = ttk.Radiobutton(main_frame, text='Array ID', variable=self.wafer_array_id_var,
                                                     value="array_id", command=self.update_submit_button_state)

        self.wafer_id_radio_button.grid(column=0, row=6, padx=(0, 10), pady=(0, 10), sticky=tk.W)
        self.array_id_radio_button.grid(column=0, row=7, padx=(0, 10), pady=(0, 10), sticky=tk.W)

        self.array_detail_var = tk.StringVar()

        self.full_array_radio_button = ttk.Radiobutton(main_frame, text='Full Array', variable=self.array_detail_var,
                                                       value="full_array", command=self.update_submit_button_state)
        self.dummy_array_radio_button = ttk.Radiobutton(main_frame, text='Dummy Array', variable=self.array_detail_var,
                                                        value="dummy_array", command=self.update_submit_button_state)
        self.full_array_radio_button.state(['disabled'])
        self.dummy_array_radio_button.state(['disabled'])

        self.full_array_radio_button.grid(column=0, row=8, padx=(0, 10), pady=(0, 10), sticky=tk.W)
        self.dummy_array_radio_button.grid(column=0, row=9, padx=(0, 10), pady=(0, 10), sticky=tk.W)

        self.wafer_id_label.grid(column=0, row=4, padx=(0, 2), pady=(0, 10), sticky=tk.W)

        self.add_wafer_id_button = ttk.Button(self.main_frame, text="+", command=self.add_wafer_id,
                                              style="Small.TButton")
        self.add_wafer_id_button.grid(column=1, row=4, padx=(0, 0), pady=(0, 10), sticky=tk.W)

        self.remove_wafer_id_button = ttk.Button(self.main_frame, text="-", command=self.remove_wafer_id,
                                                 style="Small.TButton")
        self.remove_wafer_id_button.grid(column=1, row=4, padx=(77, 0), pady=(0, 10), sticky=tk.W)

        self.submit_button = ttk.Button(self.main_frame, text="Submit", command=self.submit_data, state='disabled')
        self.submit_button.grid(column=0, row=5, padx=(0, 10), pady=(0, 10), sticky=tk.W)

    def different_preprocessing_steps(self, event):
        selected_value = self.array_type_combobox.get()
        if selected_value == "A":
            self.pre_processing_step_combobox["values"] = ["Incoming Inspection",
                                                           "Laser Drill",
                                                           "Wash",
                                                           "Drill QC",
                                                           "Chloridize + Rinse",
                                                           "Conditioning",
                                                           "Checkout",
                                                           "Shipped to E",
                                                           "Shipped to O"]
        else:
            self.pre_processing_step_combobox["values"] = ["Incoming Inspection",
                                                           "Cure",
                                                           "Wash",
                                                           "Chloridize + Rinse",
                                                           "Imaging",
                                                           "Checkout",
                                                           "Shipped to E"]

    def add_wafer_id(self):
        wafer_id_entry = ttk.Entry(self.main_frame, width=20)
        wafer_id_entry.grid(column=1, row=len(self.wafer_id_entries) + 5, padx=(0, 10), pady=(0, 10), sticky=tk.W)
        self.counter += 1
        if self.counter >= 10:
            self.add_wafer_id_button.state(['disabled'])

        if 10 > self.counter >= 0:
            self.remove_wafer_id_button.state(['!disabled'])

        self.wafer_id_entries.append(wafer_id_entry)

    def remove_wafer_id(self):
        if self.wafer_id_entries:
            entry = self.wafer_id_entries.pop()
            entry.destroy()
        self.counter -= 1

        if 0 <= self.counter < 10:
            self.add_wafer_id_button.state(['!disabled'])

        if self.counter <= 0:
            self.remove_wafer_id_button.state(['disabled'])

    def get_db_details(self):
        server = ''
        database = ''

        username = ''
        password = ''

        conn_str = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=SQL Server'

        return conn_str

    def update_submit_button_state(self):
        selected_value = self.wafer_array_id_var.get()
        selected_array_detail_value = self.array_detail_var.get()
        if selected_value == "array_id":
            self.full_array_radio_button.state(['disabled'])
            self.dummy_array_radio_button.state(['disabled'])
            self.submit_button.state(['!disabled'])
        elif selected_value == "wafer_id":
            self.full_array_radio_button.state(['!disabled'])
            self.dummy_array_radio_button.state(['!disabled'])
            if selected_array_detail_value in ['full_array', 'dummy_array']:
                self.submit_button.state(['!disabled'])
            else:
                self.submit_button.state(['disabled'])
        else:
            self.submit_button.state(['disabled'])

    def check_id(self, wafer_ids):
        selected_value = self.wafer_array_id_var.get()
        if selected_value == "wafer_id":
            for wafer_id in wafer_ids:
                if "-" in wafer_id:
                    raise ValueError("If barcode contains '-' you should select ArrayID button instead")
        if selected_value == "array_id":
            for wafer_id in wafer_ids:
                if "-" not in wafer_id:
                    raise ValueError("You should select WaferID button instead")

    def submit_data(self):
        try:
            operator_initial = self.operator_initial_entry.get()
            array_type = self.array_type_combobox.get()
            pre_processing_step = self.pre_processing_step_combobox.get()
            wafer_ids = [entry.get() for entry in self.wafer_id_entries if entry.get()]
            selected_value = self.wafer_array_id_var.get()
            selected_array_detail_value = self.array_detail_var.get()

            if not wafer_ids or not array_type or not pre_processing_step:
                raise ValueError("Array, Pre-processing Step and Wafer/Array ID are required!")

            self.check_id(wafer_ids)

            preprocessing_tracking_df = pd.DataFrame(
                columns=["Datetime",
                         "Initial",
                         "WaferID",
                         "ArrayPosition",
                         "ArrayID",
                         "PreprocessingStep"])

            current_time = datetime.now()
            time_stA = current_time.timestA()
            date_time = datetime.fromtimestA(time_stA)

            #  New Modification
            conn_str = self.get_db_details()
            engine = create_engine(conn_str)
            connection = engine.connect()

            for wafer_id in wafer_ids:
                if selected_value in ["array_id"]:
                    array_pos = 'Array{}'.format(wafer_id[-5])

                    #  New Modification
                    selected_query = f"SELECT * FROM LaserEngraver WHERE {array_pos} = ?"
                    params = (wafer_id)
                    result = connection.execute(selected_query, params)
                    if not result.fetchone():
                        raise ValueError(f"Array ID {wafer_id} does not exist in {array_pos} of LaserEngraver!")

                    preprocessing_tracking_df.loc[len(preprocessing_tracking_df.index)] = [date_time,
                                                                                           operator_initial,
                                                                                           str(''.join([x for x in
                                                                                                        wafer_id.split(
                                                                                                            '-') if
                                                                                                        x.isdigit()])),
                                                                                           array_pos,
                                                                                           wafer_id,
                                                                                           pre_processing_step]
                else:
                    array_positions = range(ord('A'), ord('Q'))

                    for array_position in array_positions:
                        array_id = '{}-{}-{}-{}-{}-{}'.format(str(wafer_id)[:4],
                                                              str(wafer_id)[4:7],
                                                              str(wafer_id)[7:],
                                                              chr(array_position),
                                                              'D' if selected_array_detail_value == 'dummy_array' else 'F',
                                                              array_type[0])

                        array_pos = 'Array{}'.format(chr(array_position))

                        #  New Modification
                        selected_query = f"SELECT * FROM LaserEngraver WHERE {array_pos} = ?"
                        params = (array_id)
                        result = connection.execute(selected_query, params)
                        if not result.fetchone():
                            raise ValueError(f"Array ID {array_id} does not exist in {array_pos} of LaserEngraver!")

                        preprocessing_tracking_df.loc[len(preprocessing_tracking_df.index)] = [date_time,
                                                                                               operator_initial,
                                                                                               wafer_id,
                                                                                               array_pos,
                                                                                               array_id,
                                                                                               pre_processing_step]

            #  New Modification
            connection.close()

            conn_str = self.get_db_details()

            engine = create_engine(conn_str)

            for i in range(preprocessing_tracking_df.shape[0]):

                with engine.begin() as connection:

                    try:
                        insert_statement = "INSERT INTO ArrayTransactions (Datetime,Initial,WaferID,ArrayPosition,ArrayID,PreprocessingStep)  VALUES (?,?,?,?,?,?) "

                        params = (preprocessing_tracking_df.iloc[i]['Datetime'],
                                  preprocessing_tracking_df.iloc[i]['Initial'],
                                  preprocessing_tracking_df.iloc[i]['WaferID'],
                                  preprocessing_tracking_df.iloc[i]['ArrayPosition'],
                                  preprocessing_tracking_df.iloc[i]['ArrayID'],
                                  preprocessing_tracking_df.iloc[i]['PreprocessingStep'])

                        connection.execute(insert_statement, params)
                        connection.execute("COMMIT;")

                    finally:
                        engine.dispose()
            messagebox.showinfo(title="Success", message="Data Transfer Successful")

        except Exception as e:
            messagebox.showerror(title="Error", message=str(e))


class Tab2Class:

    def __init__(self, main_frame):

        self.main_frame = main_frame

        style = ttk.Style()
        style.configure("Small.TButton", padding=(0, 0, 0, 0), font=("Arial", 10))

        self.data = pd.DataFrame(columns=["Array Barcode", "Status", "Action Performed"])

        self.create_fields()

    def create_fields(self):
        barcode_label = ttk.Label(self.main_frame, text="Array Barcode:")
        barcode_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.barcode_entry = ttk.Entry(self.main_frame,
                                       width=22)
        self.barcode_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

        action_label = ttk.Label(self.main_frame, text="Action Performed:")
        action_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.action_combo = ttk.Combobox(self.main_frame, values=["Shipped to E", "Scrapped", "Reserved for SAling"], state="readonly")
        self.action_combo.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)

        self.status_label = ttk.Label(self.main_frame, text="Status")
        self.status_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        self.status_entry = tk.Entry(self.main_frame, width=23)
        self.status_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

        check_button = ttk.Button(self.main_frame, text="Check", command=self.check_barcode, style="Small.TButton")
        check_button.grid(row=1, column=2, padx=10, pady=10, sticky=tk.W)

        submit_button = ttk.Button(self.main_frame, text="Submit", command=self.submit_data, style="Small.TButton", state="!disabled")
        submit_button.grid(row=2, column=2, padx=10, pady=10, sticky=tk.E)

    def update_submit_button_state(self):
        selected_value = self.action_combo.get()
        if selected_value:
            self.submit_button.state(['!disabled'])
        else:
            self.submit_button.state(['disabled'])

    def submit_data(self):
        barcode = self.barcode_entry.get()
        action = self.action_combo.get()

        self.data = self.data.append({"Array Barcode": barcode, "Action Performed": action}, ignore_index=True)

        self.barcode_entry.delete(0, tk.END)
        self.action_combo.set('')

        current_time = datetime.now()
        time_stA = current_time.timestA()
        date_time = datetime.fromtimestA(time_stA)

        conn_str = self.get_db_details()

        engine = create_engine(conn_str)

        with engine.begin() as connection:

            try:
                insert_statement = "INSERT INTO ArrayTransactions (Datetime,Initial,WaferID,ArrayPosition,ArrayID,PreprocessingStep)  VALUES (?,?,?,?,?,?) "
                barcode_id = barcode.split("-")
                array_pos = "Array{}".format(barcode_id[-3])
                wafer_id = "".join([x for x in barcode_id if x.isdigit()])
                params = (date_time, "", wafer_id, array_pos, barcode, action)

                connection.execute(insert_statement, params)
                connection.execute("COMMIT;")

                messagebox.showinfo(title="Success", message="Data Transfer Successful")

            except Exception as e:
                messagebox.showerror(title="Error", message=str(e))

            finally:
                engine.dispose()

        current_time = datetime.now()
        time_stA = current_time.timestA()
        date_time = datetime.fromtimestA(time_stA)

        conn_str = self.get_db_details()

        engine = create_engine(conn_str)

        with engine.begin() as connection:

            try:
                insert_statement = "INSERT INTO ArrayTransactions (Datetime,Initial,WaferID,ArrayPosition,ArrayID,PreprocessingStep)  VALUES (?,?,?,?,?,?) "
                barcode_id = barcode.split("-")
                array_pos = "Array{}".format(barcode_id[-3])
                wafer_id = "".join([x for x in barcode_id if x.isdigit()])
                params = (date_time, "", wafer_id, array_pos, barcode, action)

                connection.execute(insert_statement, params)
                connection.execute("COMMIT;")

            finally:
                engine.dispose()

    def get_db_details(self):
        server = ''
        database = ''

        username = ''
        password = ''

        conn_str = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=SQL Server'

        return conn_str

    def check_barcode(self):
        barcode = self.barcode_entry.get()
        barcode = str(barcode)

        conn_str = self.get_db_details()
        engine = create_engine(conn_str)
        conn = engine.raw_connection()
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM PartPassRejectNew WHERE [Barcode] = '{barcode}'")
        row = cursor.fetchone()
        check = self.barcode_entry.get()
        try:
            if row is not None:
                status = row[1]
                self.status_entry.delete(0, tk.END)
                if status == 'PASS':
                    self.status_entry.insert(0, "PASS")
                    self.status_entry.config(bg='green')
                else:
                    self.status_entry.insert(0, "FAIL")
                    self.status_entry.config(bg='red')
            elif check[:2] == "NR":
                raise ValueError("Re-scan the Barcode, NR was found")
            elif len(check) <= 15:
                raise ValueError("Enter a Valid BarcodeID")
            else:
                raise ValueError("Barcode has not been found in the PartPassRejectNew table")

        except Exception as e:
            messagebox.showerror(title="Error", message=str(e))
        finally:
            cursor.close()
            conn.close()


if __name__ == '__main__':
    root = ThemedTk(theme="breeze")
    gui = GUI(root)
    root.mainloop()