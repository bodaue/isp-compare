from fastapi.routing import APIRouter

from isp_compare.api.v1 import auth, provider, review, search_history, tariff, user

main_router = APIRouter()
main_router.include_router(auth.router)
main_router.include_router(user.router)
main_router.include_router(provider.router)
main_router.include_router(tariff.router)
main_router.include_router(review.router)
main_router.include_router(search_history.router)
