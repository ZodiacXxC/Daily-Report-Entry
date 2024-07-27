# -*- coding: utf-8 -*-
from tkinter import INSERT, ttk, END, messagebox
import tkinter as tk
import time
from datetime import datetime
import sql 
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer

pdfmetrics.registerFont(TTFont('Arabic', 'Arial.ttf'))
styles = getSampleStyleSheet()
styleN = styles['Normal']
arabic_text_style = ParagraphStyle(
    'ArabicStyle',
    parent=styleN, 
    fontName='Arabic',
    fontSize=12,
    leading=14,
    borderPadding=2,
)



curr_date = datetime.now().strftime("%Y-%m-%d")

initial_data = sql.getNotes()
all_date = ['All']
for row in sql.getDate():
    all_date.append(row[0])


def create_pdf(dataframe, filename):
    selection = filter_date.get()
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    title = f"Report for {selection} Date"
    title_x = width / 2
    title_y = height - 50  
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(title_x, title_y, title)
    
    data = [dataframe.columns.to_list()] + dataframe.values.tolist()
    col_widths = [50, 300, 100, 100]
    table = Table(data, colWidths=col_widths)
    
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)
    table_width, table_height = table.wrap(0, 0)
    x = (width - table_width) / 2
    y = title_y - 50 - table_height
    table.drawOn(c, x, y)
    c.save()
    

def export_report():
    
    data = {
        "No.": [],
        "Note": [],
        "Time": [],
        "Date": []
    }
    selection = filter_date.get()
    initial_data = sql.getNotesSpe(selection)
    
    for row in initial_data:
        reshaped_text = arabic_reshaper.reshape(row[0])
        bidi_text = get_display(reshaped_text)
        data["No."].append(row[3])
        data["Note"].append(Paragraph(bidi_text, arabic_text_style))
        data["Time"].append(row[1])
        data["Date"].append(row[2])
        
    contacts_df = pd.DataFrame(data)
    if selection == "All":
        name = f"Reports/{selection}-to-{curr_date}.pdf"
    else:
        name = f"Reports/{selection}.pdf"
    create_pdf(contacts_df, name)
    messagebox.showinfo(selection,f"Created Done !")
    

    

def delete_note(event):
    selected_item = treeview.selection()
    if selected_item:
        item = treeview.item(selected_item)
        spe_data = item['values']
        sql.deleteNote(spe_data[0],spe_data[3])
        selection = filter_date.get()
        initial_data = sql.getNotesSpe(selection)
        treeview.delete(*treeview.get_children())
        for row in initial_data:
            treeview.insert('',END,values=(row[3],row[0],row[1],row[2]))

        all_date = ['All']
        for row in sql.getDate():
            all_date.append(row[0])    
        filter_date['values'] = all_date
        dateEntry.insert(END, curr_date)


def limit_size(*args):
    value = entry_var.get()
    if len(value) > 5:
        entry_var.set(value[:5])

def validate_numeric_input(P):
    if P == "" or P == "." or P.isdigit() or P == ":":
        return True
    elif P.count('.') == 1 and P.replace(".", "").isdigit():
        return True
    elif P.count(':') == 1 and P.replace(":", "").isdigit():
        return True
    else:
        return False

def getTime():
    curr_time = time.strftime("%H:%M", time.localtime())
    timeEntry.delete("0", END)
    timeEntry.insert(END, curr_time)

def insert_data():
    selection = filter_date.get()
    global noNote
    note = noteEntry.get()
    time_ = timeEntry.get()
    date_ = dateEntry.get()
    sql.addDate(date_)
    sql.addNote(note,time_,date_)
    treeview.delete(*treeview.get_children())
    initial_data = sql.getNotesSpe(selection)
    for row in initial_data:
        treeview.insert('',END,values=(row[3],row[0],row[1],row[2]))
    noteEntry.delete("0",END)
    timeEntry.delete("0",END)
    all_date = ['All']
    for row in sql.getDate():
        all_date.append(row[0])    
    filter_date['values'] = all_date


def select_view(event):
    selection = filter_date.get()
    initial_data = sql.getNotesSpe(selection)
    treeview.delete(*treeview.get_children())
    for row in initial_data:
        treeview.insert('',END,values=(row[3],row[0],row[1],row[2]))

def fill_input(event):
    noteEntry.delete("0",END)
    timeEntry.delete("0",END)
    dateEntry.delete("0",END)
    selected_item = treeview.selection()
    if selected_item:
        item = treeview.item(selected_item)
        spe_data = item['values']
        noteEntry.insert(END,spe_data[1])
        timeEntry.insert(END,spe_data[2])
        dateEntry.insert(END,spe_data[3])
    else:
        dateEntry.insert(END, curr_date)

def update_note():
    selected_item = treeview.selection()
    if selected_item:
        item = treeview.item(selected_item)
        spe_data = item['values']
        id_ = spe_data[0]
        old_date = spe_data[3]
        note = noteEntry.get()
        time = timeEntry.get()
        new_date = dateEntry.get()
        sql.updateNote(note,time,new_date,old_date,id_)
        all_date = ['All']
        for row in sql.getDate():
            all_date.append(row[0])    
        filter_date['values'] = all_date
        selection = filter_date.get()
        initial_data = sql.getNotesSpe(selection)
        treeview.delete(*treeview.get_children())
        for row in initial_data:
            treeview.insert('',END,values=(row[3],row[0],row[1],row[2]))


