import os.path as op
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.staticfiles import StaticFiles

from contextlib import asynccontextmanager
from concurrent.futures.process import ProcessPoolExecutor

from app import settings

from app.routes.user.converter.csv2smi import user_converter_csv2smi_router
from app.routes.user.converter.sdf2smi import user_converter_sdf2smi_router
from app.routes.user.similarity.distributed import user_similarity_distributed_router
from app.routes.user.similarity.libraries import user_similarity_libraries_router
from app.routes.user.similarity.parallel import user_similarity_parallel_router
from app.routes.user.substructure.parallel import user_substructure_parallel_router

class CustomMiddleware(BaseHTTPMiddleware):
    # async def dispatch(self, request: Request, call_next: Callable) -> Response:
    #     return await call_next(request)
    async def dispatch(self, request, call_next) -> Response:
        response: Response = await call_next(request)
        response.headers.update({
            # "Cache-Control": "max-age=60" # 60 seconds
            "Cache-Control": "no-cache"
        })
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.executor = ProcessPoolExecutor()
    yield
    app.state.executor.shutdown()

app = FastAPI(lifespan=lifespan, title=settings.app_name, version=settings.app_version, docs_url="/api/docs")
app.add_middleware(CustomMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/assets", StaticFiles(directory=op.join(settings.base_dir, "assets")), name="assets")

app.include_router(router=user_converter_csv2smi_router)
app.include_router(router=user_converter_sdf2smi_router)
app.include_router(router=user_similarity_distributed_router)
app.include_router(router=user_similarity_libraries_router)
app.include_router(router=user_similarity_parallel_router)
app.include_router(router=user_substructure_parallel_router)
