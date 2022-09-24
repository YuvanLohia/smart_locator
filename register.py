import tkinter as tk
from flask_bcrypt import Bcrypt
from app import db,User
from tkinter.messagebox import askyesno

def reg():
    password = passw_var.get()
    password = Bcrypt().generate_password_hash(password)
    user = User(username=name_var.get(),password=password)
    db.session.add(user)
    db.session.commit()
    askyesno(title="Conformation",message="User Created")
root = tk.Tk()
name_var=tk.StringVar()
passw_var=tk.StringVar()
tk.Label(root,text="Username").grid(row=0,column=0)
i1 = tk.Entry(root,textvariable=name_var)
i1.grid(row=0,column=1)
tk.Label(root,text="Password").grid(row=1,column=0)
i2 = tk.Entry(root,textvariable=passw_var)
i2.grid(row=1,column=1)
b = tk.Button(root,text="Register",command = reg)
b.grid(row=3,column=0)
root.mainloop()