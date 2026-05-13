import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from flask import Flask, render_template, request
import pandas as pd
import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
from datetime import datetime

from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

app = Flask(__name__)


class NutritionAnalyzer:

    def calculate_bmi(self, weight, height_cm):
        height_m = height_cm / 100
        bmi = weight / (height_m ** 2)
        return round(bmi, 2)

    def bmi_category(self, bmi):
        if bmi < 19.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    def calculate_calories(self, gender, weight, height, age, activity):

        if gender == "Male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        activity_levels = {
            "Low": 1.2,
            "Moderate": 1.55,
            "High": 1.9
        }

        calories = bmr * activity_levels[activity]
        return round(calories)

    def calculate_macros(self, calories, goal):

        if goal == "Lose Weight":
            calories -= 300

        elif goal == "Gain Weight":
            calories += 400

        protein = round((calories * 0.30) / 4)
        carbs = round((calories * 0.45) / 4)
        fats = round((calories * 0.25) / 9)

        return calories, protein, carbs, fats

    def water_intake(self, weight):
        return round(weight * 0.035, 2)


analyzer = NutritionAnalyzer()


@app.route('/', methods=['GET', 'POST'])
def home():

    result = None

    if request.method == 'POST':

        name = request.form['name']
        age = int(request.form['age'])
        weight = float(request.form['weight'])
        height = float(request.form['height'])
        gender = request.form['gender']
        activity = request.form['activity']
        goal = request.form['goal']

        bmi = analyzer.calculate_bmi(weight, height)
        category = analyzer.bmi_category(bmi)

        calories = analyzer.calculate_calories(
            gender,
            weight,
            height,
            age,
            activity
        )

        calories, protein, carbs, fats = analyzer.calculate_macros(calories, goal)

        water = analyzer.water_intake(weight)

        result = {
            'name': name,
            'bmi': bmi,
            'category': category,
            'calories': calories,
            'protein': protein,
            'carbs': carbs,
            'fats': fats,
            'water': water
        }

        save_data(result)
        generate_graphs(protein, carbs, fats, bmi)

    return render_template('index.html', result=result)


def save_data(result):

    row = pd.DataFrame([{
        'Time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Name': result['name'],
        'BMI': result['bmi'],
        'Calories': result['calories']
    }])

    try:
        old = pd.read_csv('nutrition_history.csv')
        row = pd.concat([old, row], ignore_index=True)

    except FileNotFoundError:
        pass

    row.to_csv('nutrition_history.csv', index=False)


def generate_graphs(protein, carbs, fats, bmi):

    os.makedirs('static/graphs', exist_ok=True)

    plt.figure(figsize=(5, 5))

    plt.pie(
        [protein, carbs, fats],
        labels=['Protein', 'Carbs', 'Fats'],
        autopct='%1.1f%%'
    )

    plt.title('Macronutrient Distribution')

    plt.savefig('static/graphs/macros.png')

    plt.close()

    plt.figure(figsize=(5, 5))

    plt.bar(['BMI'], [bmi])

    plt.axhline(18.5)
    plt.axhline(25)
    plt.axhline(30)

    plt.title('BMI Analysis')

    plt.savefig('static/graphs/bmi.png')

    plt.close()


if __name__ == '__main__':
    app.run(debug=True)