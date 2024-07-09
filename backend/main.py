from fastapi import FastAPI
import uvicorn
import yaml
from pathlib import Path

from backend.context_managers.lifespan import lifespan
from routers import user


def get_config() -> dict:
    config_file = Path(__file__).parent / "config" / f"config.yaml"
    app_config = yaml.safe_load(config_file.read_text())
    return app_config


if __name__ == '__main__':
    config = get_config()
    app = FastAPI(lifespan=lambda app: lifespan(app, config))
    app.include_router(user.router)
    uvicorn.run(app, port=config['port'], host=config['host'])