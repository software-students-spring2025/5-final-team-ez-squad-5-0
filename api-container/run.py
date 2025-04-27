from app import create_app
import os
import sys

# Add the current directory to the path so that the script can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


app = create_app()

if __name__ == "__main__":
    # trigger API CI/CD test
    # Run the app
    app.run(host="0.0.0.0", port=5001, debug=True)
