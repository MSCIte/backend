import os

from dotenv import dotenv_values
from functools import lru_cache


@lru_cache()
def get_env():
    if os.environ.get("ENV") == "production":
        specific_to_env_vars = {
            **dotenv_values(".env.prod"),
            **dotenv_values(".env.prod.local")
        }
    else:  # development
        specific_to_env_vars = {
            **dotenv_values(".env.dev"),
            **dotenv_values(".env.dev.local")
        }

    env = {
        **dotenv_values(".env.shared"),  # load shared development variables
        **specific_to_env_vars,  # dev vars
        **os.environ,  # override loaded values with environment variables
    }

    return env
