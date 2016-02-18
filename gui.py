from Tkinter import Tk, Label, Button

class gui:

    def __init__(self,master):
        self.master = master
        master.title("Simple GUI")
        self.build_widgets()

    def build_widgets(self):
        self.label1 = Label(self.master, bg="red", text="1/100")
        self.label1.grid(row=0, column=0)

        self.label2 = Label(self.master, bg="red", text="2/100")
        self.label2.grid(row=0, column=1)

        self.label3 = Label(self.master, bg="red", text="3/100")
        self.label3.grid(row=0, column=2)

        self.button = Button(self.master, text="run", command=self.clicked)
        self.button.grid(row=1,column=1)

    def clicked(self):
        self.label2.configure(bg="green")

def main():
    root = Tk()
    app = gui(root)
    root.mainloop()

if __name__ == "__main__":
  main()
