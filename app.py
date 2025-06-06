import os
import psycopg2
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database connection setup using RDS credentials
def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        port=os.environ.get("DB_PORT", 5432)
    )

# GET all albums
@app.route("/albums", methods=["GET"])
def get_albums():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, release_year, artist_id FROM albums")
    albums = cur.fetchall()
    cur.close()
    conn.close()

    result = [
        {"id": row[0], "title": row[1], "release_year": row[2], "artist_id": row[3]}
        for row in albums
    ]
    return render_template('index.html', albums=result)
# GET a specific album
@app.route("/albums/<int:album_id>", methods=["GET"])
def get_album(album_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, release_year, artist_id FROM albums WHERE id = %s", (album_id,))
    album = cur.fetchone()
    cur.close()
    conn.close()

    if album:
        album_dict = {
            "id": album[0],
            "title": album[1],
            "release_year": album[2],
            "artist_id": album[3]
        }
        # Render show.html passing the album data
        return render_template("show.html", album=album_dict)
    else:
        # You can render a custom 404 page or just show an error message
        return render_template("404.html"), 404
# POST a new album
@app.route("/albums", methods=["POST"])
def add_album():
    data = request.get_json()
    title = data.get("title")
    release_year = data.get("release_year")
    artist_id = data.get("artist_id")

    if not all([title, release_year, artist_id]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO albums (title, release_year, artist_id) VALUES (%s, %s, %s)",
        (title, release_year, artist_id)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Album added successfully"}), 201

# Run the app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
