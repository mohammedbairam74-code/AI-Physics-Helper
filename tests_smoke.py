import os, tempfile
os.environ["DATABASE_PATH"] = os.path.join(tempfile.gettempdir(), "ai_physics_helper_smoke.db")
try: os.remove(os.environ["DATABASE_PATH"])
except FileNotFoundError: pass
os.environ.pop("OPENAI_API_KEY", None)
from fastapi.testclient import TestClient
from backend.main import app
from backend.advanced_solver import symbolic_solve
client=TestClient(app)
assert client.get("/health").json()["ok"] is True
assert client.get("/sources").status_code==200
assert client.get("/conversations").status_code==200
r=client.post("/ask",json={"question":"طاقة حركية كتلة 2 وسرعة 3"}); assert r.status_code==200 and "9" in r.json()["answer"]
r=client.post("/ask",json={"question":"كمية الحركة كتلة 2 وسرعة 5"}); assert r.status_code==200 and "10" in r.json()["answer"]
assert symbolic_solve("2*x+4=0","x")==["-2"]
assert symbolic_solve("x^2-9=0","x")==["-3","3"]
assert client.get("/").status_code==200
print("SMOKE TESTS PASSED")
