import hidpi_tk as tk

from gui import App

if __name__ == "__main__":
    root = tk.DPIAwareTk()
    app = App(root)
    root.mainloop()
