import sqlite3, json
from pathlib import Path
from .config import DATABASE_PATH

DB=Path(DATABASE_PATH)
DB.parent.mkdir(parents=True,exist_ok=True)

def conn():
    c=sqlite3.connect(DB)
    c.row_factory=sqlite3.Row
    return c

def init_db():
    c=conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS documents(
      id INTEGER PRIMARY KEY,
      title TEXT NOT NULL,
      authors TEXT DEFAULT '',
      year INTEGER,
      source TEXT NOT NULL,
      url TEXT DEFAULT '',
      doi TEXT DEFAULT '',
      category TEXT DEFAULT 'physics',
      abstract TEXT DEFAULT '',
      text TEXT NOT NULL,
      embedding TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
      title,authors,abstract,text,content='documents',content_rowid='id'
    );
    CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
      INSERT INTO documents_fts(rowid,title,authors,abstract,text)
      VALUES(new.id,new.title,new.authors,new.abstract,new.text);
    END;
    CREATE INDEX IF NOT EXISTS idx_category ON documents(category);
    CREATE INDEX IF NOT EXISTS idx_year ON documents(year);
    CREATE TABLE IF NOT EXISTS conversations(
      id INTEGER PRIMARY KEY,
      title TEXT NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS messages(
      id INTEGER PRIMARY KEY,
      conversation_id INTEGER NOT NULL,
      role TEXT NOT NULL,
      content TEXT NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(conversation_id) REFERENCES conversations(id)
    );
    """)
    c.commit(); c.close()

def add_document(d):
    c=conn()
    cur=c.execute("""INSERT INTO documents
      (title,authors,year,source,url,doi,category,abstract,text,embedding)
      VALUES(?,?,?,?,?,?,?,?,?,?)""",
      (d["title"],d.get("authors",""),d.get("year"),d["source"],d.get("url",""),
       d.get("doi",""),"physics",d.get("abstract",""),d["text"],
       json.dumps(d["embedding"]) if d.get("embedding") else None))
    c.commit(); rid=cur.lastrowid; c.close(); return rid

def search_text(q,limit=40):
    c=conn()
    try:
        rows=c.execute("""SELECT d.* FROM documents_fts f
        JOIN documents d ON d.id=f.rowid
        WHERE documents_fts MATCH ? LIMIT ?""",
        (" ".join(q.replace('"'," ").split()),limit)).fetchall()
    except sqlite3.OperationalError:
        rows=[]
    c.close()
    return [dict(r) for r in rows]

def get_all(limit=500):
    c=conn()
    rows=c.execute("SELECT * FROM documents ORDER BY COALESCE(year,0) DESC,id DESC LIMIT ?",(limit,)).fetchall()
    c.close()
    return [dict(r) for r in rows]

def create_conversation(title):
    c=conn()
    cur=c.execute("INSERT INTO conversations(title) VALUES(?)",(title,))
    c.commit()
    rid=cur.lastrowid
    c.close()
    return rid

def add_message(conversation_id,role,content):
    c=conn()
    c.execute("INSERT INTO messages(conversation_id,role,content) VALUES(?,?,?)",
              (conversation_id,role,content))
    c.commit()
    c.close()

def get_conversations():
    c=conn()
    rows=c.execute("SELECT * FROM conversations ORDER BY id DESC").fetchall()
    c.close()
    return [dict(r) for r in rows]

def get_messages(conversation_id):
    c=conn()
    rows=c.execute("SELECT * FROM messages WHERE conversation_id=? ORDER BY id",
                   (conversation_id,)).fetchall()
    c.close()
    return [dict(r) for r in rows]

def search_sources(query, category=None, limit=50):
    c=conn()
    if category:
        rows=c.execute("SELECT * FROM documents WHERE category=? AND (title LIKE ? OR abstract LIKE ? OR text LIKE ?) ORDER BY COALESCE(year,0) DESC LIMIT ?",
                       (category,f"%{query}%",f"%{query}%",f"%{query}%",limit)).fetchall()
    else:
        rows=c.execute("SELECT * FROM documents WHERE title LIKE ? OR abstract LIKE ? OR text LIKE ? ORDER BY COALESCE(year,0) DESC LIMIT ?",
                       (f"%{query}%",f"%{query}%",f"%{query}%",limit)).fetchall()
    c.close()
    return [dict(r) for r in rows]