def clearInput():
    noteEntry.delete("0",END)
    timeEntry.delete("0",END)
    dateEntry.delete("0",END)
    dateEntry.insert(END,curr_date)
    filter_date.current(0)
    selection = filter_date.get()
    initial_data = sql.getNotesSpe(selection)
    treeview.delete(*treeview.get_children())
    for row in initial_data:
        treeview.insert('',END,values=(row[3],row[0],row[1],row[2]))





root = tk.Tk()
root.resizable(False, False)
root.title("Daily Report")
root.geometry("+%d+%d" % ((root.winfo_screenwidth() - root.winfo_reqwidth()) / 2,
                          (root.winfo_screenheight() - root.winfo_reqheight()) / 2))
style = ttk.Style(root)

root.tk.call("source", "forest-light.tcl")
style.theme_use("forest-light")
style.configure('Treeview', rowheight=70)
validate_numeric = root.register(validate_numeric_input)
entry_var = tk.StringVar()
entry_var.trace('w', limit_size)

frame = ttk.Frame(root)
frame.pack()

topFrame = ttk.LabelFrame(frame, text="Enter a data")
topFrame.grid(row=0, column=0, padx=10, pady=10)

noteLabel = ttk.Label(topFrame, text="Note :")
noteLabel.grid(row=0, column=0, padx=5, pady=5)
noteEntry = ttk.Entry(topFrame, width=40)
noteEntry.grid(row=0, column=1, padx=5, pady=5)

timeLabel = ttk.Label(topFrame, text="Time :")
timeLabel.grid(row=0, column=2, padx=5, pady=5)
timeEntry = ttk.Entry(topFrame, validate="key", validatecommand=(validate_numeric, "%P"), width=15, textvariable=entry_var)
timeEntry.grid(row=0, column=3, padx=5, pady=5)
timeBut = ttk.Button(topFrame, text="Current Time", command=getTime)
timeBut.grid(row=0, column=4, pady=5, padx=(0, 5))

dateLabel = ttk.Label(topFrame, text="Date :")
dateLabel.grid(row=0, column=5, padx=5, pady=5)
dateEntry = ttk.Entry(topFrame, validate="key", width=15)
dateEntry.grid(row=0, column=6, padx=5, pady=5)

dateEntry.insert(END, curr_date)

insertBut = ttk.Button(topFrame,text="Insert",command=insert_data)
insertBut.grid(row=0,column=7,padx=5,pady=5)

medFrame = ttk.LabelFrame(frame,text="Control ")
medFrame.grid(row=1, column=0, padx=10, pady=10,sticky="w")
filterLabel = ttk.Label(medFrame,text="Filter data :")
filterLabel.grid(row=0,column=0,pady=5,padx=5)
selected_category = tk.StringVar()
filter_date = ttk.Combobox(medFrame, textvariable=selected_category, state="readonly")
filter_date['values'] = all_date
filter_date.current(0)
filter_date.grid(row=0, column=1, padx=5, pady=5)
filter_date.bind("<<ComboboxSelected>>", select_view)

updateBut = ttk.Button(medFrame, text="Update Note", command=update_note)
updateBut.grid(row=0, column=2, pady=5, padx=(0, 5))

exportBut = ttk.Button(medFrame, text="Export Report", command=export_report)
exportBut.grid(row=0, column=3, pady=5, padx=(0, 5))

clearBut = ttk.Button(medFrame,text="Clear",command=clearInput)
clearBut.grid(row=0,column=4,pady=5,padx=(0,5))

treeFrame = ttk.Frame(frame)
treeFrame.grid(row=2,column=0,padx=10,pady=10)
treeScroll = ttk.Scrollbar(treeFrame)
treeScroll.pack(side="right", fill="y")

cols = ("No.","Note","Time","Date")
treeview = ttk.Treeview(treeFrame,show="headings",yscrollcommand=treeScroll.set,columns=cols,height=7)
treeview.column("No.", width=60, anchor="center")
treeview.column("Note", width=450, anchor="center")
treeview.column("Time", width=175, anchor="center")
treeview.column("Date", width=175, anchor="center")
treeview.bind("<Double-Button-1>",delete_note)
treeview.bind("<ButtonRelease-1>",fill_input)
treeview.pack()
treeScroll.config(command=treeview.yview)
treeview.heading("#1", text="No.")
treeview.heading("#2", text="Task")
treeview.heading("#3", text="Time")
treeview.heading("#4", text="Date")

for row in initial_data:
    treeview.insert('',END,values=(row[3],row[0],row[1],row[2]))

root.update_idletasks()
root_width = root.winfo_width()
root_height = root.winfo_height()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - root_width) // 2
y = (screen_height - root_height) // 2
root.geometry("+{}+{}".format(x, y))
root.mainloop()
