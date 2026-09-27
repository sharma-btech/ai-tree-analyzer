from flask import Flask, request, jsonify, send_from_directory
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

# ==============================
# PATHS
# ==============================

BACKEND_FOLDER = os.path.dirname(os.path.abspath(__file__))
PROJECT_FOLDER = os.path.dirname(BACKEND_FOLDER)

# ==============================
# LOAD API KEY
# ==============================

env_path = os.path.join(BACKEND_FOLDER, ".env")
load_dotenv(env_path, override=True)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in backend/.env")

# ==============================
# FLASK
# ==============================

app = Flask(__name__)

# ==============================
# GEMINI
# ==============================

client = genai.Client(api_key=api_key)

# ==============================
# WEBSITE
# ==============================

@app.route("/")
def home():
    return send_from_directory(PROJECT_FOLDER, "index.html")


@app.route("/<path:filename>")
def files(filename):
    return send_from_directory(PROJECT_FOLDER, filename)


# ==============================
# TREE ANALYSIS
# ==============================

@app.route("/analyze", methods=["POST"])
def analyze_tree():

    try:
        if "image" not in request.files:
            return jsonify({
                "error": "No image uploaded."
            }), 400

        image = request.files["image"]

        if image.filename == "":
            return jsonify({
                "error": "No image selected."
            }), 400

        image_bytes = image.read()

        if not image_bytes:
            return jsonify({
                "error": "Image is empty."
            }), 400

        prompt = """
Analyze this tree image.

Give the answer in simple English.

Use EXACTLY these sections:

Tree Name:
Tree Health:
Leaf Condition:
Possible Issues:
Water Requirement:
Care Suggestion:

Important:
- If the tree species cannot be identified confidently, say "Identification uncertain".
- Do not claim a disease with certainty from an image alone.
- Treat the result as an image-based estimate.
- Keep each section short and clear.
"""

        # Gemini request
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=image.content_type or "image/jpeg"
                ),
                prompt
            ]
        )

        if not response.text:
            return jsonify({
                "error": "Gemini returned an empty response."
            }), 500

        return jsonify({
            "analysis": response.text
        })

    except Exception as e:
        print("Gemini error:")
        print(str(e))

        return jsonify({
            "error": "Gemini analysis failed.",
            "details": str(e)
        }), 500


# ==============================
# START SERVER
# ==============================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
