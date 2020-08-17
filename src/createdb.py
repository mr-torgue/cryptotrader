import sqlite3

print("Database name:")
filename = input() + ".db"
conn = sqlite3.connect(filename)
conn.execute('''CREATE TABLE HISTORY
         (ID INTEGER PRIMARY KEY AUTOINCREMENT,
         market CHAR(16),
         value FLOAT NOT NULL,
         timestamp DATE DEFAULT (datetime('now','localtime')));''')
conn.close()