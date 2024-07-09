from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict

from fastapi import FastAPI
from tinydb import TinyDB

from backend.controllers.db_controller import DbController




@asynccontextmanager
async def lifespan(app: FastAPI, config: Dict):
    db_path = Path(config['db']['path'])
    if not db_path.exists():
        db_path.parent.mkdir(parents=True)
    app.state.db_controller = DbController(TinyDB(db_path))
    yield
