from Tkinter import Tk, Label, Button

class gui:

    def __init__(self,master):
        from numpy import array
        self.master = master
        master.title("Simple GUI")
        labelgrid = ["red" for i in range(30*30)]
        self.labelgrid = array(labelgrid).reshape(30,30)
        self.build_widgets()

    def build_widgets(self):
        from numpy import shape
        n = 0
        for i in range(shape(self.labelgrid)[0]):
            for j in range(shape(self.labelgrid)[1]):
                self.label = Label(self.master, bg=self.labelgrid[i,j], text="%03d"%(n))
                self.label.grid(row=i, column=j)
                n += 1

        self.buttonRun = Button(self.master, text="run", command=self.clicked)
        self.buttonRun.grid(row=31,column=31)

        self.buttonReset = Button(self.master, text="reset", commend=self.build_widgets)
        self.buttonReset.grid(row=32,column=31)

    def clicked(self):
        from time import time, sleep
        from numpy import random
        x = []
        for i in range(30):
            for j in range(30):
                x.append([i,j])
        random.shuffle(x)
        starttime = time()
        n = len(x) - 1
        while n > -1:
            if (time() - starttime)%10 < 1:
                print x[n]
                self.label = Label(self.master, bg="green", text="999")
                self.label.grid(row=x[n][0], column=x[n][1])
                n -= 1

def main():
    root = Tk()
    app = gui(root)
    root.mainloop()

if __name__ == "__main__":
  main()
