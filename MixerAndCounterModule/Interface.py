# Para convertir cadenas en su clase original
import ast
# Para evitar bloquear el hilo principal
import threading
# Para widgets
import tkinter as tk
# Para tablas y scrollbars
from tkinter import ttk
# Para importar archivos
from tkinter import filedialog
# Para mostrar mensajes al usuario en una ventana emergente
from tkinter import messagebox
# Para descifrar
from Decryptor import Decryptor
# Conversiones de formatos
from Exporter import Exporter as Exp
# Verificar firmas
import BlindSignatureVerifier as BSV
# Para reconstruir la clave privada del esquema de cifrado
from KeyRecoveryComponent import KeyRecoveryComponent as KRC
# Manejador de la base de datos
import BookWorm as BW

class Interface:
    #___________________________________________________________________________________________________________________
    def __init__(self, root):
        # Configuración del frame
        # Ventana raiz
        self._root = root
        self._root.title("Módulo de Mezcla y Conteo")
        self._root.geometry("1720x920")
        self._root.resizable(True, True)

        # Parametrizacion de textos
        self.title_font = ("Ubuntu Sans Mono Regular", 12, "bold")
        self.subtitle_font = ("Ubuntu Sans Mono Regular", 11)

        # Notebook para las diferentes pestañas
        self.notebook = ttk.Notebook(self._root)
        self.notebook.pack(fill="both", expand=True)

        # Variables para almacenar las rutas de los archivos
        self.vault_path = ""
        self.vault_sign_path = ""
        self.puk_sign_path = ""
        self.shares_paths = []

        # Variables para la recuperacion de la clave de descifrado
        self.shares = []
        self.secret = None

        # Objetos necesarios para la verificación de firmas
        self.public_key = None
        self.vault_sign = None
        self.pre_count_table = None # Treeview
        self.votes_table = None # Treeview
        self.votes = None # Lista de votos recuperados de la bd
        self.pre_count = None # Lista de registros de preconteo

        # Tablas de datos descifrados
        self.plain_pre_count_table = None
        self.plain_votes_table = None

        # Variables para verificar la importación de archivos __________________

        # Necesario para verificacion de firmas y descifrado
        self.is_vault_imported = False

        # Necesarios para verificacion de firmas
        self.is_vault_sign_imported = False
        self.is_signature_imported = False

        # Necesarios para descifrado
        self.are_shares_imported = False

        # _______________________________________________________________________

        # Padding vertical que tendran los widgets
        self.default_pady = 5
        # Padding horizontal interno del texto de los botones
        self.default_padx_buttons=2

        # Leyenda default de botones de importacion de archivos
        self.default_import_legend = "Importar"

        # Nombres de los archivos
        self.vault_name = "vault.db"
        self.vault_sign_name = "vault_sign.pem"
        self.puk_signature_name = "BsgPukChaum.pem"
        self.shares_names = "EkgPrkElGamal*Of*.pem"

        # Variables con las leyendas para importar archivos
        self.vault_request_default = f"Debe importar \"{self.vault_name}\""
        self.vault_sign_req_default = f"Debe importar \"{self.vault_sign_name}\""
        self.puk_signature_request_default = f"Debe importar \"{self.puk_signature_name}\""



        ################################################################################################################
        # Tab de verificacion de firmas



        self.verify_signature_frame = tk.Frame(self.notebook, bg="#F0F0F0")
        self.notebook.add(self.verify_signature_frame, text="Verificación de Firmas")

        # Se configuran las columnas para que se expandan y centren los widgets ocupando el mismo espacio cada columna
        # Este frame tendra tres columnas
        for i in range(3):
            self.verify_signature_frame.grid_columnconfigure(i, weight=1, uniform="0")

        row_vsf = self.generate_counter() # Se inicializa el contador que contiene la posicion de la fila actual
        #===============================================================================================================
        row_value = next(row_vsf)  # Se obtiene el valor de la fila para el wigdet que colocaré a continuación

        info_verify_signature_frame_label = tk.Label(
            self.verify_signature_frame,
            text="En esta pestaña, se verificará la integridad de la bóveda electoral. "
                 "Por favor, importe los archivos solicitados a continuación:",
            font=self.title_font,
        )

        info_verify_signature_frame_label.grid(row=row_value, column=0, columnspan=3, sticky="ew")

        #===============================================================================================================
        # En cada columna de esta fila hay un contenedor de tres widgets (file_req_lbl, import_btn, file_path_lbl)
        row_value = next(row_vsf)

        self.widget_containers = {}

        # Widgets de bóveda (db)
        self.vault_container = self.create_widget_container(
            parent_frame=self.verify_signature_frame,
            container_name='vault_container',
            title="Bóveda electoral (*.db)",
            import_command=lambda: self.import_file(
                container_name='vault_container',
                file_type="DataBase",
                file_name=self.vault_name,
                request_default=self.vault_request_default,
                is_imported_attribute='is_vault_imported',
                path_attribute='vault_path'
            ),
            file_path_label=self.vault_request_default,
            row=row_value,
            column=0
        )

        # Widgets de firma de bóveda
        self.vault_sign_container = self.create_widget_container(
            parent_frame=self.verify_signature_frame,
            container_name='vault_sign_container',
            title="Firma de la bóveda electoral (*.pem)",
            import_command=lambda: self.import_file(
                container_name='vault_sign_container',
                file_type="Vault Sign",
                file_name=self.vault_sign_name,
                request_default=self.vault_sign_req_default,
                is_imported_attribute='is_vault_sign_imported',
                path_attribute='vault_sign_path'
            ),
            file_path_label=self.vault_sign_req_default,
            row=row_value,
            column=1
        )

        # Widgets de clave de verificacion de firmas
        self.puk_signature_container = self.create_widget_container(
            parent_frame=self.verify_signature_frame,
            container_name='puk_signature_container',
            title="Clave pública de firma (*.pem)",
            import_command=lambda: self.import_file(
                container_name='puk_signature_container',
                file_type="Archivo PEM",
                file_name=self.puk_signature_name,
                request_default=self.puk_signature_request_default,
                is_imported_attribute='is_signature_imported',
                path_attribute='puk_sign_path'
            ),
            file_path_label=self.puk_signature_request_default,
            row=row_value,
            column=2
        )

        #===============================================================================================================
        row_value = next(row_vsf)

        self.start_verification_button = tk.Button(
            self.verify_signature_frame,
            text="Continuar",
            state="disabled",
            command=lambda: self.create_progress_window(
                target_function=self.load_db_data,
            )
        )
        self.start_verification_button.grid(row=row_value, column=0, columnspan=3, pady=0)

        #===============================================================================================================
        self.vault_ver_res_lbl_row = next(row_vsf)

        self.vault_verification_result_label = tk.Label(
            self.verify_signature_frame,
            text="",
            font=("Arial", 14),
        )
        # Se renderiza (grid) al cargar datos y verificar firmas

        #===============================================================================================================
        row_value = next(row_vsf)

        self.pre_count_label = tk.Label(
            self.verify_signature_frame,
            text="Verificación de firmas de la tabla de preconteo:",
            font=self.title_font
        )
        self.pre_count_label.grid(row=row_value, column=0, columnspan=3, pady=self.default_pady, sticky="n")

        #===============================================================================================================
        row_value = next(row_vsf)

        self.pre_count_table = self.create_table(
            frame=self.verify_signature_frame,
            row=row_value,
            column=0,
            columnspan=3,
            columns=("ID", "Result", "Signature", "Integrity"),
            headings=("ID", "Conteo", "Firma", "Integridad"),
            column_widths=(300, 620, 620, 100),
            column_min_widths=(300, 21100, 21100, 100),
            stretch_configs=(False, False, False, True),
            table_height=6
        )

        #===============================================================================================================
        row_value = next(row_vsf)

        self.votes_label = tk.Label(
            self.verify_signature_frame,
            text="Verificación de firmas de la tabla de votos:",
            font=self.title_font
        )
        self.votes_label.grid(row=row_value, column=0, columnspan=3, pady=self.default_pady)

        #===============================================================================================================
        row_value = next(row_vsf)
        self.votes_table = self.create_table(
            frame=self.verify_signature_frame,
            row=row_value,
            column=0,
            columnspan=3,
            columns=("ID", "Vote", "Signature", "Integrity"),
            headings=("ID", "Voto", "Firma", "Integridad"),
            column_widths=(60, 740, 740, 100),
            column_min_widths=(60, 21100, 21100, 100),
            stretch_configs=(True, False, False, True),
            table_height=18
        )

        #===============================================================================================================
        row_value = next(row_vsf)

        self.goto_pre_count_button = tk.Button(
            self.verify_signature_frame,
            text="Continuar",
            state='disabled',
            command=self.goto_pre_count
        )
        self.goto_pre_count_button.grid(row=row_value, column=2, pady=self.default_pady, padx=30, sticky="e")


        # Fin del tab de verificacion de firmas
        ################################################################################################################
        # Tab de Mezcla



        # Se crea el tab de mezcla
        self.mix_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.mix_frame, text="Mezcla", state='disabled')



        # Fin del tab de Mezcla
        ################################################################################################################
        # Tab de preconteo



        # Objetos para confirmar o rechazar la conformidad con el preconteo
        self.shares_table = None
        self.accept_pre_count_button = None
        self.deny_pre_count_button = None
        self.accept_pre_count_label = None

        self.pre_count_frame = tk.Frame(self.notebook, bg="#F0F0F0")
        self.notebook.add(self.pre_count_frame, text="Preconteo", state='normal')
        self.pre_count_frame.grid_columnconfigure(0, weight=1)

        row_pcf = self.generate_counter()
        #===============================================================================================================
        self.info_pre_count_frame_label = tk.Label(
            self.pre_count_frame,
            font=self.title_font,
            text="Para iniciar la fase de conteo, se debe contar con una mínima cantidad de fragmentos de la clave de "
                 "descifrado. Para conocer este valor, importe alguno de los fragmentos.\n"
                 "A continuación, verifique la cantidad que se especifica en la columna \"Fragmentos requeridos\" de la "
                 "tabla debajo.\nContinúe importando fragmentos hasta llegar a la cantidad especificada.",

        )
        self.info_pre_count_frame_label.grid(row=next(row_pcf), column=0, sticky="ew")

        #===============================================================================================================
        # Contenedor para centrar los widgets
        self.shares_container = tk.Frame(self.pre_count_frame, bg="#F0F0F0")
        self.shares_container.grid_columnconfigure(0, weight=4)
        for i in range(1, 5): #[1,4]
            self.shares_container.grid_columnconfigure(i, weight=1, uniform="0")
        self.shares_container.grid(row=next(row_pcf), column=0, columnspan=1, padx=30, pady=self.default_pady, sticky="nsew")

        col_shares_container = self.generate_counter()
        self.share_name_label = tk.Label(
            self.shares_container,
            font=self.title_font,
            text="Fragmento",
            relief="groove"
        )
        self.share_name_label.grid(row=0, column=next(col_shares_container), sticky="ew")

        self.share_number_label = tk.Label(
            self.shares_container,
            font=self.title_font,
            text="ID de fragmento",
            relief="groove"
        )
        self.share_number_label.grid(row=0, column=next(col_shares_container), sticky="ew")

        self.share_number_label = tk.Label(
            self.shares_container,
            font=self.title_font,
            text="Fragmentos requeridos",
            relief="groove"
        )
        self.share_number_label.grid(row=0, column=next(col_shares_container), sticky="ew")

        self.required_shares_label = tk.Label(
            self.shares_container,
            font=self.title_font,
            text="Fragmentos totales",
            relief="groove"
        )
        self.required_shares_label.grid(row=0, column=next(col_shares_container), sticky="ew")

        self.required_shares_label = tk.Label(
            self.shares_container,
            font=self.title_font,
            text="Fragmentos importados",
            relief="groove"
        )
        self.required_shares_label.grid(row=0, column=next(col_shares_container), sticky="ew")

        self.req_shares = None
        self.total_shares = None

        #===============================================================================================================
        import_share_button = tk.Button(
            self.pre_count_frame,
            text=self.default_import_legend,
            command=self.import_share,
            padx=self.default_padx_buttons
        )
        import_share_button.grid(row=next(row_pcf), column=0, columnspan=5, padx=5, pady=self.default_pady)

        #===============================================================================================================
        self.reconstruct_button = tk.Button(
            self.pre_count_frame,
            text="Reconstruir clave de descifrado",
            state='disabled',
            command=self.show_confirmation_dialog_to_recover_decrypt_key
        )
        self.reconstruct_button.grid(row=next(row_pcf), column=0, pady=20)

        #===============================================================================================================
        self.plain_pre_count_table = self.create_table(
            frame=self.pre_count_frame,
            row=5,
            column=0,
            columns=("ID", "PreCount"),
            columnspan=3,
            headings=("Candidato", "Cantidad de votos a favor"),
            column_widths=(820, 820),
            column_min_widths=(820, 820),
            stretch_configs=(True, True),
            table_height=6
        )

        # Fin del tab de preconteo
        ################################################################################################################
        # Objetos para el tab de descifrado
        self.decrypt_frame = None



    # Fin del constructor ______________________________________________________________________________________________



    # Metodo auxiliar para el numero de fila
    @staticmethod
    def generate_counter(start=0, step=1):
        n = start
        while True:
            yield n
            n += step

    # Métodos genéricos

    # Metodo para crear un frame con un request_label, un import_button y debajo de ambos un path_label
    # Necesario para los widgets de la importacion de la bóveda, firma de la bóveda y clave pública de firma
    def create_widget_container(self, parent_frame, container_name, title, import_command, file_path_label, row, column):
        # Crear contenedor
        container = tk.Frame(parent_frame)
        container.grid(row=row, column=column, pady=self.default_pady, sticky="ew")
        container.configure(background="#F0F0F0")
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        # Label que solicita al usuario el archivo
        file_requested_label = tk.Label(
            container,
            text=title,
            font=self.title_font
        )
        file_requested_label.grid(row=0, column=0, sticky="e")

        # Botón para seleccionar el archivo solicitado
        import_file_button = tk.Button(
            container,
            text=self.default_import_legend,
            command=import_command,
            padx=self.default_padx_buttons
        )
        import_file_button.grid(row=0, column=1, padx=5, sticky="w")

        # Label donde se imrpimirá la ruta del archivo seleccionado
        file_path_label = tk.Label(
            container,
            text=file_path_label,
            font=self.subtitle_font,
            relief="ridge",
            fg="red",
            bg="white"
        )
        file_path_label.grid(row=1, column=0, columnspan=2, padx=10, pady=0, sticky="ew")

        # Almacena los widgets en el diccionario de contenedores
        self.widget_containers[container_name] = {
            'container': container,
            'file_path_label': file_path_label
        }

        return container

    def import_file(self, container_name, file_type, file_name, request_default, is_imported_attribute, path_attribute):
        # Abre el cuadro de diálogo de selección de archivo
        file_path = filedialog.askopenfilename(
            title=f"Busque y seleccione el archivo {file_name}",
            filetypes=[(file_type, file_name)]  # Especifica el tipo de archivo
        )

        # Si se seleccionó un archivo
        if file_path:
            # Actualiza el atributo de ruta del archivo
            setattr(self, path_attribute, file_path)

            # Actualiza el texto de la etiqueta correspondiente
            self.widget_containers[container_name]['file_path_label'].config(text=f"{file_path}", fg="blue")

            # Cambia el estado de importación a True
            setattr(self, is_imported_attribute, True)
        else:
            # Si no se seleccionó un archivo, restablece el valor
            setattr(self, path_attribute, "")

            # Actualiza la etiqueta con el valor por defecto
            self.widget_containers[container_name]['file_path_label'].config(
                text=f"{request_default}",
                fg="red"
            )

            # Cambia el estado de importación a False
            setattr(self, is_imported_attribute, False)

        # Comprueba que los archivos para la verificación de firmas están importados
        self.check_verify_files_are_imported()

    def import_share(self):
        file_path = filedialog.askopenfilename(
            title=f"Seleccionar {self.shares_names}",
            filetypes=[("Share Files", "EkgPrkElGamal*Of*.pem")]
        )
        if file_path:
            if file_path not in self.shares_paths:
                self.shares_paths.append(file_path)
                self.load_share_data(len(self.shares_paths)-1)
        else:
            self.shares_paths.clear()
            self.reconstruct_button.configure('disabled')

    def check_verify_files_are_imported(self):
        if self.is_vault_imported and self.is_signature_imported and self.is_vault_sign_imported:
            self.start_verification_button.config(state='normal')
        else:
            self.start_verification_button.config(state='disabled')
            self.notebook.tab(1, state='disabled')
            #self.notebook.tab(2, state='disabled')
            self.notebook.select(0)

    def goto_pre_count(self):
        self.notebook.select(2)

    def load_db_data(self, progress_window, info_label, progress_bar, percentage_label):
        try:
            self.start_verification_button.config(state='disabled')
            self.goto_pre_count_button.config(state='normal')
            self.notebook.tab(2, state='normal')
            print("Ruta de la base de datos:", self.vault_path)

            # Se carga la clave pública de firma
            self.public_key = Exp.import_key(self.puk_sign_path)
            # Se crea instancia de BookWorm para obtener registros de la bd
            bw = BW.BookWorm(self.vault_path)
            # Se obtienen los registros de las tablas de la base de datos
            self.votes = bw.fetch_records("votos")
            self.pre_count = bw.fetch_records("conteo")

            # Verifica si no se obtuvieron registros
            if not self.votes and not self.pre_count:
                messagebox.showinfo(
                    "Bóveda vacía",
                    "No se encontraron votos ni registros de preconteo en la base de datos."
                )
                progress_window.destroy()
                return

            # Lista de votos vacía
            if not self.votes:
                messagebox.showinfo("", "No se encontraron votos en la base de datos.")

            # Lista de preconteo vacía
            if not self.pre_count:
                messagebox.showinfo("", "No se encontraron registros de preconteo en la base de datos.")

            # Se obtiene la cantidad de registros obtenidos para calcular el preconteo
            total_candidates = len(self.pre_count)
            total_votes = len(self.votes)
            total_records = total_candidates + total_votes

            # Inicialización de la variable donde se guardará el progreso parcial
            actual_progress = None
            verifier = BSV.BlindSignatureVerifier(self.public_key)

            # Limpia datos pasados de la tabla de preconteo
            for row in self.pre_count_table.get_children():
                self.pre_count_table.delete(row)

            # Limpia datos pasados de la tabla de votos
            for row in self.votes_table.get_children():
                self.votes_table.delete(row)

            # Verificacion de la firma de la bóveda
            self.vault_sign = Exp.import_key(self.vault_sign_path)["sign"]
            vault_data_hex = Exp.get_hex_of_file(self.vault_path)
            is_vault_valid = verifier.verify(self.vault_sign, vault_data_hex)
            if is_vault_valid:
                self.vault_verification_result_label.config(
                    fg="blue",
                    font=self.subtitle_font,
                    text="La firma de la bóveda es válida",
                )
            else:
                self.vault_verification_result_label.config(
                    fg="red",
                    font=self.subtitle_font,
                    text="La firma de la bóveda es inválida",
                )
            #Se coloca el widget con el resultado de verificación
            self.vault_verification_result_label.grid(column=0, row=self.vault_ver_res_lbl_row, columnspan=3,
                                                      pady=self.default_pady)

            # Carga de datos de preconteo
            progress_window.title("Cargando registros (1/2)")
            info_label.config(text="Cargando datos de preconteo. Por favor, espere...")

            # Inserta registros en la tabla 'preconteo' mostrando el progreso
            for idx, pre_count_table_data in enumerate(self.pre_count):
                candidate, result, signature = pre_count_table_data[0], pre_count_table_data[1], pre_count_table_data[2]

                row_id = self.pre_count_table.insert("", "end", values=(candidate, result, signature, ""))
                # Mantiene enfocada la última fila has
                self.pre_count_table.selection_set(row_id)  # Selecciona la fila
                self.pre_count_table.see(row_id)  # Se desplaza para mostrarla

                progress = (idx + 1) * 100 / total_records
                progress_window.after(0, self.update_progress, progress_bar, percentage_label, progress)

                # Si se está en la última iteración
                if (idx+1) == total_candidates:
                    # Se guarda el progreso actual
                    actual_progress = progress
                    # Elimina el enfoque del registro
                    self.pre_count_table.selection_remove(row_id)


            progress_window.title("Cargando registros (2/2)")
            info_label.config(text="Cargando los votos cifrados. Por favor, espere...")

            for idx, vote in enumerate(self.votes):
                candidate, vote, signature = vote[0], vote[1], vote[2]

                row_id = self.votes_table.insert("", "end", values=(candidate, vote, signature, ""))
                # Mantiene enfocada la última fila has
                self.votes_table.selection_set(row_id)  # Selecciona la fila
                self.votes_table.see(row_id)  # Se desplaza para mostrarla

                progress = actual_progress + ((idx + 1) * 100 / total_records)
                progress_window.after(0, self.update_progress, progress_bar, percentage_label, progress)

                if (idx+1) == total_votes:
                    # Elimina el enfoque del registro
                    self.votes_table.selection_remove(row_id)

            # Se reinicia el progreso del primer for
            actual_progress = 0

            progress_window.title("Verificando integridad (1/2)")
            info_label.config(text="Verificando las firmas de los datos de preconteo. Por favor, espere...")

            # Verifica firmas de preconteo
            for idx, item_id in enumerate(self.pre_count_table.get_children()):
                pre_count = self.pre_count[idx]
                candidate, result, signature = pre_count[0], pre_count[1], pre_count[2]

                int_signature = Exp.b64_to_dictionary(signature)['sign']
                dict_result = Exp.b64_to_dictionary(result)
                # dict -> tuple -> str
                result_available_to_be_verified = str((dict_result['alpha'], dict_result['betha']))

                is_valid = "Válido" if verifier.verify(int_signature, result_available_to_be_verified) else "Inválido"
                tag = "valid" if is_valid == "Válido" else "invalid"

                current_values = self.pre_count_table.item(item_id, "values")
                updated_values = current_values[:-1] + (is_valid,)

                self.pre_count_table.item(item_id, values=updated_values, tags=(tag,))
                self.pre_count_table.selection_set(item_id)
                self.pre_count_table.see(item_id)

                progress = actual_progress + ((idx + 1) * 100 / total_records)
                progress_window.after(0, self.update_progress, progress_bar, percentage_label, progress)

                # Si es la última iteración
                if (idx + 1) == total_candidates:
                    # Guarda el progreso parcial
                    actual_progress = progress
                    self.pre_count_table.selection_remove(item_id)

            print("Datos cargados en la tabla 'preconteo'.")

            progress_window.title("Verificando integridad (2/2)")
            info_label.config(text="Verificando integridad de los votos. Por favor, espere...")

            # Verificación de firmas de votos
            for idx, item_id in enumerate(self.votes_table.get_children()):
                votes = self.votes[idx]
                id, vote, signature = votes[0], votes[1], votes[2]
                int_signature = Exp.b64_to_dictionary(signature)['sign']
                dict_vote = Exp.b64_to_dictionary(vote)
                vote_available_to_be_verified = str((dict_vote['alpha'], dict_vote['betha']))
                verifier = BSV.BlindSignatureVerifier(self.public_key)
                is_valid = "Válido" if verifier.verify(int_signature, vote_available_to_be_verified) else "Inválido"

                # Color del texto de la tabla en función de la validez
                tag = "valid" if is_valid == "Válido" else "invalid"

                current_values = self.votes_table.item(item_id, "values")
                updated_values = current_values[:-1] + (is_valid,)
                self.votes_table.item(item_id, values=updated_values, tags=(tag,))
                # Mantiene enfocada la última fila has
                self.votes_table.selection_set(item_id)  # Selecciona la fila
                self.votes_table.see(item_id)  # Se desplaza para mostrarla

                progress = actual_progress + ((idx + 1) * 100 / total_records)
                if (idx + 1) == total_votes:
                    self.votes_table.selection_remove(item_id)
                progress_window.after(0, self.update_progress, progress_bar, percentage_label, progress)

            print("Datos cargados en la tabla 'votos'.")

            # Habilitar las pestañas "Verificación de Firmas" y "Mezcla y Conteo"
            self.notebook.tab(2, state='normal')

        except Exception as e:
            messagebox.showerror("Error al insertar los registros de la base de datos:", f"{e}")
        finally:
            progress_window.destroy()

    def update_progress(self, progress_bar, percentage_label, progress):
        progress_bar['value'] = progress
        percentage_label.config(text=f"{progress:.1f}%")

    def show_confirmation_dialog_to_recover_decrypt_key(self):
        # Ventana emergente
        confirm_dialog = tk.Toplevel(self._root)
        confirm_dialog.title("¡Atención!")
        tk.Label(
            confirm_dialog,
            text="Si continúa, se reconstruirá la clave de descifrado para mostrar el preconteo."
        ).pack(pady=10)

        # Botones de Aceptar y Cancelar
        btn_frame = tk.Frame(confirm_dialog)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Aceptar",
                  command=lambda: [confirm_dialog.destroy(),
                                   self.load_shares_and_recover_secret()]
                  ).pack(side="left",padx=5)

        tk.Button(btn_frame, text="Cancelar", command=confirm_dialog.destroy).pack(side="right", padx=5)

    def load_shares_and_recover_secret(self):
        print(f"Before: {self.shares}")
        self.reconstruct_button.configure(state='disabled')

        def task():
            try:
                # Cargar cada archivo .pem y convertirlo a diccionario
                print(self.shares_paths)
                for path in self.shares_paths:
                    share = Exp.import_key(path)
                    print(share)
                    self.shares.append(share)

                print(self.shares)
                recovery_component = KRC(self.shares)
                self.secret = recovery_component.recover_secret()
                print(self.secret)

                self._root.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Éxito",
                        "Clave reconstruida exitosamente."
                    )
                )

                self._root.after(0, lambda: self.create_progress_window(
                    target_function=self.load_plain_pre_count_data,
                    win_title="Insertando datos en la tabla"
                ))
            except Exception as e:
                self._root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Error",
                        f"Se produjo un error al recuperar el secreto: {e}"
                    )
                )

        # Ejecuta en un hilo separado
        threading.Thread(target=task, daemon=True).start()

    def load_plain_pre_count_data(self, progress_window, info_label, progress_bar, percentage_label):
        try:
            if isinstance(self.secret, str):
                self.secret = ast.literal_eval(self.secret)
                print(f"Secreto convertido de tipo str a {type(self.secret)}")

            total_candidates = len(self.pre_count)

            # Limpia los datos cargados anteriormente
            for row in self.plain_pre_count_table.get_children():
                self.plain_pre_count_table.delete(row)

            progress_window.title("Cargando datos en texto claro")
            info_label.config(text="Cargando datos de preconteo en texto claro...")

            row_id = None
            for idx, pre_count_table in enumerate(self.pre_count):
                id_, result, signature = pre_count_table[0], pre_count_table[1], pre_count_table[2]

                int_signature = Exp.b64_to_dictionary(signature)['sign']
                dict_result = Exp.b64_to_dictionary(result)
                result_available_to_be_decrypted = (dict_result['alpha'], dict_result['betha'])
                result_available_to_be_verified = str(result_available_to_be_decrypted)
                verifier = BSV.BlindSignatureVerifier(self.public_key)
                is_valid = "Válido" if verifier.verify(int_signature, result_available_to_be_verified) else "Inválido"

                dec = Decryptor(self.secret["P"], self.secret["G"], self.secret["PrK"])
                plain_pre_count = dec.decipher(result_available_to_be_decrypted)

                if is_valid == "Válido":
                    row_id = self.plain_pre_count_table.insert("", "end", values=(id_, plain_pre_count))
                    self.plain_pre_count_table.selection_set(row_id)
                    self.plain_pre_count_table.see(row_id)

                progress = (idx + 1) * 100 / total_candidates
                progress_window.after(0, self.update_progress, progress_bar, percentage_label, progress)

                if (idx + 1) == total_candidates:
                    self.plain_pre_count_table.selection_remove(row_id)

            accept_pre_count_container = tk.Frame(self.pre_count_frame, bg="#F0F0F0")
            accept_pre_count_container.grid(row=6, column=0, pady=10, padx=500)
            accept_pre_count_container.grid_columnconfigure(0, weight=3)
            accept_pre_count_container.grid_columnconfigure(1, weight=1)
            accept_pre_count_container.grid_columnconfigure(2, weight=1)

            self.accept_pre_count_label = tk.Label(
                accept_pre_count_container,
                font=self.title_font,
                text="¿Está de acuerdo con el preconteo?",
                bg="white",
            )
            self.accept_pre_count_label.grid(row=0, column=0, pady=self.default_pady, sticky="ew")

            self.accept_pre_count_button = tk.Button(
                accept_pre_count_container,
                text="Sí",
                command=self.pre_count_accepted
            )
            self.accept_pre_count_button.grid(row=0, column=1, pady=10)

            self.deny_pre_count_button = tk.Button(
                accept_pre_count_container,
                text="No",
                command=lambda: self.create_progress_window(
                    target_function=self.create_decrypt_tab_and_load_plain_votes_data,
                    win_title="Descifrando votos",
                    info_label="Insertando votos descifrados en la tabla..."
                )
            )
            self.deny_pre_count_button.grid(row=0, column=2, pady=10)

            progress_window.after(0, progress_window.destroy)

        except Exception as e:
            messagebox.showerror("Error al descifrar el preconteo", f": {e}")
            progress_window.after(0, progress_window.destroy)

    def pre_count_accepted(self):
        messagebox.showinfo("", "Conteo finalizado.")
        self.accept_pre_count_button.config(state='disabled')
        self.deny_pre_count_button.config(state='disabled')
        self.accept_pre_count_label.config(text='Conteo finalizado.')


    def create_decrypt_tab_and_load_plain_votes_data(self, progress_window, info_label, progress_bar, percentage_label):
        try:
            self.accept_pre_count_button.config(state='disabled')
            self.deny_pre_count_button.config(state='disabled')
            self.accept_pre_count_label.config(text='Conteo finalizado.')
            # Se crea el tab de descifrado
            self.decrypt_frame = tk.Frame(self.notebook, bg="#F0F0F0")
            self.notebook.add(self.decrypt_frame, text="Descifrado", state='normal')
            self.decrypt_frame.grid_columnconfigure(0, weight=1)

            # Fila 1: Label informativo
            self.info_decrypt_frame_label = tk.Label(
                self.decrypt_frame,
                font=self.title_font,
                text="En esta pestaña se muestran los votos descifrados, puede contar los votos manualmente para "
                     "verificar el preconteo.",
            )
            self.info_decrypt_frame_label.grid(row=0, column=0, sticky="ew")

            self.plain_votes_table = self.create_table(
                frame=self.decrypt_frame,
                row=1,
                column=0,
                columnspan=3,
                columns=("ID", "Candidate"),
                headings=("ID (creado para el despliegue de votos)", "Candidato seleccionado"),
                column_widths=(100, 200),
                column_min_widths = (100, 200),
                stretch_configs= (True, True),
                table_height=35
            )

            self.notebook.select(3)

            self.notebook.tab(3, state='normal')
            self.notebook.select(3)
            total_votes = len(self.votes)

            row_id = None
            for idx, vote in enumerate(self.votes):
                id_, vote, signature = vote[0], vote[1], vote[2]

                int_signature = Exp.b64_to_dictionary(signature)['sign']
                dict_vote = Exp.b64_to_dictionary(vote)
                vote_available_to_be_decrypted = (dict_vote['alpha'], dict_vote['betha'])
                vote_available_to_be_verified = str(vote_available_to_be_decrypted)
                verifier = BSV.BlindSignatureVerifier(self.public_key)
                is_valid = "Válido" if verifier.verify(int_signature, vote_available_to_be_verified) else "Inválido"

                dec = Decryptor(self.secret["P"], self.secret["G"], self.secret["PrK"])
                int_plain_vote = dec.decipher_std(vote_available_to_be_decrypted)
                plain_vote = Exp.int_to_string(int_plain_vote)

                if is_valid == "Válido":
                    # Insertar el registro con la etiqueta correspondiente
                    row_id = self.plain_votes_table.insert("", "end", values=(id_, plain_vote))
                    self.plain_votes_table.selection_set(row_id)
                    self.plain_votes_table.see(row_id)

                progress = (idx + 1) * 100 / total_votes
                progress_window.after(0, self.update_progress, progress_bar, percentage_label, progress)

                if (idx + 1) == total_votes:
                    self.plain_votes_table.selection_remove(row_id)
            messagebox.showinfo("", "Descifrado de votos finalizado.")

        except Exception as e:
            messagebox.showerror("Error al descifrar los votos", f": {e}")
            progress_window.after(0, progress_window.destroy)

    def create_table(self, frame, row, column, columnspan, columns, headings, column_widths, column_min_widths,
                     stretch_configs, container_sticky="nsew", table_height=10):

        # Contenedor de la tabla
        table_container = ttk.Frame(frame)
        table_container.grid(row=row, column=column, columnspan=columnspan, padx=30, pady=self.default_pady,
                             sticky=container_sticky)
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        if headings is not None:
            table = ttk.Treeview(
                table_container,
                columns=columns,
                show="headings",
                height=table_height
            )
        else:
            table = ttk.Treeview(
                table_container,
                columns=columns,
                #show="headings",
                height=table_height
            )

        # Configuración de encabezados y columnas
        for col, heading, width, minwidth, stretch_config in zip(columns, headings, column_widths, column_min_widths,
                                                                 stretch_configs):
            table.heading(col, text=heading)
            table.column(col, anchor="center", width=width, minwidth=minwidth, stretch=stretch_config)

        # Colores para los registros de la tabla
        table.tag_configure("valid", foreground="blue")
        table.tag_configure("invalid", foreground="red")

        # Scrollbars
        vertical_scrollbar = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=table.yview
        )
        table.configure(yscrollcommand=vertical_scrollbar.set)

        horizontal_scrollbar = ttk.Scrollbar(
            table_container,
            orient="horizontal",
            command=table.xview
        )
        table.configure(xscrollcommand=horizontal_scrollbar.set)

        # Coloca los widgets creados
        table.grid(row=0, column=0, sticky="nsew")
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar.grid(row=1, column=0, columnspan=2, sticky="ew")

        return table

    def load_share_data(self, i):

        my_share = Exp.import_key(self.shares_paths[i])
        my_list = [my_share]
        #print(my_share)
        print(f"antes: {my_list}")
        krc = KRC(my_list)
        self.req_shares = my_share["Rs"]
        if len(self.shares_paths) >= self.req_shares:
            self.reconstruct_button.configure(state="normal")
        share_number = my_share["x"]

        item_name = tk.Label(
            self.shares_container,
            bg="white",
            font=self.subtitle_font,
            text=self.shares_paths[i],
        )
        item_name.grid(row=i+1, column=0, sticky="nsew")

        item_id = tk.Label(
            self.shares_container,
            bg="white",
            font=self.subtitle_font,
            text=share_number,
        )
        item_id.grid(row=i + 1, column=1, sticky="nsew")

        #if i==0:
        req_shares_label = tk.Label(
            self.shares_container,
            bg="white",
            font=self.subtitle_font,
            text=self.req_shares,
        )

        total_shares_label = tk.Label(
            self.shares_container,
            bg="white",
            font=self.subtitle_font,
            text=self.shares_paths[0][-5]
        )

        imported_shares_label = tk.Label(
            self.shares_container,
            bg="white",
            font=self.subtitle_font,
            text=len(self.shares_paths),
        )

        req_shares_label.grid(row=1, rowspan=len(self.shares_paths), column=2, sticky="nsew")
        total_shares_label.grid(row=1, rowspan=len(self.shares_paths), column=3, sticky="nsew")
        imported_shares_label.grid(row=1, rowspan=len(self.shares_paths), column=4, sticky="nsew")

    def create_progress_window(self, target_function, win_title="Cargando", win_width=500, win_height=100,
                               info_label=""):
        # Ventana emergente de progreso
        progress_window = tk.Toplevel(self._root)
        progress_window.title(win_title)
        progress_window.geometry(f"{win_width}x{win_height}")
        info_label = ttk.Label(
            progress_window,
            text=info_label
        )
        info_label.pack(pady=10)

        # Barra de progreso
        progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=200, mode="determinate")
        progress_bar.pack(pady=10)

        # Porcentaje de progreso
        percentage_label = ttk.Label(progress_window, text="0%")
        percentage_label.pack()

        # Se lanza la tarea en un hilo independiente
        load_thread = threading.Thread(
            target=self.try_except_launcher,
            args=(target_function, progress_window, info_label, progress_bar, percentage_label)
        )
        load_thread.start()

    def try_except_launcher(self, target_function, progress_window, info_label, progress_bar, percentage_label):
        try:
            target_function(progress_window, info_label, progress_bar, percentage_label)
        except Exception as e:
            info_label.config(text=f"Error: {e}")
        finally:
            progress_window.after(0, progress_window.destroy)

if __name__ == "__main__":
    #root es la ventana
    root = tk.Tk()
    app = Interface(root)
    root.mainloop()