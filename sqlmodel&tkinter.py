from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, create_engine, Session, select
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import os

### Eski veritabanı dosyasını sil
##if os.path.exists("database.db"):
##    os.remove("database.db")

# Model Sınıfları
class Base(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    create_date: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))
    update_date: datetime | None = Field(default=None)
    delete_date: datetime | None = Field(default=None)
    isactive: bool = Field(default=True)

class Child(Base, table=True):
    name: str
    surname: str
    mailaddress: str
    age: int

# Veritabanı Bağlantısı
engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)

# CRUD İşlemleri
def add_child(session: Session, child: Child):
    session.add(child)
    session.commit()
    session.refresh(child)
    return child

def get_child(session: Session, child_id: int):
    statement = select(Child).where(Child.id == child_id)
    result = session.exec(statement).one_or_none()
    return result

def update_child(session: Session, child_id: int, **kwargs):
    child = get_child(session, child_id)
    if child:
        for key, value in kwargs.items():
            setattr(child, key, value)
        child.update_date = datetime.now(timezone.utc)
        session.add(child)
        session.commit()
        session.refresh(child)
    return child

def toggle_active(session: Session, child_id: int):
    child = get_child(session, child_id)
    if child:
        child.isactive = not child.isactive
        child.delete_date = datetime.now(timezone.utc) if not child.isactive else None
        session.add(child)
        session.commit()
        session.refresh(child)
    return child

def query_children(session: Session):
    statement = select(Child)
    return session.exec(statement).all()

# Tkinter Arayüzü
def clear_entries():
    id_var.set("")
    name_var.set("")
    surname_var.set("")
    mail_var.set("")
    age_var.set("")

def submit():
    with Session(engine) as session:
        child = Child(
            name=name_var.get(),
            surname=surname_var.get(),
            mailaddress=mail_var.get(),
            age=int(age_var.get())
        )
        add_child(session, child)
        messagebox.showinfo("Başarı", "Veri eklendi")
        clear_entries()
        query()  # Listeyi güncelle

def delete():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Uyarı", "Lütfen silmek için bir kayıt seçin")
        return
    child_id = tree.item(selected_item)["values"][0]
    with Session(engine) as session:
        toggle_active(session, child_id)
        messagebox.showinfo("Başarı", "Veri durumu güncellendi")
        clear_entries()
        query()  # Listeyi güncelle

def update():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Uyarı", "Lütfen güncellemek için bir kayıt seçin")
        return
    child_id = tree.item(selected_item)["values"][0]
    with Session(engine) as session:
        kwargs = {
            "name": name_var.get(),
            "surname": surname_var.get(),
            "mailaddress": mail_var.get(),
            "age": int(age_var.get())
        }
        update_child(session, child_id, **kwargs)
        messagebox.showinfo("Başarı", "Veri güncellendi")
        clear_entries()
        query()  # Listeyi güncelle

def query():
    with Session(engine) as session:
        children = query_children(session)
        for row in tree.get_children():
            tree.delete(row)
        for child in children:
            status = "Aktif" if child.isactive else "Pasif"
            tree.insert("", "end", values=(child.id, child.name, child.surname, child.mailaddress, child.age, child.create_date, child.update_date, child.delete_date, status))

def on_tree_select(event):
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        values = item["values"]
        id_var.set(values[0])
        name_var.set(values[1])
        surname_var.set(values[2])
        mail_var.set(values[3])
        age_var.set(values[4])
        for row in tree.get_children():
            tree.item(row, tags=())
        tree.item(selected_item, tags=("selected",))
        tree.tag_configure("selected", background="yellow")

def on_operation_change(event):
    selected_operation = operation_var.get()
    if selected_operation == "Ekle":
        set_button_states(True, False, False)
    elif selected_operation == "Güncelle":
        set_button_states(False, True, False)
        query()  # Listeyi güncelle
    elif selected_operation == "Sil":
        set_button_states(False, False, True)
        query()  # Listeyi güncelle
    elif selected_operation == "Listele":
        set_button_states(False, False, False)
        query()  # Listeyi güncelle
    clear_entries()

def set_button_states(add_state, update_state, delete_state):
    add_button.config(state=tk.NORMAL if add_state else tk.DISABLED)
    update_button.config(state=tk.NORMAL if update_state else tk.DISABLED)
    delete_button.config(state=tk.NORMAL if delete_state else tk.DISABLED)

root = tk.Tk()
root.title("Veri Girişi")

# Giriş Alanları
tk.Label(root, text="ID:").grid(row=0, column=0)
tk.Label(root, text="Ad:").grid(row=1, column=0)
tk.Label(root, text="Soyad:").grid(row=2, column=0)
tk.Label(root, text="E-posta:").grid(row=3, column=0)
tk.Label(root, text="Yaş:").grid(row=4, column=0)

id_var = tk.StringVar()
name_var = tk.StringVar()
surname_var = tk.StringVar()
mail_var = tk.StringVar()
age_var = tk.StringVar()

tk.Entry(root, textvariable=id_var).grid(row=0, column=1)
tk.Entry(root, textvariable=name_var).grid(row=1, column=1)
tk.Entry(root, textvariable=surname_var).grid(row=2, column=1)
tk.Entry(root, textvariable=mail_var).grid(row=3, column=1)
tk.Entry(root, textvariable=age_var).grid(row=4, column=1)

# İşlem Seçim Menüsü
operation_var = tk.StringVar(value="İşlem Seç")
operations = ["Ekle", "Güncelle", "Sil", "Listele"]
operation_menu = ttk.Combobox(root, textvariable=operation_var, values=operations, state="readonly")
operation_menu.grid(row=5, column=0)
operation_menu.bind("<<ComboboxSelected>>", on_operation_change)

# Butonlar
add_button = tk.Button(root, text="Kaydet", command=submit, state=tk.DISABLED)
add_button.grid(row=5, column=1)
update_button = tk.Button(root, text="Güncelle", command=update, state=tk.DISABLED)
update_button.grid(row=5, column=2)
delete_button = tk.Button(root, text="Durum Güncelle", command=delete, state=tk.DISABLED)
delete_button.grid(row=5, column=3)

# Treeview
columns = ("ID", "Ad", "Soyad", "E-posta", "Yaş", "Create Date", "Update Date", "Delete Date", "Durum")
tree = ttk.Treeview(root, columns=columns, show="headings")
tree.grid(row=6, column=0, columnspan=4)

# Başlıkları koyu yapmak
for col in columns:
    tree.heading(col, text=col)

# Kolon genişlikleri
tree.column("ID", width=50)
tree.column("Ad", width=100)
tree.column("Soyad", width=100)
tree.column("E-posta", width=150)
tree.column("Yaş", width=50)
tree.column("Create Date", width=150)
tree.column("Update Date", width=150)
tree.column("Delete Date", width=150)
tree.column("Durum", width=80)

# Çizgiler için stil ayarı
style = ttk.Style()
style.configure("Treeview", rowheight=25)
style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))

# Treeview seçim işlemi
tree.bind("<<TreeviewSelect>>", on_tree_select)

root.mainloop()
