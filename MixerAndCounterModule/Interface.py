# Para convertir cadenas en su clase original
import ast
import hashlib
# Para evitar bloquear el hilo principal
import threading
import time
# Para widgets
import tkinter as tk
import traceback
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
# Mezclar votos
from FakeMixNet import FakeMixNet as FMN
# Para reconstruir la clave privada del esquema de cifrado
from KeyRecoveryComponent import KeyRecoveryComponent as KRC
# Manejador de la base de datos
import BookWorm as BW
from Crypto.Random import random

class Error(Exception):
    pass

class Interface:
    #___________________________________________________________________________________________________________________
    def __init__(self, root):
        # Configuración del frame
        # Ventana raiz
        self.stop_event = threading.Event()
        self._root = root
        self._root.title("Módulo de Mezcla y Conteo")
        # Obtiene el tamaño de la pantalla
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self._root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        #self._root.minsize(width=1720, height=950)
        self._root.resizable(True, True)

        # Parametrizacion de textos
        self.title_font = ("Ubuntu Sans Mono Regular", 12, "bold")
        self.subtitle_font = ("Ubuntu Sans Mono Regular", 11)
        self.winner_font = ("Ubuntu Sans Mono Regular", 24, "bold")

        # Notebook para las diferentes pestañas
        self.notebook = ttk.Notebook(self._root)
        self.notebook.pack(fill="both", expand=True)

        # Variables para almacenar las rutas de los archivos
        self.vault_path = ""
        self.vault_sign_path = ""
        self.puk_sign_path = ""
        self.puk_cipher_path = ""
        self.shares_paths = []
        self.prk_hash_path = ""

        # Variables para la recuperacion de la clave de descifrado
        self.shares = []
        self.secret = None

        # Objetos necesarios para la verificación de firmas
        self.public_key = None
        self.vault_sign = None
        self.is_vault_valid = None
        self.pre_count_table = None # Treeview
        self.votes_table = None # Treeview
        self.votes = None # Lista de votos recuperados de la bd
        self.pre_count = None # Lista de registros de preconteo

        # Tablas de datos descifrados
        self.plain_pre_count_table = None
        self.plain_votes_table = None

        # Variables para verificar la importación de archivos __________________

        # Banderas de importación

        # Bandera de bóveda
        self.is_vault_imported = False

        # Necesarios para verificacion de firmas
        self.is_vault_sign_imported = False
        self.is_signature_imported = False

        # Necesaria para mezclado
        self.is_puk_cipher_imported = False
        self.mixed_votes_not_approved_by_verifier = []

        # Necesarios para conteo y descifrado
        self.are_shares_imported = False
        self.is_prk_hash_imported = False

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
        self.puk_cipher_name = "EkgPukElGamal.pem"
        self.shares_names = "EkgPrkElGamal*Of*.pem"
        self.hash_name = "EkgPrkElGamalDigest.pem"

        # Variables con las leyendas para importar archivos
        self.vault_request_default = f"Debe importar \"{self.vault_name}\""
        self.vault_sign_req_default = f"Debe importar \"{self.vault_sign_name}\""
        self.puk_signature_request_default = f"Debe importar \"{self.puk_signature_name}\""
        self.puk_cipher_request_default = f"Debe importar \"{self.puk_cipher_name}\""
        self.prk_hash_request_default = f"Debe importar \"{self.hash_name}\""



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
        info_verify_signature_frame_label = tk.Label(
            self.verify_signature_frame,
            text="En esta pestaña, se verificará la integridad de la bóveda electoral. "
                 "Por favor, importe los archivos solicitados a continuación:",
            font=self.title_font,
        )
        info_verify_signature_frame_label.grid(row=next(row_vsf), column=0, columnspan=3, sticky="ew")
        self.verify_signature_frame.grid_rowconfigure(next(row_vsf), minsize=20) # Fila de padding

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
        self.start_verification_button = tk.Button(
            self.verify_signature_frame,
            text="Continuar",
            state="disabled",
            command=lambda: self.create_progress_window(
                target_function=self.load_db_data,
            )
        )
        self.start_verification_button.grid(row=next(row_vsf), column=0, columnspan=3, pady=0)
        self.verify_signature_frame.grid_rowconfigure(next(row_vsf), minsize=20) # Fila de padding

        #===============================================================================================================
        self.vault_ver_res_lbl_row = next(row_vsf)

        self.vault_verification_result_label = tk.Label(
            self.verify_signature_frame,
            text="",
            font=("Arial", 14),
        )
        # Se renderiza (grid) al cargar datos y verificar firmas

        #===============================================================================================================
        self.pre_count_label = tk.Label(
            self.verify_signature_frame,
            text="Verificación de firmas de la tabla de preconteo:",
            font=self.title_font
        )
        self.pre_count_label.grid(row=next(row_vsf), column=0, columnspan=3, pady=self.default_pady, sticky="n")

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
            column_min_widths=(300, 14100, 14100, 100),
            stretch_configs=(False, False, False, True),
            table_height=6
        )
        # Se renderiza en la llamada a self.create_table

        #===============================================================================================================
        self.votes_label = tk.Label(
            self.verify_signature_frame,
            text="Verificación de firmas de la tabla de votos:",
            font=self.title_font
        )
        self.votes_label.grid(row=next(row_vsf), column=0, columnspan=3, pady=self.default_pady)

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
            column_min_widths=(60, 14100, 14100, 100),
            stretch_configs=(True, False, False, True),
            table_height=18
        )

        #===============================================================================================================
        row_value = next(row_vsf)

        self.goto_mix_button = tk.Button(
            self.verify_signature_frame,
            text="Continuar",
            state='disabled',
            command=self.goto_mix
        )
        self.goto_mix_button.grid(row=row_value, column=2, pady=self.default_pady, padx=30, sticky="e")


        # Fin del tab de verificacion de firmas
        ################################################################################################################
        # Tab de Mezcla


        # Se crea el tab de mezcla
        self.mix_frame = tk.Frame(self.notebook, bg="#F0F0F0")
        self.notebook.add(self.mix_frame, text="Mezcla", state="disabled")
        self.mix_frame.grid_columnconfigure(0, weight=1)

        row_mf = self.generate_counter()

        #===============================================================================================================
        info_mix_frame_label = tk.Label(
            self.mix_frame,
            font=self.title_font,
            text="En esta pestaña se mostrará el mezclado de votos."
        )
        info_mix_frame_label.grid(row=next(row_mf), column=0, pady=self.default_pady, sticky="ew")
        self.mix_frame.grid_rowconfigure(next(row_mf), minsize=20) # Fila de padding

        #===============================================================================================================
        self.puk_cipher_container = self.create_widget_container(
            self.mix_frame,
            container_name="puk_cipher_container",
            title="Clave pública de cifrado (*.pem)",
            import_command=lambda: self.import_file(
                container_name='puk_cipher_container',
                file_type="Clave de cifrado",
                file_name=self.puk_cipher_name,
                request_default=self.puk_cipher_request_default,
                is_imported_attribute='is_puk_cipher_imported',
                path_attribute='puk_cipher_path'
            ),
            file_path_label=self.puk_cipher_request_default,
            row=next(row_mf),
            column=0,
            padx_container=20
        )

        #===============================================================================================================
        self.table_containers_container = tk.Frame(self.mix_frame, bg="#F0F0F0")
        self.table_containers_container.grid(row=next(row_mf), column=0, padx=30, pady=self.default_pady)
        for i in range(3):
            self.table_containers_container.grid_columnconfigure(i, weight=1, uniform="0")

        self.table_containers = []
        for i in range(3):
            self.table_containers.append(tk.Frame(self.table_containers_container, bg="#F0F0F0"))
            self.table_containers[i].grid_columnconfigure(0, weight=1)
            self.table_containers[i].grid(row=0, column=i, pady=self.default_pady, padx=0, sticky="nsew")

        for i in range(3):
            info_permutation = tk.Label(self.table_containers[i], font=self.title_font, text=f"Mezcla #{i+1}:")
            info_permutation.grid(row=0, column=0, pady=self.default_pady)

        self.mix_table = []

        for i in range(3):
            self.mix_table.append(
                self.create_table(
                    self.table_containers[i],
                    row=1,
                    column=0,
                    columnspan=1,
                    columns=["Vote"],
                    headings=["Voto"],
                    column_widths=[520],
                    column_min_widths=[14100],
                    stretch_configs=[False],
                    table_height=35
                )
            )

        # ==========================================================================================================
        self.goto_pre_count_button = tk.Button(
            self.mix_frame,
            text="Continuar",
            state='disabled',
            command=self.goto_pre_count
        )
        self.goto_pre_count_button.grid(row=next(row_mf), column=0, pady=self.default_pady, padx=30, sticky="e")

        # Fin del tab de Mezcla
        ################################################################################################################
        # Tab de preconteo



        # Objetos para confirmar o rechazar la conformidad con el preconteo
        self.shares_table = None
        self.accept_pre_count_button = None
        self.deny_pre_count_button = None
        self.accept_pre_count_label = None

        self.pre_count_frame = tk.Frame(self.notebook, bg="#F0F0F0")
        self.notebook.add(self.pre_count_frame, text="Preconteo", state="disabled")
        self.pre_count_frame.grid_columnconfigure(0, weight=1)

        row_pcf = self.generate_counter()
        #===============================================================================================================
        self.info_pre_count_frame_label = tk.Label(
            self.pre_count_frame,
            font=self.title_font,
            text="Para iniciar la fase de conteo, se debe contar con una mínima cantidad de fragmentos de la clave de "
                 "descifrado. Para conocer este valor, importe alguno de los fragmentos desde el botón \"Importar "
                 "fragmentos\".\n"
                 "Después de importar el primer fragmento, verifique la cantidad que se especifica en la columna "
                 "\"Fragmentos requeridos\" en la tabla de fragmentos importados de la clave privada. Continúe "
                 "importando fragmentos hasta llegar a dicha cantidad.",

        )
        self.info_pre_count_frame_label.grid(row=next(row_pcf), column=0, sticky="ew")
        self.pre_count_frame.grid_rowconfigure(next(row_pcf), minsize=20) # Fila de padding

        #===============================================================================================================
        self.info_shares_table = tk.Label(
            self.pre_count_frame,
            text="Tabla de fragmentos importados de la clave privada",
            font=self.title_font,
        )
        self.info_shares_table.grid(row=next(row_pcf), column=0, pady=self.default_pady)

        #===============================================================================================================
        self.shares_table = tk.Frame(
            self.pre_count_frame,
            bg="#F0F0F0",
        )
        self.shares_table.grid(row=next(row_pcf), column=0, pady=self.default_pady, sticky="nsew")
        self.shares_table.grid_columnconfigure(0, weight=3, uniform="0")
        self.shares_table.grid_columnconfigure(1, weight=1, uniform="0")


        self.req_shares = None
        self.total_shares = None
        # Diccionario con los widgets de los shares importados
        self.shares_widgets = {
            "share_name": [],
            "share_id": [],
        }

        self.shares_container = tk.Frame(self.shares_table, bg="#F0F0F0")
        self.shares_container.grid(row=0, column=0, padx=30, sticky="nsew")
        self.shares_container.grid_columnconfigure(0, weight=1)
        self.shares_container.grid_rowconfigure(0, weight=1)

        self.share_name_id_table = self.create_table(
            self.shares_container,
            row=0,
            column=0,
            columnspan=1,
            columns=("share_name", "share_id"),
            headings=("Fragmento", "ID"),
            column_widths=(500, 500),
            column_min_widths=(10, 10),
            stretch_configs=(True, True),
            table_height=2
        )

        self.shares_quantities = tk.Frame(self.shares_table, bg="#F0F0F0")
        self.shares_quantities.grid(row=0, column=1, padx=30, sticky="ew")
        self.shares_quantities.grid_columnconfigure(0, weight=1)
        self.shares_quantities.grid_columnconfigure(1, weight=1)
        for i in range(3):
            self.shares_quantities.grid_rowconfigure(i, weight=1)

        info_required_shares = tk.Label(
            self.shares_quantities,
            font=self.title_font,
            text="Fragmentos requeridos",
            relief="solid"
        )
        info_required_shares.grid(row=0, column=0, sticky="ew")

        info_total_shares = tk.Label(
            self.shares_quantities,
            font=self.title_font,
            text="Fragmentos totales",
            relief="solid"
        )
        info_total_shares.grid(row=1, column=0, sticky="ew")

        info_imported_shares = tk.Label(
            self.shares_quantities,
            font=self.title_font,
            text="Fragmentos importados",
            relief="solid"
        )
        info_imported_shares.grid(row=2, column=0, sticky="ew")

        self.numbers_shares = {
            "rs": tk.Label(
                self.shares_quantities,
                bg="white",
                relief="solid"
            ), "ts": tk.Label(
                self.shares_quantities,
                bg="white",
                relief="solid"
            ), "is": tk.Label(
                self.shares_quantities,
                bg="white",
                relief="solid"
            )}
        for i, key in enumerate(self.numbers_shares):
            self.numbers_shares[key].grid(row=i, column=1, sticky="nsew")

        # ===============================================================================================================
        # Contenedor para centrar los widgets
        self.shares_container = tk.Frame(self.pre_count_frame, bg="#F0F0F0")
        self.shares_container.grid_columnconfigure(0, weight=4)

        #===============================================================================================================
        self.import_share_button = tk.Button(
            self.pre_count_frame,
            text="Importar fragmentos",
            command=self.import_share,
            padx=self.default_padx_buttons
        )
        self.import_share_button.grid(row=next(row_pcf), column=0, columnspan=5, padx=5, pady=self.default_pady)
        empty_space_2 = self.get_empty_space(self.pre_count_frame, bg="#F0F0F0")
        empty_space_2.grid(row=next(row_pcf), column=0, sticky="ew")

        #===============================================================================================================
        # Widgets de hash de prk
        self.prk_hash_container = self.create_widget_container(
            parent_frame=self.pre_count_frame,
            container_name='prk_hash_container',
            title="Por favor, importe el hash de la clave de descifrado (*.pem)",
            import_command=lambda: self.import_file(
                container_name='prk_hash_container',
                file_type="Hash",
                file_name=self.hash_name,
                request_default=self.prk_hash_request_default,
                is_imported_attribute='is_prk_hash_imported',
                path_attribute='prk_hash_path'
            ),
            file_path_label=self.prk_hash_request_default,
            row=next(row_pcf),
            column=0,
            padx_container=20
        )
        self.widget_containers["prk_hash_container"]["button"].config(state='disabled')

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
            row=next(row_pcf),
            column=0,
            columns=("ID", "PreCount"),
            columnspan=3,
            headings=("Candidato", "Cantidad de votos a favor"),
            column_widths=(820, 820),
            column_min_widths=(820, 820),
            stretch_configs=(True, True),
            table_height=6
        )

        #===============================================================================================================
        self.accept_pre_count_container_row = next(row_pcf)

        # Fin del tab de preconteo
        ################################################################################################################
        # Objetos para el tab de descifrado
        self.decrypt_frame = None
        self.info_decrypt_frame_label = None
        self.info_count_table_label = None
        self.count_container = None
        self.info_plain_votes_table_label = None
        self.plain_votes_table = None
        self.counter_of_votes_in_favor_dict = {}
        self.count_of_votes_in_favor_label = []
        self.dynamic_plain_votes_table_height = 0


        #Ya que se construyeron todos los objetos
        self._root.bind("<Configure>", self.ajustar_labels)



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
    def create_widget_container(self, parent_frame, container_name, title, import_command, file_path_label, row, column,
                                padx_container=0):
        # Crear contenedor
        container = tk.Frame(parent_frame, bg="#F0F0F0")
        container.grid(row=row, column=column, padx=padx_container, pady=self.default_pady, sticky="ew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        # Label que solicita al usuario el archivo
        file_requested_label = tk.Label(
            container,
            text=title,
            font=self.title_font
        )
        file_requested_label.grid(row=0, column=0, padx=0, sticky="e")

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
            'file_path_label': file_path_label,
            'button': import_file_button,
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

            if file_type == "Clave de cifrado":
                self.do_mix()
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

        if file_type == "Hash":
            self.check_prk_hash_is_imported()

        elif file_type != "Clave de cifrado":
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
            self.set_default_shares_table()

    def check_verify_files_are_imported(self):
        if self.is_vault_imported and self.is_signature_imported and self.is_vault_sign_imported:
            self.start_verification_button.config(state='normal')
        else:
            self.start_verification_button.config(state='disabled')

    def check_prk_hash_is_imported(self):
        if self.is_prk_hash_imported:
            self.reconstruct_button.config(state='normal')
        else:
            self.reconstruct_button.config(state='disabled')


    def goto_mix(self):
        self.notebook.select(1)

    def goto_pre_count(self):
        self.notebook.select(2)

    def load_db_data(self, progress_window, info_label, progress_bar, percentage_label):
        empty_flag = False
        try:
            self.start_verification_button.config(state='disabled')

            # Se carga la clave pública de firma
            self.public_key = Exp.import_key(self.puk_sign_path)
            # Se crea instancia de BookWorm para obtener registros de la bd
            bw = BW.BookWorm(self.vault_path)
            # Se obtienen los registros de las tablas de la base de datos
            self.votes = bw.fetch_records("votos")
            self.pre_count = bw.fetch_records("conteo")
            cancel = False
            # Verifica si no se obtuvieron registros
            if not self.votes and not self.pre_count:
                cancel = True
                empty_flag = True

            # Lista de preconteo vacía
            if not self.pre_count:
                cancel = True
                empty_flag = True

            # Lista de votos vacía
            if not self.votes:
                cancel = True
                empty_flag = True

            if not cancel:
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
                self.is_vault_valid = verifier.verify(self.vault_sign, vault_data_hex)
                if self.is_vault_valid:
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
                    cancel = self.verify_stop_event()
                    if cancel:
                        break
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
                    cancel = self.verify_stop_event()
                    if cancel:
                        break
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
                    cancel = self.verify_stop_event()
                    if cancel:
                        break
                    pre_count = self.pre_count[idx]
                    result, signature = pre_count[1], pre_count[2]

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

                progress_window.title("Verificando integridad (2/2)")
                info_label.config(text="Verificando integridad de los votos. Por favor, espere...")

                # Verificación de firmas de votos
                for idx, item_id in enumerate(self.votes_table.get_children()):
                    cancel = self.verify_stop_event()
                    if cancel:
                        break
                    votes = self.votes[idx]
                    vote, signature = votes[1], votes[2]
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

                if cancel:
                    # Limpia datos pasados de la tabla de preconteo
                    for row in self.pre_count_table.get_children():
                        self.pre_count_table.delete(row)

                    # Limpia datos pasados de la tabla de votos
                    for row in self.votes_table.get_children():
                        self.votes_table.delete(row)

                    self.start_verification_button.config(state="normal")
                    self.vault_verification_result_label.grid_remove()
                    messagebox.showinfo("Atención", "Proceso cancelado por el usuario.")

                else:
                    # Al finalizar debe habilitar el boton para continuar
                    if self.is_vault_valid:
                        self.goto_mix_button.config(state='normal')
                        self.notebook.tab(1, state='normal')
                        self.widget_containers['vault_container']['button'].configure(state='disabled')
                        self.widget_containers['vault_sign_container']['button'].configure(state='disabled')
                        self.widget_containers['puk_signature_container']['button'].configure(state='disabled')
                    else:
                        # Casos cuando la firma de la base de datos no es válida
                        # Consideraciones iniciales
                        # El nombre de la bóveda no fue modificado
                        # La bóveda es correcta (no es una bóveda de otra sesión)
                        # La firma es correcta (el archivo de firma se obtuvo de la bóveda importada)
                        # Se está usando la clave de verificación correcta
                        # Caso 1: Preconteo y votos íntegros: Faltan o sobran votos
                        # 1. Pueden faltar votos si se borró el par voto-firma
                        # 2. Pueden sobrar votos si se usaron los mismos registros de la tabla para crear más registros
                        #       (copiando el par voto-firmay agregandolo como un nuevo registro)
                        # Resultado esperado: El preconteo y el conteo no deberían coincidir

                        # Caso 2: Preconteo corrupto y votos íntegros
                        # En esta situación, se puede estar también cumpliendo el caso 1, pero no hay forma de determinarlo
                        # Basta con un solo registro de preconteo corrupto para que ya no se pueda comprobar el numero de
                        # votos a favor para el candidato del registro afectado

                        # Caso 3: Preconteo íntegro y votos corruptos
                        # Si el preconteo es íntegro, se pueden obtener los resultados pero generaría desconfianza la falta
                        # integridad en los votos

                        # Caso 4: Preconteo corrpto y votos corruptos
                        # Nada sirve

                        # En cualquiera de los casos, no conviene proceder
                        messagebox.showerror("Firma inválida", "La firma de la bóveda es inválida, "
                                                               "el proceso no puede continuar.")

        except Exception as e:
            messagebox.showerror("Error al insertar los registros de la base de datos:", f"{e}")
        finally:
            progress_window.destroy()
            if empty_flag:
                messagebox.showwarning("Bóveda vacía", "No se encontraron votos.")

    def update_progress(self, progress_bar, percentage_label, progress):
        progress_bar['value'] = progress
        percentage_label.config(text=f"{progress:.1f}%")

    def show_confirmation_dialog_to_recover_decrypt_key(self):
        # Ventana emergente
        confirm_dialog = tk.Toplevel(self._root)
        width = 500
        height = 100
        pos_x = int((self.screen_width - width) / 2)
        pos_y = int((self.screen_height - height) / 2)
        confirm_dialog.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
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
        self.widget_containers['prk_hash_container']['button'].configure(state='disabled')

        def task():
            try:
                # Cargar cada archivo .pem y convertirlo a diccionario
                for path in self.shares_paths:
                    share = Exp.import_key(path)
                    self.shares.append(share)

                recovery_component = KRC(self.shares)
                self.secret = recovery_component.recover_secret()
                if isinstance(self.secret, str):
                    self.secret = ast.literal_eval(self.secret)

                # Comprobar hash
                result = self.verify_hash(self.secret)
                if result:
                    self._root.after(
                        0,
                        lambda: messagebox.showinfo(
                            "Éxito",
                            "Clave reconstruida exitosamente."
                        )
                    )
                    self.reconstruct_button.config(state='disabled')
                    self.widget_containers['prk_hash_container']['button'].configure(state='disabled')
                    self.import_share_button.config(state='disabled')

                    self._root.after(0, lambda: self.create_progress_window(
                        target_function=self.load_plain_pre_count_data,
                        win_title="Insertando datos en la tabla"
                    ))

                else:
                    self.set_default_shares_table()
                    self._root.after(
                        0,
                        lambda: messagebox.showwarning(
                            "Error de hash",
                            "Se importaron fragmentos de una clave incorrecta.\n"
                        )
                    )
            except UnicodeDecodeError as e:
                self.set_default_shares_table()
                print(f"{e}\n{traceback.format_exc()}")
                messagebox.showerror("Error de decodificación", "¿Está usando fragmentos de distintas claves?")

            except Exception as e:
                self.set_default_shares_table()
                print(traceback.format_exc())
                if str(e) == "invalid points":
                    messagebox.showerror("Error", "Los fragmentos no son compatibles entre sí."
                                                  "¿Está usando fragmentos de distintas claves?")
                    self.set_default_shares_table()

                else:
                    self._root.after(
                        0,
                        lambda: messagebox.showerror(
                            "Error",
                            "No se pudo recuperar la clave privada."
                        )
                    )

        # Ejecuta en un hilo separado
        threading.Thread(target=task, daemon=True).start()

    def load_plain_pre_count_data(self, progress_window, info_label, progress_bar, percentage_label):
        try:
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
            accept_pre_count_container.grid(row=self.accept_pre_count_container_row, column=0, pady=10, padx=500)
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
            messagebox.showerror("Error al descifrar el preconteo:", f":{e}\n{traceback.format_exc()}")

            progress_window.after(0, progress_window.destroy)

    def pre_count_accepted(self):
        messagebox.showinfo("", "Conteo finalizado.")
        self.accept_pre_count_button.destroy()
        self.deny_pre_count_button.destroy()
        self.accept_pre_count_label.config(text='Conteo finalizado.')


    def create_decrypt_tab_and_load_plain_votes_data(self, progress_window, info_label, progress_bar, percentage_label):
        try:
            self.accept_pre_count_button.destroy()
            self.deny_pre_count_button.destroy()
            self.accept_pre_count_label.config(text='Conteo finalizado.')
            # Se crea el tab de descifrado
            self.decrypt_frame = tk.Frame(self.notebook, bg="#F0F0F0")
            self.notebook.add(self.decrypt_frame, text="Descifrado", state='normal')
            self.decrypt_frame.grid_columnconfigure(0, weight=1)

            row_df = self.generate_counter()
            # =========================================================================================================
            self.info_decrypt_frame_label = tk.Label(
                self.decrypt_frame,
                font=self.title_font,
                text="En esta pestaña se muestran los votos descifrados, puede contar los votos manualmente para "
                     "verificar el preconteo.",
            )
            self.info_decrypt_frame_label.grid(row=next(row_df), column=0, sticky="ew")

            # =========================================================================================================
            self.info_count_table_label = tk.Label(
                self.decrypt_frame,
                font=self.title_font,
                text="Tabla de conteo"
            )
            self.info_count_table_label.grid(row=next(row_df), column=0, pady=self.default_pady)

            # Tabla de conteo
            # Contenedor para centrar los widgets
            self.count_container = tk.Frame(self.decrypt_frame, bg="#F0F0F0")

            self.count_container.grid_columnconfigure(0, weight=1, uniform="0")
            self.count_container.grid_columnconfigure(1, weight=1, uniform="0")

            self.count_container.grid(row=next(row_df), column=0, columnspan=1, padx=30, sticky="nsew")

            self.candidate_name_header_label = tk.Label(
                self.count_container,
                font=self.title_font,
                text="Candidato",
                relief="groove"
            )
            self.candidate_name_header_label.grid(row=0, column=0, sticky="ew")

            self.candidate_count_header_label = tk.Label(
                self.count_container,
                font=self.title_font,
                text="Votos a favor",
                relief="groove"
            )
            self.candidate_count_header_label.grid(row=0, column=1, sticky="ew")

            for i, candidate in enumerate(self.pre_count):
                candidate_name = candidate[0]
                self.counter_of_votes_in_favor_dict[f"{candidate_name}"] = int(0)
                name_lbl = self.create_label(self.count_container, bg="white", text=f"{candidate_name}", font=self.subtitle_font)
                name_lbl.grid(row=i+1, column=0, sticky="ew")

                count_lbl = self.create_label(
                    self.count_container,
                    bg="white",
                    text=self.counter_of_votes_in_favor_dict[f"{candidate_name}"],
                    font=self.subtitle_font
                )

                self.count_of_votes_in_favor_label.append([f"{candidate_name}", name_lbl, count_lbl])
                idx = len(self.count_of_votes_in_favor_label)
                self.count_of_votes_in_favor_label[idx-1][2].grid(row=i+1, column=1, sticky="ew")

            self.info_plain_votes_table_label = tk.Label(
                self.decrypt_frame,
                font=self.title_font,
                text="Tabla de votos descifrados",
            )
            self.info_plain_votes_table_label.grid(row=next(row_df), column=0, pady=self.default_pady)

            self.plain_votes_table = self.create_table(
                frame=self.decrypt_frame,
                row=next(row_df),
                column=0,
                columnspan=3,
                columns=("ID", "Candidate"),
                headings=("ID (creado para el despliegue de votos)", "Candidato seleccionado"),
                column_widths=(100, 200),
                column_min_widths = (100, 200),
                stretch_configs= (True, True),
                table_height=0
            )

            self.notebook.tab(3, state='normal')
            self.notebook.select(3)
            total_votes = len(self.votes)

            row_id = None
            # Limpia los datos cargados anteriormente
            for row in self.plain_votes_table.get_children():
                self.plain_votes_table.delete(row)

            for idx, vote in enumerate(self.votes):
                dict_vote = Exp.b64_to_dictionary(vote)
                vote_available_to_be_decrypted = (dict_vote['alpha'], dict_vote['betha'])

                dec = Decryptor(self.secret["P"], self.secret["G"], self.secret["PrK"])
                int_plain_vote = dec.decipher_std(vote_available_to_be_decrypted)
                plain_vote = Exp.int_to_string(int_plain_vote)

                if self.dynamic_plain_votes_table_height < 15:
                    self.dynamic_plain_votes_table_height += 1
                    self.plain_votes_table.configure(height=self.dynamic_plain_votes_table_height)
                    self._root.update_idletasks()
                row_id = self.plain_votes_table.insert("", "end", values=((idx+1), plain_vote))
                self.plain_votes_table.selection_set(row_id)
                self.plain_votes_table.see(row_id)

                # Se suma el contador del candidato votado
                self.counter_of_votes_in_favor_dict[f"{plain_vote}"] += 1

                for i, _list in enumerate(self.count_of_votes_in_favor_label):
                    # Si el candidato de la lista es igual al candidato del voto
                    if _list[0] == plain_vote:
                        # Resalta el candidato votado en esta iteracion
                        _list[1].config(font=self.title_font)
                        # Configura el label de esa lista con el valor de su contador de votos a favor
                        _list[2].config(
                            text=f"{self.counter_of_votes_in_favor_dict[f"{plain_vote}"]}",
                            font=self.title_font
                        )
                        # Actualiza la interfaz
                        self._root.update_idletasks()
                        # Espera un segundo
                        time.sleep(400/1000)
                        # Deja de resaltar la fila del candidato votado
                        _list[1].config(font=self.subtitle_font)
                        _list[2].config(font=self.subtitle_font)
                        # Espera 100ms para dejar que se aprecie como vuelve a su estado original
                        # (por si el candidato tiene votos seguidos)
                        time.sleep(100/1000)
                        # Como ya encontro el label indicado, break
                        break

                progress = (idx + 1) * 100 / total_votes
                progress_window.after(0, self.update_progress, progress_bar, percentage_label, progress)

                if (idx + 1) == total_votes:
                    self.plain_votes_table.selection_remove(row_id)
                    just_one_winner, number, winner = self.get_winner()
                    if just_one_winner:
                        winner_label = tk.Label(
                            self.decrypt_frame,
                            text=f"Ganó {winner} con {number} votos a favor.",
                            font=self.winner_font
                        )
                        winner_label.grid(row=next(row_df), column=0, pady=self.default_pady)
                    else:
                        empate_label = tk.Label(
                            self.decrypt_frame,
                            text=f"Empate entre {len(winner)} candidatos.",
                            font=self.winner_font
                        )
                        empate_label.grid(row=next(row_df), column=0, pady=self.default_pady)

                        empate_label = tk.Label(
                            self.decrypt_frame,
                            text=f"No hay mayoría de votos para un solo candidato:",
                            font=self.title_font
                        )
                        empate_label.grid(row=next(row_df), column=0)

                        for i in winner:
                            lbl = self.create_label(
                                self.decrypt_frame,
                                bg="#F0F0F0",
                                text=f"{i} obtuvo {number} votos a favor.",
                                font=self.title_font
                            )
                            lbl.grid(row=next(row_df), column=0)
            messagebox.showinfo("", "Descifrado de votos finalizado.")

        except Exception as e:
            messagebox.showerror("Error al descifrar los votos", f": {e} in line {traceback.format_exc()}")
            progress_window.after(0, progress_window.destroy)

    def create_label(self, parent, bg, text, font):
        new_label = tk.Label(
            parent,
            bg=bg,
            text=text,
            font=font
        )
        return new_label

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
        krc = KRC(my_list)

        if self.req_shares is None:
            self.req_shares = krc.get_required_shares(krc)

        else:
            if self.req_shares != my_share["Rs"]:
                messagebox.showwarning("Fragmento incompatible",
                                       "El fragmento importado no es compatible con el anterior.")
                return

        if len(self.shares_paths) >= self.req_shares:
            self.widget_containers["prk_hash_container"]["button"].configure(state="normal")
        share_number = my_share["x"]

        for row in self.share_name_id_table.get_children():
            self.share_name_id_table.delete(row)

        for share_name in self.shares_paths:
            row_id = self.share_name_id_table.insert("", "end", values=(share_name, share_number))
            self.share_name_id_table.selection_set(row_id)
            self.share_name_id_table.see(row_id)

        self.numbers_shares["rs"].configure(text=self.req_shares)
        self.numbers_shares["ts"].configure(text=self.shares_paths[i][-5])
        self.numbers_shares["is"].configure(text=len(self.shares_paths))

    def create_progress_window(self, target_function, win_title="Cargando", win_width=500, win_height=100,
                               info_label=""):
        # Ventana emergente de progreso
        progress_window = tk.Toplevel(self._root)
        progress_window.title(win_title)
        pos_x = int((self.screen_width - win_width) / 2)
        pos_y = int((self.screen_height - win_height) / 2)
        progress_window.geometry(f"{win_width}x{win_height}+{pos_x}+{pos_y}")
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

        # Acción al cerrar la ventana: detener el hilo
        progress_window.protocol("WM_DELETE_WINDOW", lambda: self.cancel_thread(load_thread))

        # Limpia el evento por si se activó anteriormente
        self.stop_event.clear()
        # Se lanza la tarea en un hilo independiente
        load_thread.start()

    def cancel_thread(self, thread):
        # Detener el hilo mediante la señal
        self.stop_event.set()

    def try_except_launcher(self, target_function, progress_window, info_label, progress_bar, percentage_label):
        try:
            target_function(progress_window, info_label, progress_bar, percentage_label)
        except Exception as e:
            print(e)
        finally:
            progress_window.after(0, progress_window.destroy)

    def ajustar_labels(self, event):
        nuevo_ancho = event.width - 20  # Ancho ajustado según el tamaño de la ventana
        for widget in self.pre_count_frame.winfo_children():
            # Verificar si el widget es un Label
            if isinstance(widget, tk.Label):
                widget.config(wraplength=nuevo_ancho)

    def get_winner(self):
        winner = []
        greater_count = 0

        for candidate in self.counter_of_votes_in_favor_dict:
            if self.counter_of_votes_in_favor_dict[f"{candidate}"] > greater_count:
                greater_count = self.counter_of_votes_in_favor_dict[f"{candidate}"]
                winner.clear()
                winner.append(candidate)
            elif self.counter_of_votes_in_favor_dict[f"{candidate}"] == greater_count:
                winner.append(candidate)
        if len(winner) == 1:
            return True, greater_count, winner[0]
        else:
            return False, greater_count, winner

    def get_empty_space(self, parent, bg):
        empty_space = tk.Label(parent, bg=bg)
        return empty_space

    def verify_hash(self, key):
        # Se crea el diccionario con comillas simples porque así se guarda en el módulo de generación de claves
        key_formated = {'P':int(key["P"]), 'G':int(key["G"]), 'PrK':int(key["PrK"])}
        key_resume_hex = hashlib.sha3_256(str(key_formated).encode('utf-8')).hexdigest()
        resume_reference_dict = Exp.import_key(self.prk_hash_path)
        if key_resume_hex == resume_reference_dict["digesto"]:
            return True
        else:
            return False

    def verify_stop_event(self):
        if self.stop_event.is_set():
            return True
        else:
            return False

    def set_default_shares_table(self):
        for row in self.share_name_id_table.get_children():
            self.share_name_id_table.delete(row)
        for k in self.numbers_shares:
            self.numbers_shares[k].configure(text="")
        self.req_shares = None
        self.shares_paths.clear()
        self.shares.clear()
        self.reconstruct_button.configure(state='disabled')
        self.prk_hash_path = None
        self.widget_containers["prk_hash_container"]["button"].configure(state="disabled")
        self.widget_containers["prk_hash_container"]["file_path_label"].configure(
            text=self.prk_hash_request_default,
            fg="red"
        )

    def do_mix(self):
        puk_encrption = Exp.import_key(self.puk_cipher_path)

        if isinstance(puk_encrption, str):
            puk_encrption = ast.literal_eval(puk_encrption)

        for i in range(3):
            for row in self.mix_table[i].get_children():
                self.mix_table[i].delete(row)

        self.widget_containers["puk_cipher_container"]["button"].configure(state="disabled")

        self._root.update_idletasks()
        if self.votes is not None:
            votes_before_mixed = []
            for vote in self.votes:
                votes_before_mixed.append(vote[1])
            for i, vote in enumerate(votes_before_mixed):
                # Convertimos la lista de votos a un formato compatible para el recifrado
                dict_vote = Exp.b64_to_dictionary(vote)
                vote_available_to_be_reciphered = (dict_vote['alpha'], dict_vote['betha'])
                votes_before_mixed[i] = vote_available_to_be_reciphered

            for i in range(3):
                # Se obtienen los votos mezclados
                mixer = FMN(puk_encrption["P"], puk_encrption["G"], puk_encrption["PuK"])
                mixed_votes = mixer.permute(votes_before_mixed.copy())

                for idx in range(len(mixed_votes)):
                    if random.getrandbits(1) == 1: # Si el bit aleatorio es 1 pide prueba de mezclado
                        print(f"Verificando voto {idx} de la mezcla {i+1}.")
                        # Pregunta por los factores usados para obtener el voto idx de la lista de votos mezclados
                        factors = mixer.challenge(mixed_votes[idx][0])
                        permutation_fac = factors[0]
                        re_encryption_fact = factors[1]
                        input_vote = votes_before_mixed[permutation_fac]
                        output_vote = mixed_votes[idx]
                        # Comprueba si el recifrado del voto no mezclado en la posicion del factor de permutacion
                        #       genera el voto recibido
                        is_mix_valid = self.do_mix_proof(puk_encrption, input_vote, re_encryption_fact, output_vote)
                        if not is_mix_valid:
                            self.mixed_votes_not_approved_by_verifier.append({"idx": idx, "mix": i})
                            print(f"Falló la prueba de mezclado para el voto {idx} de la mezcla número {i + 1}")

                for j, vote in enumerate(mixed_votes):
                    vote = Exp.dictionary_to_b64(vote)
                    row_id = self.mix_table[i].insert("", "end", values=(vote,))
                    self.mix_table[i].selection_set(row_id)  # Selecciona la fila
                    self.mix_table[i].see(row_id)  # Se desplaza para mostrarla
                    self._root.update_idletasks()
                    self.mix_table[i].selection_remove(row_id)
                votes_before_mixed = mixed_votes

            self.votes.clear()
            for vote in votes_before_mixed:
                ctext_j = {"alpha": vote[0], "betha": vote[1]}
                self.votes.append(Exp.dictionary_to_b64(ctext_j))

            self.goto_pre_count_button.configure(state="normal")
            self.notebook.tab(2, state="normal")
            if len(self.mixed_votes_not_approved_by_verifier) == 0:
                messagebox.showinfo("Mezcla exitosa", "Todas las mezclas verificadas fueron aprobadas.")

            else:
                votos_mal_mezclados = "\n".join(map(str, self.mixed_votes_not_approved_by_verifier))
                messagebox.showwarning("Advertencia", "La prueba de mezclado fue inválida para los votos:\n"
                                                      f"{votos_mal_mezclados}")

    @staticmethod
    def do_mix_proof(puk_encrption, input_vote, k, output_vote):
        mixer_verifier = FMN(puk_encrption["P"], puk_encrption["G"], puk_encrption["PuK"])
        result, k = mixer_verifier.recipher(input_vote, k)
        if result == output_vote:
            #print("Prueba aprobada.")
            return True
        else:
            print("Prueba reprobada.")
            return False

if __name__ == "__main__":
    #root es la ventana
    root = tk.Tk()
    app = Interface(root)
    root.mainloop()