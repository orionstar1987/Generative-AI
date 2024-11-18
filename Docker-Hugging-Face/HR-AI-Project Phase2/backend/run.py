"""App runner"""

from dotenv import load_dotenv, find_dotenv

from app import create_app

_ = load_dotenv(find_dotenv(filename=".env"))

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
