from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import os
from src.pipeline import main_pipeline
from src.logger import logger

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure key

UPLOAD_FOLDER = "data/input_video"
GENERATED_PPT_FOLDER = "data/ppt"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["GENERATED_PPT_FOLDER"] = GENERATED_PPT_FOLDER

# Home route
@app.route("/")
def index():
    return render_template("index.html")

# Upload route
@app.route("/upload", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        flash("No file part")
        return redirect(request.url)
    file = request.files["video"]
    if file.filename == "":
        flash("No selected file")
        return redirect(request.url)
    if file:
        video_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(video_path)
        logger.info(f"Uploaded file saved to {video_path}")
        try:
            main_pipeline(video_path)  # Run the pipeline
            ppt_path = os.path.join(app.config["GENERATED_PPT_FOLDER"], "presentation.pptx")
            return redirect(url_for("download_ppt", filename="presentation.pptx"))
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            flash("An error occurred while processing the video.")
            return redirect("/")
    else:
        flash("Unsupported file type.")
        return redirect("/")

# Download route
@app.route("/download/<filename>")
def download_ppt(filename):
    return send_from_directory(app.config["GENERATED_PPT_FOLDER"], filename, as_attachment=True)

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(GENERATED_PPT_FOLDER, exist_ok=True)
    app.run(debug=True)
