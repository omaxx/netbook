import os
import dotenv

dotenv.load_dotenv()


class BaseConfig:
    API_TITLE = "NetBook API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"

    OPENAPI_JSON_PATH = "api-spec.json"
    OPENAPI_URL_PREFIX = "/api"
    OPENAPI_REDOC_PATH = "/redoc"
    OPENAPI_REDOC_URL = (
        "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    )
    # OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_PATH = "/"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    OPENAPI_RAPIDOC_PATH = "/rapidoc"
    OPENAPI_RAPIDOC_URL = "https://unpkg.com/rapidoc/dist/rapidoc-min.js"


settings = {
    "db": {
        "mongo": {
            "host": os.environ.get("PG_DB_MONGO_HOST"),
            "dbe": os.environ.get("PG_DB_MONGO_DB"),
            "username": os.environ.get("PG_DB_MONGO_USERNAME"),
            "password": os.environ.get("PG_DB_MONGO_PASSWORD"),
        }
    }
}
