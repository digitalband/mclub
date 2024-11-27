import logging

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from core.config import settings
from api_v1.routers import router as api_v1_router
from api_v1.exceptions import APIException

settings.logging.configure_logging()

app = FastAPI()


@app.exception_handler(APIException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logging.info(f"API Exception > {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


app.include_router(api_v1_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8001, reload=True)
