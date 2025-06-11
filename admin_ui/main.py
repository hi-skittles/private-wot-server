from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, FileResponse
from starlette.staticfiles import StaticFiles
from pydantic import BaseModel
import mysql.connector
import secrets
import os
import base64
import pickle

app = FastAPI(title="Player Data Admin UI")
security = HTTPBasic()

DB_CONFIG = dict(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "bigworld"),
    password=os.getenv("DB_PASSWORD", "bigworld"),
    database=os.getenv("DB_NAME", "player_data_dev1"),
)

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin")

# ----- Authentication -----
def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USER)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASS)
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    return credentials.username

# ----- Database utilities -----

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

TABLES = {"stats", "dossier", "inventory", "quests"}

def decode_row(row):
    decoded = {}
    for k, v in row.items():
        if v is None:
            decoded[k] = None
            continue
        try:
            if isinstance(v, str):
                v_bytes = v.encode()
            else:
                v_bytes = v
            decoded[k] = pickle.loads(base64.b64decode(v_bytes))
        except Exception:
            try:
                decoded[k] = v.decode() if isinstance(v, (bytes, bytearray)) else v
            except Exception:
                decoded[k] = v
    return decoded

def encode_payload(data):
    encoded = {}
    for k, v in data.items():
        try:
            encoded[k] = base64.b64encode(pickle.dumps(v))
        except Exception:
            encoded[k] = v
    return encoded

# ----- Data models -----

class Player(BaseModel):
    email: str
    data: dict

# ----- API Endpoints -----

@app.get("/players", dependencies=[Depends(get_current_username)])
def list_players():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT email FROM stats LIMIT 100")
    players = [row["email"] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return {"players": players}

@app.get("/players/{email}", dependencies=[Depends(get_current_username)])
def get_player(email: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM stats WHERE email=%s", (email,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Player not found")
    return decode_row(row)

@app.put("/players/{email}", dependencies=[Depends(get_current_username)])
def update_player(email: str, payload: Player):
    conn = get_connection()
    cursor = conn.cursor()
    data = encode_payload(payload.data)
    if not data:
        raise HTTPException(status_code=400, detail="No data provided")
    assignments = ", ".join(f"{col}=%s" for col in data.keys())
    values = list(data.values()) + [email]
    cursor.execute(
        f"UPDATE stats SET {assignments} WHERE email=%s",
        values,
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "updated"}


@app.get("/data/{table}/{email}", dependencies=[Depends(get_current_username)])
def get_table_data(table: str, email: str):
    table = table.lower()
    if table not in TABLES:
        raise HTTPException(status_code=400, detail="Invalid table")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {table} WHERE email=%s", (email,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Record not found")
    return decode_row(row)


@app.put("/data/{table}/{email}", dependencies=[Depends(get_current_username)])
def update_table_data(table: str, email: str, payload: dict):
    table = table.lower()
    if table not in TABLES:
        raise HTTPException(status_code=400, detail="Invalid table")
    data = encode_payload(payload)
    if not data:
        raise HTTPException(status_code=400, detail="No data provided")
    assignments = ", ".join(f"`{col}`=%s" for col in data.keys())
    values = list(data.values()) + [email]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE {table} SET {assignments} WHERE email=%s",
        values,
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "updated"}

# ----- Static files -----
app.mount("/static", StaticFiles(directory="admin_ui/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def read_index():
    return FileResponse("admin_ui/templates/index.html")
