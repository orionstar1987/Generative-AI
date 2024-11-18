"""__main__.py"""

from dotenv import load_dotenv, find_dotenv
from . import create_app

if __name__ == "__main__":
    status = load_dotenv(find_dotenv(filename=".env.local"))
    print(status)
    create_app().run(debug=True, threaded=True)
