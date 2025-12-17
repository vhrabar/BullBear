import os
from dotenv import load_dotenv

load_dotenv()
production = os.getenv("PRODUCTION", "false").lower() == "true"

if production:
    from .prod import *
else:
    from .dev import *
