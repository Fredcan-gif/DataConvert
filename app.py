import csv
import io
import json

from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

# Course code -> full program name.
# Edit/extend this to match the codes used in exercise_datamap.csv.
PROGRAMS = {
    "BSIT": "Bachelor of Science in Information Technology",
    "BSCS": "Bachelor of Science in Computer Science",
    "BSIS": "Bachelor of Science in Information Systems",
    "BSBA": "Bachelor of Science in Business Administration",
    "BSA": "Bachelor of Science in Accountancy",
    "BSN": "Bachelor of Science in Nursing",
    "BSED": "Bachelor of Science in Education",
    "BSCE": "Bachelor of Science in Civil Engineering",
    "BSCPE": "Bachelor of Science in Computer Engineering",
    "BSHM": "Bachelor of Science in Hospitality Management",
    "BSTM": "Bachelor of Science in Tourism Management",
    "BSPSY": "Bachelor of Science in Psychology",
}


def capitalize_first(value: str) -> str:
    value = (value or "").strip()
    return value[:1].upper() + value[1:]


def to_int(value: str) -> int:
    return int(str(value).strip())


def to_money(value: str) -> float:
    cleaned = str(value).strip().replace(",", "").replace("$", "").replace("₱", "")
    return round(float(cleaned), 2)


def full_program(course: str) -> str:
    course = (course or "").strip()
    return PROGRAMS.get(course.upper(), course)  # fall back to original value


def transform(row: dict) -> dict:
    return {
        "studentId": to_int(row["student_id"]),
        "firstName": capitalize_first(row["first_name"]),
        "lastName": capitalize_first(row["last_name"]),
        "program": full_program(row["course"]),
        "yearLevel": to_int(row["year_level"]),
        "emailAddress": row["email"].strip().lower(),
        "outstandingBalance": f"{to_money(row['tuition_balance']):.2f}",
    }


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify(error="No file uploaded."), 400
    try:
        text = file.read().decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        reader.fieldnames = [f.strip().lower() for f in (reader.fieldnames or [])]
        result = []
        for row in reader:
            result.append(transform(row))
        return app.response_class(
            json.dumps(result, indent=2, ensure_ascii=False),
            mimetype="application/json",
        )
    except KeyError as e:
        return jsonify(error=f"Missing expected column: {e}"), 400
    except (ValueError, UnicodeDecodeError) as e:
        return jsonify(error=f"Could not parse CSV: {e}"), 400


if __name__ == "__main__":
    app.run(debug=True)
