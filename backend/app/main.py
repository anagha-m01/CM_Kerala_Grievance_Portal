from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.routes import router

settings = get_settings()
app = FastAPI(
    title='CM Kerala Public Grievance Portal - Recruitment Prototype',
    description='Fictional recruitment prototype. Not affiliated with the Government of Kerala.',
    version='0.1.0',
)
app.add_middleware(
    CORSMiddleware, allow_origins=settings.origins, allow_credentials=False,
    allow_methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'], allow_headers=['Authorization', 'Content-Type'],
)
app.include_router(router)


@app.get('/')
def root():
    return {'message': 'CM Kerala Recruitment Prototype API', 'docs': '/docs'}
