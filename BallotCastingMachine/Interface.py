import tkinter as tk
import Encryptor as Ecr
import Voter as Vtr
import BlindSignatory as Bsg
import io
import os
import shutil
import ast
from tkinter import filedialog
from source import DEF_IMAGE
from PIL import Image, ImageTk


class FormatKeyError(Exception):
    pass

class Interface:
    def __init__(self, root, exp, worm, ticket_worm):
        # Atributos de la interfaz.
        self._root = root
        self._root.protocol("WM_DELETE_WINDOW", self.abort)
        self._ecr = None
        self._vtr = None
        self._sgr = None
        self._exp = exp
        self._worm = worm
        self._tworm = ticket_worm
        self._frame_collection = dict()
        self._candidates = dict()
        self._widget_collection = dict()
        self._flag_label_cll = dict()
        self._ticket = tk.StringVar(value="")

        # Atributos para el voto
        self._precount = dict()
        self._worm.start_up_vault()
        self._tworm.start_up_ticket_vault()

        # Parametrización de textos.
        titles = ("Ubuntu Sans Mono Regular", 22, "bold")
        sub_titles = ("Ubuntu Sans Mono Regular", 20)
        small_title = ("Ubuntu Sans Mono Regular", 10)
        small_title_bold = ("Ubuntu Sans Mono Regular", 10, "bold")
        button_font = ("Ubuntu Sans Mono Regular", 18)
        button_font_bold = ("Ubuntu Sans Mono Regular", 18, "bold")

        # Configuración general de la interfaz.
        self._root.title("URNA DE VOTACIÓN ELECTRÓNICA")
        # self._root.overrideredirect(True)
        self._root.geometry("800x480")
        self._root.resizable(False, False)

        # Se genera el frame de la primera pantalla(configuración).
        self._frame_collection["settings"] = tk.Frame(self._root, bg='#F0F0F0', bd=0, relief=tk.RAISED)
        self._frame_collection["settings"] .place(x=0, y=0, width=800, height=480)

        set_bcm_label = tk.Label(self._frame_collection["settings"], text="Configuración de Urna:", font=titles)
        set_bcm_label.place(x=5, y=5)

        enc_puk_path = tk.StringVar(value="")
        enc_puk_label = tk.Label(self._frame_collection["settings"], text="Llave de Cifrado:", font=sub_titles)
        enc_puk_label.place(x=15, y=73)
        enc_puk_label_inf = tk.Label(self._frame_collection["settings"],
                                     text="(Llave de pública del esquema de cifrado ElGamal)", font=small_title)
        enc_puk_label_inf.place(x=15, y=113)
        enc_puk_ent = tk.Entry(self._frame_collection["settings"], textvariable=enc_puk_path,
                               state="readonly", width=27, font=sub_titles)
        enc_puk_ent.place(x=226, y=73)
        self._flag_label_cll["enc_puk"] = tk.Label(self._frame_collection["settings"], text="ERROR", font=sub_titles)


        sig_puk_path = tk.StringVar(value="")
        sig_puk_label = tk.Label(self._frame_collection["settings"], text="Llave de Verificación:", font=sub_titles)
        sig_puk_label.place(x=15, y=133)
        sig_puk_label_inf = tk.Label(self._frame_collection["settings"],
                                     text="(Llave de pública del esquema de firma a ciegas de Chaum)", font=small_title)
        sig_puk_label_inf.place(x=15, y=173)
        sig_puk_ent = tk.Entry(self._frame_collection["settings"], textvariable=sig_puk_path,
                               state="readonly", width=23, font=sub_titles)
        sig_puk_ent.place(x=285, y=133)
        self._flag_label_cll["sig_puk"] = tk.Label(self._frame_collection["settings"], text="ERROR", font=sub_titles)
        # self._flag_label_cll["sig_puk"].place(x=400, y=63)

        sig_prk_path = tk.StringVar(value="")
        sig_prk_label = tk.Label(self._frame_collection["settings"], text="Llave de Firma:", font=sub_titles)
        sig_prk_label.place(x=15, y=193)
        sig_prk_label_inf = tk.Label(self._frame_collection["settings"],
                                     text="(Llave de privada del esquema de firma a ciegas de Chaum)", font=small_title)
        sig_prk_label_inf.place(x=15, y=233)
        sig_prk_ent = tk.Entry(self._frame_collection["settings"], textvariable=sig_prk_path,
                               state="readonly", width=28, font=sub_titles)
        sig_prk_ent.place(x=211, y=193)
        self._flag_label_cll["sig_prk"] = tk.Label(self._frame_collection["settings"], text="ERROR", font=sub_titles)

        con_fle_path = tk.StringVar(value="")
        con_fle_label = tk.Label(self._frame_collection["settings"], text="Archivo de Configuración:", font=sub_titles)
        con_fle_label.place(x=15, y=253)
        con_fle_label_inf = tk.Label(self._frame_collection["settings"],
                                     text="(Archivo que contiene los candidatos de la elección)", font=small_title)
        con_fle_label_inf.place(x=15, y=293)
        con_fle_ent = tk.Entry(self._frame_collection["settings"], textvariable=con_fle_path,
                               state="readonly", width=19, font=sub_titles)
        con_fle_ent.place(x=347, y=253)
        self._flag_label_cll["con_fle"] = tk.Label(self._frame_collection["settings"], text="ERROR", font=sub_titles)

        warning_a = tk.Label(self._frame_collection["settings"],
                             text="*No extraiga los dispositivos USB hasta que comience la elección.",
                             font=small_title_bold,
                             fg="red")
        warning_a.place(x=15, y=323)

        warning_b = tk.Label(self._frame_collection["settings"],
                             text="**La elección no podrá comenzar si se encuentra algun error en los archivos proporcionados.",
                             font=small_title_bold,
                             fg="red")
        warning_b.place(x=15, y=343)

        paths = [enc_puk_path, sig_puk_path, sig_prk_path, con_fle_path]

        coy = 73
        for path in paths:
            pth_sel = tk.Button(self._frame_collection["settings"], text="...",
                                font=button_font,
                                command=lambda p=path: self.sel_pem(p))
            pth_sel.place(x=642, y=coy)
            coy = coy + 60

        start_button = tk.Button(self._frame_collection["settings"], text="COMENZAR\nVOTACIÓN",
                               command=lambda: self.check_files(paths),
                               width=10, height=2, font=button_font_bold, relief=tk.RAISED)
        start_button.place(x=400, y=380)

        full_s_button = tk.Button(self._frame_collection["settings"], text="PANTALLA\nCOMPLETA",
                               command=self.full_size_on,
                               width=10, height=2, font=button_font_bold, relief=tk.RAISED)
        full_s_button.place(x=200, y=380)

        self.full_size_on()
        self._root.bind("<Escape>", self.full_size_off)

    @staticmethod
    def select_dir():
        return filedialog.askdirectory()

    @staticmethod
    def find_pem():
        return filedialog.askopenfilename(title="Selecciona el archivo PEM",
                                          filetypes=[("Archivo PEM", "*.pem")])

    @staticmethod
    def sel_pem(var):
        aux_path = var.get()
        path = Interface.find_pem()
        var.set(path)
        if var.get() == "":
            var.set(aux_path)

    def check_files(self, files):

        aux_key = None

        try:
            data = self._exp.import_key(files[0].get())
            if not isinstance(data['P'], int):
                raise FormatKeyError("El primo no es entero")
            if not isinstance(data['G'], int):
                raise FormatKeyError("El generador no es entero")
            if not isinstance(data['PuK'], int):
                raise FormatKeyError("El parametro público no es entero")
            self._ecr = Ecr.Encryptor(data['P'], data['G'], data['PuK'])
            enc_puk_flag = True
            self._flag_label_cll["enc_puk"].place_forget()
        except Exception as e:
            print(e)
            self._flag_label_cll["enc_puk"].place(x=695, y=73)
            enc_puk_flag = False

        try:
            data = self._exp.import_key(files[1].get())
            if not isinstance(data['Puk'], int):
                raise FormatKeyError("El parametro público (Puk) no es entero")
            if not isinstance(data['N'], int):
                raise FormatKeyError("El primo (N) no es entero")
            self._vtr = Vtr.Voter(data)
            sig_puk_flag = True
            aux_key = data
            self._flag_label_cll["sig_puk"].place_forget()
        except Exception as e:
            print(e)
            self._flag_label_cll["sig_puk"].place(x=695, y=133)
            sig_puk_flag = False

        try:
            data = self._exp.import_key(files[2].get())
            if not isinstance(data['Prk'], int):
                raise FormatKeyError("El parametro privado (Prk) no es entero")
            if not isinstance(data['N'], int):
                raise FormatKeyError("El primo (N) no es entero")
            if aux_key is None:
                 raise FormatKeyError("Llave pública faltante (Verificación)")
            self._sgr = Bsg.BlindSignatory(data)
            sig_prk_flag = True
            self._flag_label_cll["sig_prk"].place_forget()
        except Exception as e:
            print(e)
            self._flag_label_cll["sig_prk"].place(x=695, y=193)
            sig_prk_flag = False

        self._candidates = dict()
        session = self._tworm.check_session()
        try:

            if not enc_puk_flag:
                raise FormatKeyError("No se cargó la llave de cifrado")

            data = self._exp.import_key(files[3].get())
            if not 1 < len(data) < 8:
                raise FormatKeyError("Archivo de configuración no compatible (número de candidatos no permitido)")
            if "auth" in data:
                tickets = data["auth"]
                if len(tickets) == 750 or len(tickets) == 1000:
                    if session:
                        self._tworm.clean_up_ticket_vault()
                        for ticket in tickets:
                            self._tworm.regist_ticket(ticket)
                    data.pop("auth")
                else:
                    self._flag_label_cll["con_fle"].place(x=397, y=50)
                    raise FormatKeyError("Archivo de configuración no compatible (número de votos no aceptado)")
            else:
                self._flag_label_cll["con_fle"].place(x=397, y=50)
                raise FormatKeyError("Archivo de configuración no compatible")
            for candidate in data:
                if not isinstance(data[candidate], list):
                    raise FormatKeyError("Archivo de configuración no compatible (error en formato)")
                if len(data[candidate]) != 3:
                    raise FormatKeyError("Archivo de configuración no compatible (error en candidato)")
                # aux_list = list()
                try:
                    aux_list = [data[candidate][0], data[candidate][1]]
                    # Condición invertida, si no hay sesión entra al if.
                    if session:
                        self._precount[str(data[candidate][0]) + " - " + str(data[candidate][1])] = self._ecr.cipher(0)
                        self.set_precount(str(data[candidate][0]) + " - " + str(data[candidate][1]))
                    else:
                        pecount = self._worm.get_precount(str(data[candidate][0]) + " - " + str(data[candidate][1]))
                        # precount es una lista que contiene una dupla que contiene el str del texto cifrado y un elemeto vácio [('(alpha, betha)',)]
                        self._precount[str(data[candidate][0]) + " - " + str(data[candidate][1])] = ast.literal_eval(pecount[0][0])
                    img = self._exp.json_to_bytes(data[candidate][2])
                    img = self._exp.b64_to_bytes(img)
                    img = Image.open(io.BytesIO(img))
                    img = img.resize((80, 100), Image.DEFAULT_STRATEGY)
                    aux_list.append(ImageTk.PhotoImage(img))
                    self._candidates[candidate] = aux_list
                except Exception as e:
                    print(e)
                    aux_list = [data[candidate][0], data[candidate][1]]
                    img = self._exp.json_to_bytes(DEF_IMAGE)
                    img = self._exp.b64_to_bytes(img)
                    img = Image.open(io.BytesIO(img))
                    img = img.resize((80, 100), Image.DEFAULT_STRATEGY)
                    aux_list.append(ImageTk.PhotoImage(img))
                    self._candidates[candidate] = aux_list
            con_flag = True

            self._flag_label_cll["con_fle"].place_forget()
        except Exception as e:
            print(e)
            self._flag_label_cll["con_fle"].place(x=695, y=253)
            self._candidates = dict()
            con_flag = False

        if enc_puk_flag and sig_puk_flag and sig_prk_flag and con_flag:
            self._frame_collection["settings_verification"] = tk.Frame(self._root, bg='#F0F0F0', bd=0, relief=tk.RAISED)
            self._frame_collection["settings_verification"].place(x=0, y=0, width=800, height=480)

            verification_lbl = tk.Label(self._frame_collection["settings_verification"],
                                        text="Listado de candidatos:",
                                        font=("Ubuntu Sans Mono Regular", 22, "bold"))
            verification_lbl.place(x=5, y=5)

            if len(self._candidates) < 6:
                aux = self._candidates['5']
                self._candidates.pop('5')
                self._candidates[str(len(self._candidates))] = aux

            coy = 60
            for candidate in self._candidates:
                img_label = tk.Label(self._frame_collection["settings_verification"],
                                     image=str(self._candidates[candidate][2]))
                name_label = tk.Label(self._frame_collection["settings_verification"],
                                      text=str(self._candidates[candidate][1]),
                                      font=("Ubuntu Sans Mono Regular", 18, "bold"))
                code_label = tk.Label(self._frame_collection["settings_verification"],
                                      text=str(self._candidates[candidate][0]),
                                      font=("Ubuntu Sans Mono Regular", 18, "bold"))

                if int(candidate) % 2 == 0:
                    img_label.place(x=25, y=coy)
                    name_label.place(x=115, y=coy)
                    code_label.place(x=115, y=coy + 43)
                else:
                    img_label.place(x=405, y=coy)
                    name_label.place(x=495, y=coy)
                    code_label.place(x=495, y=coy + 43)
                    coy = coy + 120

            decline_ver = tk.Button(self._frame_collection["settings_verification"],
                                    text="Rechazar",
                                    font=("Ubuntu Sans Mono Regular", 18, "bold"),
                                    width=12,
                                    command=self._frame_collection["settings_verification"].destroy)
            decline_ver.place(x=100, y=420)

            accept_ver = tk.Button(self._frame_collection["settings_verification"],
                                   text="Aceptar",
                                   font=("Ubuntu Sans Mono Regular", 18, "bold"),
                                   width=12,
                                   command=self.start_elections)
            accept_ver.place(x=500, y=420)

    def create_request_code(self):
        self._frame_collection["request"] = tk.Frame(self._root, bg='#F0F0F0',
                                                     bd=0, relief=tk.RAISED, width=800, height=480)

        set_req_code_label = tk.Label(self._frame_collection["request"],
                                 text="Ingrese su ticket de autorización:",
                                 font=("Ubuntu Sans Mono Regular", 22, "bold"))
        set_req_code_label.place(x=5, y=5)

        ticket_ent = tk.Entry(self._frame_collection["request"], textvariable=self._ticket,
                               state="readonly", width=19, font=("Ubuntu Sans Mono Regular", 22, "bold"))
        ticket_ent.place(x=232, y=100)

        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        count = 0
        cox = 30
        coy = 200
        for letter in letters:
            kb_button = tk.Button(self._frame_collection["request"], text=letter, font=("Ubuntu Sans Mono Regular", 18),
                                  width=4, command=lambda l=letter: self.add_letter(l))
            kb_button.place(x=cox, y=coy)
            cox += 94
            count += 1
            if count == 8:
                coy += 50
                cox = 30
                count = 0

        delete_button = tk.Button(self._frame_collection["request"], text="<--", font=("Ubuntu Sans Mono Regular", 18),
                                  command=self.rmv_letter, width=4)
        delete_button.place(x=218, y=350)

        delete_button = tk.Button(self._frame_collection["request"], text="limpiar",
                                  command=self.clean_ticket, font=("Ubuntu Sans Mono Regular", 18), width=4)
        delete_button.place(x=312, y=350)

        acept_button = tk.Button(self._frame_collection["request"], text="ACEPTAR",
                               command=self.verify_ticket_code,
                               width=10, height=1, font=("Ubuntu Sans Mono Regular", 18, "bold"), relief=tk.RAISED)
        acept_button.place(x=320, y=410)

        end_elections_button = tk.Button(self._frame_collection["request"],
                                         text="Finalizar elección",
                                         font=("Ubuntu Sans Mono Regular", 14, "bold"),
                                         command=self.finish_election)

        self._frame_collection["request"].bind('<Key-a>',lambda event : end_elections_button.place(x=550, y=5))
        self._frame_collection["request"].bind('<Key-b>',lambda event : end_elections_button.place_forget())

    def add_letter(self, letter):
        aux_ticket = self._ticket.get()
        aux_ticket = aux_ticket + letter
        if len(aux_ticket) < 7:
            self._ticket.set(aux_ticket)

    def rmv_letter(self):
        aux_ticket = self._ticket.get()[:-1]
        self._ticket.set(aux_ticket)

    def clean_ticket(self):
        self._ticket.set("")

    def trigger_code_request(self):
        self._frame_collection["request"].place(x=0, y=0)
        self._frame_collection["request"].focus_set()

    def hidde_code_request(self):
        self._frame_collection["request"].place_forget()


    def create_elections(self):
        # self._frame_collection["settings_verification"].destroy()
        self._frame_collection["elections"] = tk.Frame(self._root, bg='#F0F0F0',
                                                       bd=0, relief=tk.RAISED, width=800, height=480)
        # self._frame_collection["elections"].place(x=0, y=0, width=800, height=480)
        # self._frame_collection["elections"].focus_set()

        set_bcm_label = tk.Label(self._frame_collection["elections"],
                                 text="Seleccione su candidato de preferencia:",
                                 font=("Ubuntu Sans Mono Regular", 22, "bold"))
        set_bcm_label.place(x=5, y=5)

        coy = 60
        for candidate in self._candidates:
            img_label = tk.Label(self._frame_collection["elections"],
                                 image=str(self._candidates[candidate][2]))
            name_label = tk.Label(self._frame_collection["elections"],
                                  text=str(self._candidates[candidate][1]),
                                  font=("Ubuntu Sans Mono Regular", 18, "bold"))
            code_label = tk.Label(self._frame_collection["elections"],
                                  text=str(self._candidates[candidate][0]),
                                  font=("Ubuntu Sans Mono Regular", 18, "bold"))
            selection_button = tk.Button(self._frame_collection["elections"],
                                  text="Votar",
                                  font=("Ubuntu Sans Mono Regular", 14, "bold"),
                                  command= lambda c=self._candidates[candidate]: self.verify_vote(c))

            if int(candidate) % 2 == 0:
                img_label.place(x=25, y=coy)
                name_label.place(x=115, y=coy)
                code_label.place(x=115, y=coy + 43)
                selection_button.place(x=195, y=coy + 43)
            else:
                img_label.place(x=405, y=coy)
                name_label.place(x=495, y=coy)
                code_label.place(x=495, y=coy + 43)
                selection_button.place(x=575, y=coy + 43)
                coy = coy + 120

    def trigger_election_screen(self):
        self._frame_collection["elections"].place(x=0, y=0)
        self._frame_collection["elections"].focus_set()

    def hidde_election_screen(self):
        self._frame_collection["elections"].place_forget()

    def verify_ticket_code(self):
        code = self._ticket.get()
        if self._tworm.check_ticket(code):
            self._tworm.update_status(code)
            self.hidde_code_request()
            self.trigger_election_screen()

    def start_elections(self):
        self._frame_collection["settings_verification"].destroy()
        self.create_elections()
        self.create_request_code()
        self.trigger_code_request()

    def finish_election(self):
        try:
            file_pem_path = self.find_pem()
            data = self._exp.import_key(file_pem_path)
            if self._sgr.authorize(data):
                path = self.select_dir()
                if path:
                    # Se trasforman los registros del preconteo a base 64
                    for precount in self._worm.get_recount_registers():
                        # print(precount[1])
                        ctext = ast.literal_eval(precount[1])
                        # print(ctext)
                        ctext_j = {"alpha":ctext[0], "betha":ctext[1]}
                        sign_j = {"sign": int(precount[2])}
                        self._worm.update_results(precount[0],
                                                  self._exp.dictionary_to_b64(ctext_j),
                                                  self._exp.dictionary_to_b64(sign_j))
                    # Se genra el archivo de firma de la bóveda
                    vault_data_hex = self._exp.get_hex_of_file("./Resultados/vault.db")
                    vault_sign = {"sign": self.sign(vault_data_hex)}
                    self._exp.export_key(vault_sign, path, "vault_sign")
                    shutil.move("./Resultados/vault.db", path)
                    os.remove("./Sesión/session.db")
                    self._tworm.seal_vault()
                    self._worm.seal_vault()
                    self._root.destroy()
        except Exception as e:
            print(f'Error al intentar extraer bóveda {e}')

    def verify_vote(self, candidate):
        self._frame_collection["verify_vote"] = tk.Frame(self._root, bg='#F0F0F0', bd=0, relief=tk.RAISED)
        self._frame_collection["verify_vote"].place(x=0, y=0, width=800, height=480)
        self._frame_collection["verify_vote"].focus_set()

        verify_label = tk.Label(self._frame_collection["verify_vote"],
                                 text="Confirme su voto:",
                                 font=("Ubuntu Sans Mono Regular", 22, "bold"))
        verify_label.place(x=5, y=5)

        message_label = tk.Label(self._frame_collection["verify_vote"],
                                 text="Usted va a votar por el siguiente candidato:",
                                 font=("Ubuntu Sans Mono Regular", 12, "bold"))
        message_label.place(x=220, y=150)

        img_label = tk.Label(self._frame_collection["verify_vote"], image=str(candidate[2]))
        name_label = tk.Label(self._frame_collection["verify_vote"], text=str(candidate[1]),
                              font=("Ubuntu Sans Mono Regular", 18, "bold"))
        code_label = tk.Label(self._frame_collection["verify_vote"],
                              text=str(candidate[0]),
                              font=("Ubuntu Sans Mono Regular", 18, "bold"))

        img_label.place(x=250, y=180)
        name_label.place(x=340, y=180)
        code_label.place(x=340, y=220)

        decline_ver = tk.Button(self._frame_collection["verify_vote"],
                                text="Rechazar",
                                font=("Ubuntu Sans Mono Regular", 18, "bold"),
                                width=12,
                                command=self.deny_vote)
        decline_ver.place(x=100, y=420)

        accept_ver = tk.Button(self._frame_collection["verify_vote"],
                               text="Aceptar",
                               font=("Ubuntu Sans Mono Regular", 18, "bold"),
                               width=12,
                               command=lambda : self.accept_vote(candidate))
        accept_ver.place(x=500, y=420)

    def sign(self, message):
        hidden_message = self._vtr.hide(str(message))
        blind_signature = self._sgr.sign(hidden_message)
        signature = self._vtr.find(blind_signature)
        return signature

    def set_precount(self, candidate):
        # se cifra 0 con el formato g0 = 1
        start_up_value = self._ecr.cipher(0)
        sign_sup_value = self.sign(start_up_value)
        self._worm.regist_results(candidate, str(start_up_value), str(sign_sup_value))

    def precount(self, candidate):
        dict_key = str(candidate[0]) + ' - ' + str(candidate[1])
        # Se hace la multiplicacion homomórfica g0 * g1 = g(0+1)
        self._precount[dict_key] = self._ecr.homomorphic_product(self._precount[dict_key], self._ecr.cipher(1))
        precount_sign = self.sign(self._precount[dict_key])
        try:
            self._worm.update_results(dict_key, str(self._precount[dict_key]), str(precount_sign))
            print("PRECONTEO ACTUALIZADO")
        except Exception as e:
            print(e)
            self._worm.regist_results(dict_key, str(self._precount[dict_key]), str(precount_sign))
            print("PRECONTEO NO ACTUALIZADO")

    def seal_vote(self, candidate):
        message = str(candidate[0]) + ' - ' + str(candidate[1])
        message = self._exp.string_to_int(message)
        ciphertxt = self._ecr.cipher_std(message)
        ciphertxt_sign = self.sign(str(ciphertxt))
        j_ciphertext = {"alpha": ciphertxt[0], "betha": ciphertxt[1]}
        j_sign = {"sign": ciphertxt_sign}
        self._worm.regist_vote(self._exp.dictionary_to_b64(j_ciphertext), self._exp.dictionary_to_b64(j_sign))

    def proccess_vote(self, candidate):
        self.precount(candidate)
        self.seal_vote(candidate)

    def accept_vote(self, candidate):
        pop = tk.Toplevel()
        pop.focus_set()
        pop.title("Gracias")
        pop.geometry("380x170")
        pop.resizable(False, False)
        pop.protocol("WM_DELETE_WINDOW", self.ignore_close_request)
        pop.grab_set()
        frame =  tk.Frame(pop, width=380, height=170)
        frame.place(x=0, y=0)
        message = tk.Label(frame, text="Gracias por votar... :)",
                           font=("Ubuntu Sans Mono Regular", 12, "bold"))
        message.place(relx=0.5, rely=0.5, anchor="center")

        def on_close():
            pop.destroy()  # Destruye el pop-up
            self.deny_vote() # Luego llama a deny_vote(), para borrar la pantalla de confirmación del candidato seleccionado
            self.hidde_election_screen()
            self.clean_ticket()
            self.trigger_code_request()
            self.proccess_vote(candidate)  # Procesa el voto

        pop.after(5000, on_close)

    def deny_vote(self):
        self._frame_collection["verify_vote"].destroy()
        self._frame_collection["elections"].focus_set()

    def full_size_on(self):
        self._root.attributes('-fullscreen', True)

    def full_size_off(self, event):
        self._root.attributes('-fullscreen', False)

    @staticmethod
    def ignore_close_request():
        print("Cerrado ignorado")

    def abort(self):
        try:
            self._tworm.seal_vault()
            self._worm.seal_vault()
        except Exception as e:
            print(e)
        self._root.destroy()
