import os.path as op
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "API"
    app_version: str = "1.0"
    base_dir: str = op.abspath(op.dirname(__file__))
    asset_dir: str = op.join(base_dir, "assets")

    py: str = "/share1-100G/fanny/anaconda3/envs/xxx/bin/python"


# Settings().model_dump()
settings = Settings.model_validate({})
