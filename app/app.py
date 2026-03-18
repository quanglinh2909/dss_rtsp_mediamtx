import importlib
import pkgutil
from fastapi import APIRouter, Depends

from app.routers import __path__ as routers_path  # path của app/routers


def create_api_router() -> APIRouter:
    api_router = APIRouter()

    for _, module_name, _ in pkgutil.iter_modules(routers_path):
        if module_name.endswith("_router"):
            module_path = f"app.routers.{module_name}"
            module = importlib.import_module(module_path)

            if hasattr(module, "router"):
                # Lấy prefix và tags từ module nếu có
                prefix = getattr(module, "prefix", None)
                tags = getattr(module, "tags", None)
                auth = getattr(module, "auth", None)

                # Nếu không có, tự động sinh từ tên file
                if prefix is None:
                    prefix = "/" + module_name.replace("_router", "").replace("_", "-")
                if tags is None:
                    tags = [module_name.replace("_router", "").replace("_", " ").title()]

                else:
                    api_router.include_router(
                        module.router,
                        prefix=prefix,
                        tags=tags
                    )

    return api_router


# Sử dụng:
api_router = create_api_router()
