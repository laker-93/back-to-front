import logging
from http import HTTPStatus

from fastapi import APIRouter, Request, Depends
from starlette.responses import JSONResponse

from backend.controllers.db_controller import DbController

router = APIRouter()

logger = logging.getLogger(__name__)


async def get_db_controller(req: Request) -> DbController:
    return req.app.state.db_controller


@router.post("/user/create", tags=["db"])
async def create_user(
        username: str,
        password: str,
        email: str,
        newsletter: str,
        db_controller: DbController = Depends(get_db_controller)
) -> JSONResponse:
    logger.info(f'creating user {username}')
    reason = ""
    success = True

    if newsletter == 'True':
        newsletter = True
    else:
        newsletter = False

    session_id = ""
    try:
        session_id = db_controller.create_user(username, password, email, newsletter)
    except Exception as ex:
        logger.error(f'error occurred creating services for user', exc_info=True)
        reason = repr(ex)
        success = False
    if session_id is None:
        reason = "max number of users reached"
    response = JSONResponse(content=reason, status_code=HTTPStatus.OK if success else HTTPStatus.INTERNAL_SERVER_ERROR)
    if success and session_id:
        logger.info(f'setting cookie to {session_id}')
        response.set_cookie(key='session_id', value=session_id, httponly=True)
    return response


@router.post("/user/login", tags=["user"])
async def user_login(
        username: str,
        password: str,
        session_id: str | None,
        db_controller: DbController = Depends(get_db_controller)
) -> JSONResponse:
    logger.info(f'logging in user {username}')
    reason = ""
    success = True
    if session_id is None or session_id == 'none':
        try:
            session_id = db_controller.create_session(username, password)
        except Exception as ex:
            logger.error(f'error occurred logging in user', exc_info=True)
            reason = repr(ex)
            success = False
    response = JSONResponse(content=reason, status_code=HTTPStatus.OK if success else HTTPStatus.INTERNAL_SERVER_ERROR)
    if success:
        logger.info(f'setting cookie to {session_id}')
        response.set_cookie(key='session_id', value=session_id, httponly=True)
    return response


@router.get("/user/delete", tags=["db"])
async def delete_user(
        username: str,
        db_controller: DbController = Depends(get_db_controller)
) -> dict:
    logger.info(f'deleting user {username}')
    reason = ""
    success = True
    try:
        db_controller.delete_user(username)
    except Exception as ex:
        logger.error(f'error occurred deleting user', exc_info=True)
        reason = repr(ex)
        success = False
    return {
        'success': success,
        'reason': reason
    }


@router.get("/user/get_by_username", tags=["db"])
async def get_user(
        username: str,
        db_controller: DbController = Depends(get_db_controller)
) -> dict:
    logger.info(f'retrieving user {username}')
    reason = ""
    success = True
    user: dict = {}
    try:
        user = db_controller.get_user(username)
    except Exception as ex:
        logger.error(f'error occurred getting user {username}', exc_info=True)
        reason = repr(ex)
        success = False
    return {
        'success': success,
        'reason': reason,
        'user': user
    }


@router.get("/user/get_by_session_id", tags=["db"])
async def get_user_by_session_id(
        session_id: str,
        db_controller: DbController = Depends(get_db_controller)
) -> dict:
    logger.info(f'retrieving user with session id {session_id}')
    reason = ""
    success = True
    user: dict = {}
    try:
        user = db_controller.get_user_by_session_id(session_id)
    except Exception as ex:
        logger.error(f'error occurred getting user for session id {session_id}', exc_info=True)
        reason = repr(ex)
        success = False
    finally:
        logger.info(f'found user {user}')
        return {
            'success': success,
            'reason': reason,
            'user': user
        }
