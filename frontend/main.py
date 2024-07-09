from pathlib import Path

import yaml
from fastapi import FastAPI
import uvicorn

from routers import home, user, files, about


def get_config() -> dict:
    config_file = Path(__file__).parent / "config" / f"config.yaml"
    app_config = yaml.safe_load(config_file.read_text())
    return app_config



if __name__ == '__main__':
    app = FastAPI()
    app.include_router(home.router)
    app.include_router(user.router)
    app.include_router(files.router)
    app.include_router(about.router)
    config = get_config()
    app.state.config = config
    uvicorn.run(app, port=config['port'], host=config['host'])