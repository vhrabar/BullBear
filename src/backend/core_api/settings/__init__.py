import os

production = os.getenv("PRODUCTION", "false").lower() == "true"

if production:
    from .prod import *
else:
    from .dev import *
