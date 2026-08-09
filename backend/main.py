from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
import os, sqlite3, uuid, shutil

APP_SECRET = os.getenv("APP_SECRET", "CHANGE_THIS_SECRET_IN_PRODUCTION")
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "CHANGE_THIS_PASSWORD")
DB_PATH = os.getenv("DB_PATH", "data.db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Manoj Mishra Portfolio API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer(auto_error=False)

def db():
    c=sqlite3.connect(DB_PATH)
    c.row_factory=sqlite3.Row
    return c

def init():
    c=db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY AUTOINCREMENT,title_hi TEXT,title_en TEXT,body_hi TEXT,body_en TEXT,type TEXT,created_at TEXT);
    CREATE TABLE IF NOT EXISTS gallery(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,image TEXT,category TEXT,created_at TEXT);
    CREATE TABLE IF NOT EXISTS contacts(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,email TEXT,message TEXT,created_at TEXT,read INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS career(id INTEGER PRIMARY KEY AUTOINCREMENT,year TEXT,title_hi TEXT,title_en TEXT,description_hi TEXT,description_en TEXT);
    """)
    c.commit(); c.close()
init()

class Login(BaseModel): username:str; password:str
class Post(BaseModel):
    title_hi:str; title_en:str=""; body_hi:str; body_en:str=""; type:str="Blog"
class Career(BaseModel):
    year:str; title_hi:str; title_en:str=""; description_hi:str; description_en:str=""
class Contact(BaseModel): name:str; email:str; message:str

def token_for(user):
    return jwt.encode({"sub":user,"exp":datetime.now(timezone.utc)+timedelta(hours=12)}, APP_SECRET, algorithm="HS256")
def admin(creds:HTTPAuthorizationCredentials=Depends(bearer)):
    if not creds: raise HTTPException(401,"Login required")
    try:
        p=jwt.decode(creds.credentials,APP_SECRET,algorithms=["HS256"])
        if p.get("sub")!=ADMIN_USER: raise Exception()
        return p
    except Exception: raise HTTPException(401,"Invalid or expired token")

@app.get("/api/health")
def health(): return {"ok":True}

@app.post("/api/admin/login")
def login(x:Login):
    if x.username==ADMIN_USER and x.password==ADMIN_PASSWORD: return {"access_token":token_for(x.username)}
    raise HTTPException(401,"Invalid credentials")

@app.get("/api/posts")
def posts():
    c=db(); rows=c.execute("SELECT * FROM posts ORDER BY id DESC").fetchall(); c.close()
    return [dict(r) for r in rows]

@app.post("/api/posts")
def add_post(x:Post, _:dict=Depends(admin)):
    c=db(); cur=c.execute("INSERT INTO posts(title_hi,title_en,body_hi,body_en,type,created_at) VALUES(?,?,?,?,?,?)",
        (x.title_hi,x.title_en,x.body_hi,x.body_en,x.type,datetime.now(timezone.utc).isoformat()))
    c.commit(); item=dict(c.execute("SELECT * FROM posts WHERE id=?",(cur.lastrowid,)).fetchone()); c.close(); return item

@app.delete("/api/posts/{id}")
def delete_post(id:int,_:dict=Depends(admin)):
    c=db(); c.execute("DELETE FROM posts WHERE id=?",(id,)); c.commit(); c.close(); return {"ok":True}

@app.get("/api/career")
def career():
    c=db(); rows=c.execute("SELECT * FROM career ORDER BY CAST(year AS INTEGER)").fetchall(); c.close(); return [dict(r) for r in rows]

@app.post("/api/career")
def add_career(x:Career,_:dict=Depends(admin)):
    c=db(); cur=c.execute("INSERT INTO career(year,title_hi,title_en,description_hi,description_en) VALUES(?,?,?,?,?)",
        (x.year,x.title_hi,x.title_en,x.description_hi,x.description_en)); c.commit()
    item=dict(c.execute("SELECT * FROM career WHERE id=?",(cur.lastrowid,)).fetchone()); c.close(); return item

@app.delete("/api/career/{id}")
def delete_career(id:int,_:dict=Depends(admin)):
    c=db(); c.execute("DELETE FROM career WHERE id=?",(id,)); c.commit(); c.close(); return {"ok":True}

@app.get("/api/gallery")
def gallery():
    c=db(); rows=c.execute("SELECT * FROM gallery ORDER BY id DESC").fetchall(); c.close(); return [dict(r) for r in rows]

@app.post("/api/gallery")
async def upload_gallery(title:str,category:str,file:UploadFile=File(...),_:dict=Depends(admin)):
    ext=os.path.splitext(file.filename or "")[1].lower()[:10] or ".jpg"
    name=f"{uuid.uuid4().hex}{ext}"; path=os.path.join(UPLOAD_DIR,name)
    with open(path,"wb") as out: shutil.copyfileobj(file.file,out)
    c=db(); cur=c.execute("INSERT INTO gallery(title,image,category,created_at) VALUES(?,?,?,?)",
        (title,f"/uploads/{name}",category,datetime.now(timezone.utc).isoformat())); c.commit()
    item=dict(c.execute("SELECT * FROM gallery WHERE id=?",(cur.lastrowid,)).fetchone()); c.close(); return item

@app.delete("/api/gallery/{id}")
def delete_gallery(id:int,_:dict=Depends(admin)):
    c=db(); row=c.execute("SELECT image FROM gallery WHERE id=?",(id,)).fetchone()
    if row:
        fn=row["image"].replace("/uploads/",""); p=os.path.join(UPLOAD_DIR,fn)
        if os.path.exists(p): os.remove(p)
    c.execute("DELETE FROM gallery WHERE id=?",(id,)); c.commit(); c.close(); return {"ok":True}

@app.post("/api/contact")
def contact(x:Contact):
    c=db(); c.execute("INSERT INTO contacts(name,email,message,created_at) VALUES(?,?,?,?)",
        (x.name,x.email,x.message,datetime.now(timezone.utc).isoformat())); c.commit(); c.close()
    return {"ok":True}

@app.get("/api/contacts")
def contacts(_:dict=Depends(admin)):
    c=db(); rows=c.execute("SELECT * FROM contacts ORDER BY id DESC").fetchall(); c.close(); return [dict(r) for r in rows]

@app.delete("/api/contacts/{id}")
def delete_contact(id:int,_:dict=Depends(admin)):
    c=db(); c.execute("DELETE FROM contacts WHERE id=?",(id,)); c.commit(); c.close(); return {"ok":True}
