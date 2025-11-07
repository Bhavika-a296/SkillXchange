import sqlite3
import json

DB = 'db.sqlite3'
conn = sqlite3.connect(DB)
cur = conn.cursor()

print('SQLite file:', DB)
print('\nTables:')
for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"):
    print('-', row[0])

def print_schema(table):
    print('\nSchema for', table)
    cols = cur.execute(f"PRAGMA table_info({table});").fetchall()
    for c in cols:
        print(c)
    try:
        count = cur.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0]
        print('Row count:', count)
        if count>0:
            print('Sample rows (up to 5):')
            for r in cur.execute(f"SELECT * FROM {table} LIMIT 5;"):
                print(r)
    except Exception as e:
        print('Could not read rows for', table, '->', e)

# Inspect key tables
for t in ['api_userprofile', 'api_connection', 'api_message', 'api_skill', 'auth_user', 'api_resume']:
    try:
        print_schema(t)
    except Exception as e:
        print('\nTable', t, 'not found or error ->', e)

conn.close()
