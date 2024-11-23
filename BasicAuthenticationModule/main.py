import tkinter as tk
import Exporter as Exp
import Interface as Ifc
import BookWorm as Bwm
import sys
if __name__ == '__main__':
    Exp.Exporter.make_dir("Sesión")
    worm = Bwm.BookWorm("./Sesión")
    sys.set_int_max_str_digits(1000000)
    exp = Exp.Exporter()
    root = tk.Tk()
    Ifc.Interface(root, exp, worm)
    root.mainloop()