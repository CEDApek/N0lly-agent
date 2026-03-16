from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

# basic application config
class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "N0lly")
    app_env: str = os.getenv("APP_ENV", "dev")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    allow_private_targets: bool = os.getenv("ALLOW_PRIVATE_TARGETS", "true").lower() == "true"
    default_profile: str = os.getenv("DEFAULT_PROFILE", "baseline")


settings = Settings()