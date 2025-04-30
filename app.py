from flask import Flask, request, jsonify, render_template
import pandas as pd
import random
import json

app = Flask(__name__)
df_tags = pd.read_pickle("exercise_tags.pkl")

# 🔍 Print all unique tags in the loaded .pkl file
print("🧪 Sample of ALL tags:", sorted(set(tag for tags in df_tags['Category'] for tag in tags)), flush=True)

with open("full_focus_rules.json") as f:
    focus_rules = json.load(f)

def filter_exercises(subcategory, access):
    print("🔎 Searching for:", subcategory, access, flush=True)
    print("🧠 Sample tags from file:", df_tags.iloc[0]['Category'], flush=True)
    return df_tags[
        df_tags['Category'].apply(lambda tags: subcategory in tags and access in tags)
    ]

def generate_workout_plan(subcategory, access, days_per_week, focus, weeks=4):
    filtered = filter_exercises(subcategory, access)
    if filtered.empty:
        return pd.DataFrame([{"Day": "N/A", "Workout": "No matching exercises found."}])
    exercises = filtered['Exercise'].tolist()
    random.shuffle(exercises)
    total_days = days_per_week * weeks
    rules = focus_rules.get(focus, {})
    workout_plan = []
    for day in range(total_days):
        daily = exercises[day % len(exercises):(day % len(exercises)) + 3]
        sets = rules.get("Number of sets", "?")
        reps = rules.get("Number of Reps", "?")
        rest = rules.get("Rest Times", "?")
        workout_plan.append({
            "Week": (day // days_per_week) + 1,
            "Day": f"Day {(day % days_per_week) + 1}",
            "Workout": ', '.join(daily),
            "Sets": sets,
            "Reps": reps,
            "Rest": rest
        })
    return pd.DataFrame(workout_plan)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    focus = data["focus"]
    raw_subcategory = data["subcategory"]
    access = data["access"]
    days = int(data["days"])

    if raw_subcategory == "full_body":
        raw_subcategory = "fullbody"
    if focus == "power":
        subcategory = "power"
    else:
        subcategory = f"{focus}_{raw_subcategory}"

    plan = generate_workout_plan(subcategory, access, days, focus)
    return jsonify(plan.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
