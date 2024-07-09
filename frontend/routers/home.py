from typing import Optional
from fastapi import Request, Header, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
@router.get("/", response_class=HTMLResponse)
async def home(request: Request, hx_request: Optional[str] = Header(None)):
    templates = Jinja2Templates(directory="ui/templates")
    context = {"request": request}
    return templates.TemplateResponse("home.html", context)