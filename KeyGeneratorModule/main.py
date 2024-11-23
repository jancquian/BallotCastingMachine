import EncryptionKeyGenerator as Ekg
import BlindSignatureGenerator as Bsg
import KeySplitterComponent as Ksc
import Exporter as Exp
import Interface as Ifc
import tkinter as tk
import sys


if __name__ == '__main__':

    sys.set_int_max_str_digits(1000000)
    Exp.Exporter.make_dir("Cifrar")
    Exp.Exporter.make_dir("Descifrar")
    Exp.Exporter.make_dir("Firma")
    Exp.Exporter.make_dir("Verificacion")
    Exp.Exporter.make_dir("Configuracion")
       
    root = tk.Tk()

    elgamal = Ekg.EncryptionKeyGenerator()
    exporter = Exp.Exporter()
    shamir = Ksc.KeySplitterComponent()
    chaum = Bsg.BlindSignatureGenerator()
    Ifc.Interface(root, elgamal, chaum, shamir, exporter)
    root.mainloop()
