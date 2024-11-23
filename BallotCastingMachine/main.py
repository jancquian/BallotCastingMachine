import tkinter as tk
import Exporter as Exp
import Interface as Ifc
import BookWorm as Bwm
import TicketBookWorm as Tbw
import sys
if __name__ == '__main__':
    sys.set_int_max_str_digits(1000000)
    Exp.Exporter.make_dir("./Resultados")
    Exp.Exporter.make_dir("./Sesión")
    worm = Bwm.BookWorm("./Resultados")
    ticket_worm = Tbw.TicketBookWorm("./Sesión")
    root = tk.Tk()
    exp = Exp.Exporter()
    Ifc.Interface(root, exp, worm, ticket_worm)
    root.mainloop()