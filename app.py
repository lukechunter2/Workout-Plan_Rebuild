
from flask import Flask, request, jsonify, render_template
import pandas as pd
import random
import json

app = Flask(__name__)

df_tags = pd.read_pickle('exercise_tags.pkl')
with open('full_focus_rules.json') as f:
    focus_rules = json.load(f)

def filter_exercises(category, access):
    return df_tags[
        df_tags['Category'].apply(lambda tags: category in tags and access in tags)
    ]

def generate_workout_plan(category, access, days_per_week, focus, weeks=4):
    filtered = filter_exercises(category, access)
    if filtered.empty:
        return pd.DataFrame([{"Day": "N/A", "Workout": "No matching exercises found."}])

    exercises = filtered['Exercise'].tolist()
    random.shuffle(exercises)
    total_days = days_per_week * weeks
    rules = focus_rules.get(focus.lower(), {})
    workout_plan = []

    for day in range(total_days):
        daily = exercises[day % len(exercises):(day % len(exercises)) + 3]
        sets = rules.get('Number of sets', '?')
        reps = rules.get('Number of Reps', '?')
        rest = rules.get('Rest Times', '?')
        workout_plan.append({
            "Week": (day // days_per_week) + 1,
            "Day": f"Day {(day % days_per_week) + 1}",
            "Workout": ', '.join(daily),
            "Sets": sets,
            "Reps": reps,
            "Rest": rest
        })
    return pd.DataFrame(workout_plan)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    focus = data['focus'].capitalize()  # e.g., Strength
    raw_subcategory = data['subcategory'].replace('_', ' ')  # e.g., upper_body → upper body
    access = data['access'].replace('access_', '').capitalize()  # access_low → Low
    days = int(data['days'])

    if focus == "Power":
        category = "Power"
    elif focus == "Endurance" and raw_subcategory in ["aerobic", "anaerobic"]:
        category = f"Endurance-{raw_subcategory.capitalize()}"
    elif focus == "Endurance":
        category = "Endurance-Muscular"
    else:
        body_map = {
            "upper body": "Upper Body",
            "lower body": "Lower Body",
            "fullbody": "Full Body"
        }
        clean = body_map.get(raw_subcategory, raw_subcategory.capitalize())
        category = f"{focus}-{clean}"

    plan = generate_workout_plan(category, access, days, focus)
    return jsonify(plan.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
