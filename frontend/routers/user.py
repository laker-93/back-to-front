import aiohttp
import logging
from http import HTTPStatus


from typing import Optional, Dict
from fastapi import Request, Header, APIRouter, Form, Depends, Cookie
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/user/signupform", response_class=HTMLResponse)
async def signup_form(
        request: Request,
        session_id: str | None = Cookie(None),
):
    templates = Jinja2Templates(directory="frontend/ui/templates")
    config = request.app.state.config

    context = {"request": request}
    success = False

    if session_id:
        try:
            username = await _get_username_by_session_id(config["backend-addr"], session_id)
        except Exception:
            logger.error('error getting user by session id', exc_info=True)
        else:
            context.update(
                {
                    "user": {
                        "username": username
                    }
                }
            )
            success = True
    if success:
        template = templates.TemplateResponse("partials/logged_in.html", context)
    else:
        template = templates.TemplateResponse("partials/signup_form.html", context)
    return template


async def _get_username_by_session_id(addr: str, session_id: str) -> str:
    data = {
        'session_id': session_id
    }

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), timeout=aiohttp.ClientTimeout()) as session:
        async with session.get(f'http://{addr}/user/get_by_session_id', params=data) as response:
            if response.status == HTTPStatus.OK:
                response_json = await response.json()
                try:
                    user = response_json['user']
                except KeyError:
                    logger.error(f'error extracting user from {response_json}', exc_info=True)
                    raise
                else:
                    try:
                        username = user['username']
                    except KeyError:
                        logger.error(f'error extracting username from {user}', exc_info=True)
                        raise
    return username


@router.get("/user/loginform", response_class=HTMLResponse)
async def login_form(request: Request,
                     session_id: str | None = Cookie(None),
                     hx_request: Optional[str] = Header(None),
                     ):
    templates = Jinja2Templates(directory="frontend/ui/templates")

    config = request.app.state.config

    context = {"request": request}
    success = False
    if session_id:
        try:
            username = await _get_username_by_session_id(config["backend-addr"], session_id)
        except Exception:
            logger.error('error getting user by session id', exc_info=True)
        else:
            context.update(
                {
                    "user": {
                        "username": username
                    }
                }
            )
            success = True
    if success:
        template = templates.TemplateResponse("partials/logged_in.html", context)
    else:
        template = templates.TemplateResponse("partials/login_form.html", context)
    return template


@router.post("/user/login", response_class=HTMLResponse)
async def login(
        request: Request,
        session_id: str | None = Cookie(None),
        username: str = Form(...),
        password: str = Form(...),
):
    print(f'username {username} password {password}')
    print(f'got cookie {session_id}')
    data = {
        'username': username,
        'password': password,
        # aiohttp does not support sending a None param
        'session_id': 'none' if not session_id else session_id
    }
    error = {}
    success = False
    config = request.app.state.config

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), timeout=aiohttp.ClientTimeout()) as session:
        async with session.post(f'http://{config["backend-addr"]}/user/login', params=data) as response:
            error['status_code'] = response.status
            if response.status == HTTPStatus.OK:
                response_json = await response.json()
                session_id = response.cookies.get('session_id').value
                print(response_json)
                template = 'partials/logged_in.html'
                success = True
            else:
                print(f'error {response.status} {HTTPStatus.OK}')
                try:
                    response_json = await response.json()
                except Exception:
                    logger.error(f'failed to decode response {response}', exc_info=True)
                    response_json = ""
                template = 'partials/failure.html'
                error['response'] = response_json

    templates = Jinja2Templates(directory="frontend/ui/templates")
    if success:
        context = {
            "request": request,
            "user": {
                "username": username
            }
        }
        response = templates.TemplateResponse(template, context)
        print(f'setting cookie to {session_id}')
        response.set_cookie(key='session_id', value=session_id, httponly=True)
    else:
        context = {"request": request, "error": error}
        response = templates.TemplateResponse(template, context)
    return response

@router.post("/user/create", response_class=HTMLResponse)
async def create(
        request: Request,
        session_id: str | None = Cookie(None),
        username: str = Form(...),
        password: str = Form(...),
        email: str = Form(...),
        newsletter: str | None = Form(True),
):
    templates = Jinja2Templates(directory="frontend/ui/templates")
    print(f'username {username} password {password} session id {session_id}')
    data = {
        'username': username,
        'password': password,
        'email': email,
        'newsletter': newsletter
    }
    error = {}
    success = False
    config = request.app.state.config

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), timeout=aiohttp.ClientTimeout()) as session:
        async with session.post(f'http://{config["backend-addr"]}/user/create', params=data) as response:
            error['status_code'] = response.status
            if response.status == HTTPStatus.OK:
                session_id = response.cookies.get('session_id')
                if session_id:
                    session_id = session_id.value
                    template = 'partials/success.html'
                else:
                    template = 'partials/max_users.html'
                success = True
            else:
                print(f'error {response.status} {HTTPStatus.OK}')
                try:
                    response_json = await response.json()
                except Exception:
                    logger.error(f'failed to decode response {response}', exc_info=True)
                    response_json = ""
                template = 'partials/failure.html'
                error['response'] = response_json

    context = {"request": request}
    if success:
        if session_id:
            response = templates.TemplateResponse(template, context)
            response.set_cookie(key='session_id', value=session_id, httponly=True)
        else:
            response = templates.TemplateResponse(template, context)
    else:
        context = {"request": request, "error": error}
        response = templates.TemplateResponse(template, context)

    return response
