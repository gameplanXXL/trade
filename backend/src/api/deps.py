"""API dependencies for dependency injection."""

from typing import Annotated

from fastapi import Depends

from src.config.settings import Settings, get_settings

# Settings dependency
SettingsDep = Annotated[Settings, Depends(get_settings)]
