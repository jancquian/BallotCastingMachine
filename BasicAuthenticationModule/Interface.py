import tkinter as tk
from tkinter import filedialog


class FormatError(Exception):
    pass

class Interface:
    def __init__(self, root, exp, worm):
        # Atributos de la interfaz.
        self._root = root
        self._worm = worm
        self._exp = exp
        self._frame_collection = dict()
        self._flag_label_cll = dict()
        self._total_tickets = None
        self._current_ticket = None

        # Configuración general de la interfaz.
        self._root.title("MÓDULO BÁSICO DE AUTENTICACIÓN")
        self._root.geometry("465x150")
        self._root.resizable(False, False)

        try:
            if int(self._worm.get_total_register_number()) - int(self._worm.get_total_register_available_number()) != 0:
                self.launch_ticket_distrution_frame()
        except:
            print("No hay sesión anterior")

            # Parametrización de textos.
            titles = ("Ubuntu Sans Mono Regular", 12, "bold")
            sub_titles = ("Ubuntu Sans Mono Regular", 11)
            small_titles = ("Ubuntu Sans Mono Regular", 8)
            button_font_bold = ("Ubuntu Sans Mono Regular", 12, "bold")

            # Se genera el frame de la primera pantalla(configuración).
            self._frame_collection["settings"] = tk.Frame(self._root, bg='#F0F0F0', bd=0, relief=tk.RAISED)
            self._frame_collection["settings"].place(x=0, y=0, width=800, height=480)

            set_mcm_label = tk.Label(self._frame_collection["settings"], text="Carga de archivos:", font=titles)
            set_mcm_label.place(x=5, y=5)

            con_fle_path = tk.StringVar(value="")
            con_fle_label = tk.Label(self._frame_collection["settings"], text="Archivo de Configuración:", font=sub_titles)
            con_fle_label.place(x=15, y=50)
            con_fle_ent = tk.Entry(self._frame_collection["settings"], textvariable=con_fle_path,
                                   state="readonly", width=19, font=sub_titles)
            con_fle_ent.place(x=200, y=50)
            self._flag_label_cll["con_fle"] = tk.Label(self._frame_collection["settings"], text="ERROR", font=sub_titles)

            pth_sel = tk.Button(self._frame_collection["settings"], text="...",
                                font=small_titles,
                                command=lambda: self.sel_pem(con_fle_path))
            pth_sel.place(x=360, y=48)

            start_button = tk.Button(self._frame_collection["settings"], text="COMENZAR",
                                   command=lambda: self.check_file(con_fle_path),
                                   width=10, height=1, font=button_font_bold, relief=tk.RAISED)
            start_button.place(x=170, y=100)

    def check_file(self, file_path):
        try:
            data = self._exp.import_key(file_path.get())
            if "auth" in data:
                tickets = data["auth"]
                if len(tickets) == 750 or len(tickets) == 1000:
                    self._flag_label_cll["con_fle"].place_forget()
                    self._worm.start_up_ticket_vault()
                    self._worm.clean_up_ticket_vault()
                    for ticket in tickets:
                        self._worm.regist_ticket(ticket)
                    self.launch_ticket_distrution_frame()
                else:
                    self._flag_label_cll["con_fle"].place(x=397, y=50)
                    raise FormatError("Archivo de configuración no compatible (número de votos no aceptado)")
            else:
                self._flag_label_cll["con_fle"].place(x=397, y=50)
                raise FormatError("Archivo de configuración no compatible")
        except Exception as e:
            self._flag_label_cll["con_fle"].place(x=397, y=50)
            print(e)

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

    def launch_ticket_distrution_frame(self):
        try:
            self._frame_collection["settings"].place_forget()
        except:
            print("Se encontró sesión activa")
        self._frame_collection["ticket_dist"] = tk.Frame(self._root, bg='#F0F0F0', bd=0, relief=tk.RAISED)
        self._frame_collection["ticket_dist"].place(x=0, y=0, width=800, height=480)
        ticket_label_info = tk.Label(self._frame_collection["ticket_dist"],
                                     text="Ticket de acceso:", font=("Ubuntu Sans Mono Regular", 12, "bold"))
        ticket_label_info.place(x=5, y=5)

        self._total_tickets = self._worm.get_total_register_number()
        self._flag_label_cll["total_tickets"] = tk.Label(self._frame_collection["ticket_dist"],
                                                         text=f'Tickets totales: {str(self._total_tickets)}',
                                                         font=("Ubuntu Sans Mono Regular", 10, "bold"))
        self._flag_label_cll["total_tickets"].place(x=320, y=5)

        current_ticket_code =  str(self._worm.get_last_ticket())
        print(current_ticket_code)
        if current_ticket_code == "NONE":
            current_ticket_code = self._worm.get_ticket()
            self._worm.regist_last_ticket(current_ticket_code)

        self._current_ticket = int(self._total_tickets) - int(self._worm.get_total_register_available_number())
        self._flag_label_cll["current_ticket"] = tk.Label(self._frame_collection["ticket_dist"],
                                                         text=f'Ticket actual: {str(self._current_ticket)}',
                                                         font=("Ubuntu Sans Mono Regular", 10, "bold"))
        self._flag_label_cll["current_ticket"].place(x=320, y=25)

        self._flag_label_cll["ticket"] = tk.Label(self._frame_collection["ticket_dist"],
                                     text=current_ticket_code, font=("Ubuntu Sans Mono Regular", 18, "bold"))
        self._flag_label_cll["ticket"].place(x=190, y=50)

        start_button = tk.Button(self._frame_collection["ticket_dist"], text="SIGUIENTE TICKET",
                               command=self.request_next_ticket,
                               width=15, height=1, font=("Ubuntu Sans Mono Regular", 12, "bold"), relief=tk.RAISED)
        start_button.place(x=160, y=100)

    def request_next_ticket(self):
        self._current_ticket = self._current_ticket + 1
        self._flag_label_cll["current_ticket"].config(text=f'Ticket actual: {str(self._current_ticket)}')
        next_ticket = str(self._worm.get_ticket())
        self._worm.update_last_ticket(self._flag_label_cll["ticket"].cget("text"), next_ticket)
        self._flag_label_cll["ticket"].config(text=next_ticket)
        print(next_ticket)
        if str(next_ticket) == "NONE":
            self._worm.seal_vault()
            self._root.destroy()
