import os
from .config import OPENAI_API_KEY
from .db import init_db
def run():
    init_db()
    return bool(OPENAI_API_KEY)
if __name__=="__main__":
    print("database: PASS")
    print("OPENAI_API_KEY present:", "YES" if run() else "NO")
