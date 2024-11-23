import threading
import random
import string
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from source import DEF_IMAGE

class Interface:
    def __init__(self, root, ekg, bsg, ksc, exp):
        # Atributos de la interfaz.
        self._root = root
        self._ekg = ekg
        self._bsg = bsg
        self._ksc = ksc
        self._exp = exp
        self._widget_collection = dict()

        # Configuración general de la interfaz.
        self._root.title("MÓDULO GENERADOR DE LLAVES Y CONFIGURACIÓN")
        self._root.geometry("465x407")
        self._root.resizable(False, False)

        # Parametrizacion de textos.
        titles = ("Ubuntu Sans Mono Regular", 12, "bold")
        sub_titles = ("Ubuntu Sans Mono Regular", 11)
        mini_titles = ("Ubuntu Sans Mono Regular", 9)

        # Creación del Notebook.
        self.notebook = ttk.Notebook(self._root, width=452, height=370)

        #----PÁGINA DE GENERACIÓN DE LLAVES----

        # Creación del frame para la generación de llaves.
        f_kg = tk.Frame(self.notebook, bg="#F0F0F0", bd=0, relief=tk.RAISED)
        f_kg.place(x=0, y=0, width=452, height=370)

        # SECCIÓN DE TAMAÑO DE LLAVE
        # Generación de label para tamaño de llave y declaración de su variable
        key_size_label = tk.Label(f_kg, text="Tamaño de llave (seguridad):", font=titles)
        key_size_label.place(x=5, y=5)

        key_size = tk.IntVar(value=2048)

        # Generación de RadioButton para seleccionar el tamaño de llave
        cox = 5
        coy = 35
        for option in [("2048 bits (éstandar)", 2048), ("3072 bits (alta)", 3072)]:
            rb = tk.Radiobutton(f_kg, text=option[0], variable=key_size, value=option[1], font=sub_titles)
            rb.bind('<Motion>', lambda e: bool(key_size.get()))
            rb.place(x=cox, y=coy)
            cox = cox + 175

        # SECCIÓN DE FRAGMENTACIÓN DE LLAVE PRIVADA ELGAMAL MEDIANTE S.C. CHAUM
        # Generación de label para la fragmentación de llave
        ekg_sec_spt_opt = tk.Label(f_kg, text="Fragmentar llave de descifrado:", font=titles)
        ekg_sec_spt_opt.place(x=5, y=65)

        # Generación de label y combobox para configurar los fragmentos creados.
        self._widget_collection["spt_dst_lbl"] = tk.Label(f_kg, text="No. de fragmentos generados:",
                                                          font=sub_titles)
        self._widget_collection["spt_dst_lbl"].place(x=15, y=95)

        self._widget_collection["spt_dst_shr"] = ttk.Combobox(f_kg,
                                                              values=[str(i) for i in range(3, 6)],
                                                              state='readonly', width=14, height=2)
        self._widget_collection["spt_dst_shr"].set(3)
        self._widget_collection["spt_dst_shr"].place(x=235, y=95)

        # Generación de label y combobox para configurar los fragmentos necesarios para reconstruir el secreto.
        self._widget_collection["spt_req_lbl"] = tk.Label(f_kg, text="No.de fragmentos necesarios:",
                                                          font=sub_titles)
        self._widget_collection["spt_req_lbl"].place(x=15, y=123)

        self._widget_collection["spt_req_shr"] = ttk.Combobox(f_kg, values=['2', '3'],
                                                              state='readonly', width=14)
        self._widget_collection["spt_req_shr"].set(2)
        self._widget_collection["spt_req_shr"].place(x=235, y=123)

        # El combobox de los fragmentos generados detecta el cambio para actualizar el número de...
        # fragmentos necesarios para reconstruir el secrerto, de tal manera que este nunca es superior...
        # al número de fragmentos generados
        self._widget_collection["spt_dst_shr"].bind("<<ComboboxSelected>>", self.update_spt_shr)

        # SECCIÓN PARA CONFIGURAR LOS DIRECTORIOS DE SALIDA PARA LAS LLAVES.
        # Se genera el label de la sección.
        path_sec_label = tk.Label(f_kg, text="Directorios de salida:", font=titles)
        path_sec_label.place(x=5, y=151)

        # Se generan los labels relativos a las distintas llaves.
        cox = 15
        coy = 180
        for option in ["Fragmentos llave de descifrado:", "Llave de cifrado:", "Llave de firma:", "Llave de comprobación de firma:"]:
            pth_lbl = tk.Label(f_kg, text=option,
                               font=sub_titles)
            pth_lbl.place(x=cox, y=coy)
            coy = coy + 28


        # Se declaran las variales para almacenar las rutas; por defecto se guardan en la ruta creada por el prototipo
        prk_ekg_path = tk.StringVar(value="./Descifrar")
        puk_ekg_path = tk.StringVar(value="./Cifrar")
        prk_bsg_path = tk.StringVar(value="./Firma")
        puk_bsg_path = tk.StringVar(value="./Verificacion")

        # Se agrupan las variables en una lista
        paths = [prk_ekg_path, puk_ekg_path, prk_bsg_path, puk_bsg_path]

        # Se generan los entry para cada una de las llaves, se asocia a cada una su correspondiente variable de ruta
        prk_ekg_ent = tk.Entry(f_kg, textvariable=prk_ekg_path, state="readonly", width=21)
        prk_ekg_ent.place(x=235, y=180)

        puk_ekg_ent = tk.Entry(f_kg, textvariable=puk_ekg_path, state="readonly", width=33)
        puk_ekg_ent.place(x=139, y=208)

        prk_bsg_ent = tk.Entry(f_kg, textvariable=prk_bsg_path, state="readonly", width=35)
        prk_bsg_ent.place(x=123, y=236)

        puk_bsg_ent = tk.Entry(f_kg, textvariable=puk_bsg_path, state="readonly", width=19)
        puk_bsg_ent.place(x=251, y=264)

        # Se generan los botones para configurar las rutas de salida; se usa la lista "paths" como parametro.
        coy = 180
        for path in paths:
            pth_sel = tk.Button(f_kg, text="...", font=("Ubuntu Sans Mono Regular", 6),
                                command=lambda p=path: self.sel_path(p))
            pth_sel.place(x=411, y=coy)
            coy = coy + 28

        # Se genera el botton para generar las llaves.
        kg_button = tk.Button(f_kg, text="GENERAR",
                               command=lambda: self.start_key_gen(key_size.get(), *[pth.get() for pth in paths]),
                               width=10, height=1, font=("Ubuntu Sans Mono Regular", 9, "bold"), relief=tk.RAISED)
        kg_button.place(x=178, y=310)

        # Se agrega la página al Notebook.
        self.notebook.add(f_kg, text="Generación de llaves")

        # ----PÁGINA DE GENERACIÓN DE ARCHIVO DE CONFIGURACIÓN DE LA URNA----

        # Creación del frame para la configuración de la urna.
        f_con = tk.Frame(self.notebook, bg='#F0F0F0', bd=0, relief=tk.RAISED)
        f_con.place(x=0, y=0, width=420, height=300)

        # Generación del label para la configuración general de la urna.
        grl_con_lbl = tk.Label(f_con, text="Configuración general:",
                           font=titles)
        grl_con_lbl.place(x=5, y=5)

        # Generación del label de número de candidatos.
        con_candidate_number_label = tk.Label(f_con, text="No. candidatos:", font=mini_titles)
        con_candidate_number_label.place(x=10, y=37)

        self._widget_collection["can_num"] = ttk.Combobox(f_con, values=[str(i) for i in range(2, 6)],
                                                              state='readonly', width=2)
        self._widget_collection["can_num"].set(2)
        self._widget_collection["can_num"].place(x=102, y=36)

        con_voter_number_label = tk.Label(f_con, text="No. electores:", font=mini_titles)
        con_voter_number_label.place(x=137, y=37)

        self._widget_collection["vot_num"] = ttk.Combobox(f_con, values=["750", "1000"],
                                                              state='readonly', width=4)
        self._widget_collection["vot_num"].set(750)
        self._widget_collection["vot_num"].place(x=220, y=36)

        con_path_label = tk.Label(f_con, text="Dir.:", font=mini_titles)
        con_path_label.place(x=272, y=38)

        con_path = tk.StringVar(value="./Configuracion")

        con_path_ent = tk.Entry(f_con, textvariable=con_path, state="readonly", width=13)
        con_path_ent.place(x=299, y=36)

        con_pth_sel = tk.Button(f_con, text="...", font=("Ubuntu Sans Mono Regular", 6),
                            command= lambda: self.sel_path(con_path))
        con_pth_sel.place(x=411, y=36)


        con_candidate = tk.Label(f_con, text="Configuración de candidatos:", font=titles)
        con_candidate.place(x=5, y=63)

        self._widget_collection["can_number"] = dict()
        self._widget_collection["can_name"] = dict()
        self._widget_collection["can_code"] = dict()
        self._widget_collection["can_image"] = dict()
        self._widget_collection["can_image_bt"] = dict()

        aux_s ="#\tid\t\t\t\tnombre\t\t\t\t           foto              "
        data_label = tk.Label(f_con, text=aux_s, font=("Ubuntu Sans Mono Regular", 7))
        data_label.place(x=15, y=92)

        unique_codes = set()
        while len(unique_codes) < 5:
            code = ''.join(random.choices(string.ascii_uppercase, k=4))
            if code != "NONE":
                unique_codes.add(code)
        unique_codes = list(unique_codes)

        photo_path = [tk.StringVar(value="Sin foto"),
                      tk.StringVar(value="Sin foto"),
                      tk.StringVar(value="Sin foto"),
                      tk.StringVar(value="Sin foto"),
                      tk.StringVar(value="Sin foto")]

        coy = 110
        for can_num in range(0, 5):

            number = str(can_num)

            self._widget_collection["can_number"][number] = tk.Label(f_con, text=f"{int(number) + 1}:", font=sub_titles)
            self._widget_collection["can_code"][number] = tk.Label(f_con, width=7,
                                                                   font=sub_titles, text=unique_codes[can_num])
            self._widget_collection["can_name"][number] = tk.Entry(f_con, width=33, font=sub_titles)
            self._widget_collection["can_image"][number]=tk.Label(f_con, textvariable=photo_path[can_num],
                                                                  font=("Ubuntu Sans Mono Regular", 6))
            self._widget_collection["can_image_bt"][number] = tk.Button(f_con, text="Agregar foto",
                                                                        font=("Ubuntu Sans Mono Regular", 6),
                                                                        command=lambda p=photo_path[can_num]: self.sel_photo(p))
            self._widget_collection["can_number"][number].place(x=15, y=coy)
            self._widget_collection["can_code"][number].place(x=32, y=coy)
            self._widget_collection["can_name"][number].place(x=95, y=coy)
            self._widget_collection["can_image"][number].place(x=32, y=coy+26)
            self._widget_collection["can_image_bt"][number].place(x=370, y=coy)

            coy = coy + 43

        self._widget_collection["can_num"].bind("<<ComboboxSelected>>", self.update_candidates)
        self.update_candidates(self._widget_collection["can_num"].get())


        kg_button = tk.Button(f_con, text="GENERAR",
                               command=lambda: self.start_con_gen(con_path.get()),
                               width=10, height=1, font=("Ubuntu Sans Mono Regular", 9, "bold"), relief=tk.RAISED)
        kg_button.place(x=178, y=330)

        self.notebook.add(f_con, text="Configuración de urna")


        self.notebook.place(x=5, y=5)

    @staticmethod
    def disable_widget(widget):
        try:
            widget.config(state='disabled')
        except tk.TclError:
            widget.config(state='readonly')

    @staticmethod
    def enable_widget(widget):
        try:
            widget.config(state='active')
        except tk.TclError:
            widget.config(state='normal')

    def update_spt_shr(self, event):
        dis_shares = int(self._widget_collection["spt_dst_shr"].get()) + 1
        self._widget_collection["spt_req_shr"].set(dis_shares - 1)
        self._widget_collection["spt_req_shr"].config(values=[str(i) for i in range(2, dis_shares)])

    @staticmethod
    def select_dir():
        return filedialog.askdirectory()

    @staticmethod
    def find_photo():
        return filedialog.askopenfilename(title="Selecciona una imagen",
                                          filetypes=[("Imágenes JPG", "*.jpg *.jpeg")])

    @staticmethod
    def sel_path(var):
        aux_path = var.get()
        path = Interface.select_dir()
        var.set(path)
        if var.get() == "":
            var.set(aux_path)

    @staticmethod
    def sel_photo(var):
        aux_path = var.get()
        path = Interface.find_photo()
        var.set(path)
        if var.get() == "":
            var.set(aux_path)

    def ignore_close_request(self):
        pass

    def pop_hold_on(self, mili_seconds):
        self._root.protocol("WM_DELETE_WINDOW", self.ignore_close_request)
        pop = tk.Toplevel()
        pop.title("ESPERA")
        pop.geometry("380x170")
        pop.resizable(False, False)
        pop.protocol("WM_DELETE_WINDOW", self.ignore_close_request)
        pop.grab_set()
        frame =  tk.Frame(pop, width=380, height=170)
        frame.place(x=0, y=0)
        message = tk.Label(frame, text="Espere un momento...",
                           font=("Ubuntu Sans Mono Regular", 12, "bold"))
        message.place(relx=0.5, rely=0.5, anchor="center")
        pop.after(mili_seconds, pop.destroy)
        self._root.after(mili_seconds, self.set_up_abort)

    def generate_keys(self, key_size, prk_ekg_path, puk_ekg_path, prk_bsg_path, puk_bsg_path):
        # creación de llaves de ElGamal
        self._ekg.set_key_size(key_size)
        self._ekg.create_key_pair()
        puk = self._ekg.get_public_key()
        prk = self._ekg.get_private_key()
        # Se fragmenta la llave privada de ElGamal mediante el esquema de secreto compartido de Shamir
        total_shares = int(self._widget_collection["spt_dst_shr"].get())
        required_shares = int(self._widget_collection["spt_req_shr"].get())
        self._ksc.set_required_shares(required_shares)
        self._ksc.set_distribiuted_shares(total_shares)
        shares = self._ksc.split_secret(self._exp.dictionary_to_json(prk))
        for share in shares:
            # Se obtiene los pem de los fragmentos de la llave privada de ElGamal
            self._exp.export_key(share, prk_ekg_path, "EkgPrkElGamal{0}Of{1}".format(share['x'], total_shares))

        # Se obtiene el pem de la llave pública de ElGamal
        self._exp.export_key(puk, puk_ekg_path, "EkgPukElGamal")

        # Se generan el par de llaves del esquema de Chaum
        self._bsg.set_security_parameter(key_size*2)
        self._bsg.generate_keys()
        puk_s = self._bsg.get_public_key()
        prk_s = self._bsg.get_private_key()

        # Se obtienen los pem de las llaves de Chaum
        self._exp.export_key(puk_s, puk_bsg_path, "BsgPukChaum")
        self._exp.export_key(prk_s, prk_bsg_path, "BsgPrkChaum")

    def start_key_gen(self, key_size, prk_ekg_path, puk_ekg_path, prk_bsg_path, puk_bsg_path):
        threading.Thread(target=self.generate_keys,
                         args=(key_size, prk_ekg_path, puk_ekg_path, prk_bsg_path, puk_bsg_path)).start()
        self.pop_hold_on(10000)

    def update_candidates(self, event):
        candidate_number = int(self._widget_collection["can_num"].get())
        for index in range(0, candidate_number):
            number = str(index)
            Interface.enable_widget(self._widget_collection["can_number"][number])
            Interface.enable_widget(self._widget_collection["can_code"][number])
            Interface.enable_widget(self._widget_collection["can_name"][number])
            Interface.enable_widget(self._widget_collection["can_image"][number])
            Interface.enable_widget(self._widget_collection["can_image_bt"][number])

        for index in range(candidate_number, 5):
            number = str(index)
            Interface.disable_widget(self._widget_collection["can_number"][number])
            Interface.disable_widget(self._widget_collection["can_code"][number])
            Interface.disable_widget(self._widget_collection["can_name"][number])
            Interface.disable_widget(self._widget_collection["can_image"][number])
            Interface.disable_widget(self._widget_collection["can_image_bt"][number])

    def generate_config(self, path):
        candidate_number = int(self._widget_collection["can_num"].get())
        candiate_dict = dict()

        for index in range(0, candidate_number):
            aux_list = list()
            number = str(index)
            aux_list.append(self._widget_collection["can_code"][number].cget("text"))
            aux_list.append(self._widget_collection["can_name"][number].get())
            image = self._widget_collection["can_image"][number].cget("text")
            if image != "Sin foto":
                with open(image, "rb") as img:
                    bytes_imagen = self._exp.bytes_to_b64(img.read())
                    data_s = self._exp.bytes_to_json(bytes_imagen)
                    aux_list.append(data_s)
            else:
                aux_list.append(DEF_IMAGE)
            candiate_dict[number] = aux_list

        candiate_dict['5'] = ["NONE", "VOTO NULO", DEF_IMAGE]

        voter_code = set()
        while len(voter_code) < int(self._widget_collection["vot_num"].get()):
            code = ''.join(random.choices(string.ascii_uppercase, k=6))
            if code != "NONE":
                voter_code.add(code)
        voter_code = list(voter_code)

        candiate_dict['auth'] = voter_code

        self._exp.export_key(candiate_dict, path, "Configuracion")

    def start_con_gen(self, path):
        threading.Thread(target=self.generate_config, args=(path,)).start()
        self.pop_hold_on(5000)

    def abort(self):
        self._root.destroy()

    def set_up_abort(self):
        self._root.protocol("WM_DELETE_WINDOW", self.abort)
