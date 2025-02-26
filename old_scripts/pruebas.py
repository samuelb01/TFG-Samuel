import tkinter as tk
import tkinter.ttk as ttk
root = tk.Tk()
root.geometry("400x400")
ventana = ttk.Notebook(root)
tab_01 = tk.Frame(ventana)
tab_02 = tk.Frame(ventana)
ventana.add(tab_01, text="Tab 01")
ventana.add(tab_02, text="Tab 02")

ventana.grid()

label_01 = tk.Label(tab_01, text="Hola Mundo")
label_01.grid()

root.mainloop()