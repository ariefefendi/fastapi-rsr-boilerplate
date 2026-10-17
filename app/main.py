from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions import NotFoundError, UniqueViolationError
from app.routers import units

app = FastAPI(title="Django Core API")


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    """Format error ala Laravel:
    {"result": "VALIDATION_ERROR", "errors": {"field": ["pesan"]}}
    """
    errors: dict[str, list[str]] = {}
    for err in exc.errors():
        loc = [str(p) for p in err["loc"] if p not in ("body", "query", "path")]
        field = ".".join(loc) or "_"
        errors.setdefault(field, []).append(err["msg"])
    return JSONResponse(
        status_code=422,
        content={"result": "VALIDATION_ERROR", "errors": errors},
    )


@app.exception_handler(UniqueViolationError)
async def unique_violation_handler(request: Request, exc: UniqueViolationError):
    return JSONResponse(
        status_code=422,
        content={"result": "VALIDATION_ERROR", "errors": {exc.field: [exc.message]}},
    )


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": exc.message})


app.include_router(units.router)
