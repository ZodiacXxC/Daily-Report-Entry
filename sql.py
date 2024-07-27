import sqlite3

def addDate(dateEntry):
    with sqlite3.connect("main.db") as sql_connect:
        cursor = sql_connect.cursor()
        cursor.execute('''
            SELECT * FROM Date_table WHERE date_report = ?
        ''', (dateEntry,))
        exists = cursor.fetchone()
        if not exists:
            cursor.execute('''
                INSERT INTO Date_table (date_report)
                VALUES (?)
            ''', (dateEntry,))
        sql_connect.commit()

def addNote(note, time, dateEntry):
    with sqlite3.connect("main.db") as sql_connect:
        cursor = sql_connect.cursor()
        cursor.execute('''
            SELECT MAX(entry_number) FROM Report WHERE date_report = ?
        ''', (dateEntry,))
        last_entry_number = cursor.fetchone()[0]
        if last_entry_number is None:
            last_entry_number = 0
        
        entry_number = last_entry_number + 1
        
        cursor.execute('''
            INSERT INTO Report (Note, time_note, date_report, entry_number)
            VALUES (?, ?, ?, ?)
        ''', (note, time, dateEntry, entry_number))
        sql_connect.commit()


def deleteNote(id_,dateEntry):
    with sqlite3.connect("main.db") as sql_connect:
        cursor = sql_connect.cursor()
        cursor.execute('''DELETE FROM Report WHERE entry_number = ? AND date_report = ?''', (id_, dateEntry))
        sql_connect.commit()

        cursor.execute('''SELECT COUNT(*) FROM Report WHERE date_report = ?''', (dateEntry,))
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.execute('''DELETE FROM Date_table WHERE date_report = ?''', (dateEntry,))
            sql_connect.commit()


def getNotesSpe(dateEntry):
    with sqlite3.connect("main.db") as sql_connect:
        cursor = sql_connect.cursor()
        if dateEntry == "All":
            cursor.execute('''SELECT * FROM Report ORDER BY date_report''')
        else:
            cursor.execute('''SELECT * FROM Report WHERE date_report = ? ORDER BY date_report''', (dateEntry,))
        return cursor.fetchall()

def getNotes():
    with sqlite3.connect("main.db") as sql_connect:
        cursor = sql_connect.cursor()
        cursor.execute('''SELECT * FROM Report ORDER BY date_report ''')
        return cursor.fetchall()

def getDate():
    with sqlite3.connect("main.db") as sql_connect:
        cursor = sql_connect.cursor()
        cursor.execute('''SELECT date_report FROM Date_table ORDER BY date_report''')
        return cursor.fetchall()

def updateNote(note, time, dateEntry,old_date,id_):
    with sqlite3.connect("main.db") as sql_connect:
        cursor = sql_connect.cursor()
        new_num = id_
        if dateEntry != old_date:
            cursor.execute('''SELECT entry_number FROM Report WHERE date_report = ? ORDER BY entry_number DESC''',(dateEntry,))
            new_num = cursor.fetchall()
            if not new_num:
                new_num = 0
            else:
                new_num = new_num[0][0]
            new_num += 1
        cursor.execute('''UPDATE Report SET entry_number = ?, Note = ?,time_note = ?,date_report = ? WHERE entry_number = ? AND date_report = ?
            ''',(new_num,note,time,dateEntry,id_,old_date))

        cursor.execute('''SELECT COUNT(*) FROM Report WHERE date_report = ?''', (old_date,))
        count = cursor.fetchone()[0]
        print(count)
        cursor.execute('''SELECT COUNT(*) FROM Report WHERE date_report = ?''', (dateEntry,))
        count2 = cursor.fetchone()[0]
        print(count2)
        if count == 0:
            cursor.execute('''DELETE FROM Date_table WHERE date_report = ?''', (old_date,))
            sql_connect.commit()
        if count2 == 1:
            cursor.execute('''
                INSERT INTO Date_table (date_report)
                VALUES (?)
            ''', (dateEntry,))




with sqlite3.connect("main.db") as sql_connect:
    cursor = sql_connect.cursor()
    cursor.execute('PRAGMA foreign_keys = ON;')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Date_table (
            ID_date INTEGER PRIMARY KEY AUTOINCREMENT,
            date_report TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Report (
            Note TEXT NOT NULL,
            time_note REAL NOT NULL,
            date_report TEXT NOT NULL,
            entry_number INTEGER NOT NULL
        )
    ''')
    sql_connect.commit()

