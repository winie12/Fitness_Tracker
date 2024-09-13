import pandas as pd
import os
from datetime import datetime

def load_exercises(filename):
    """Loads exercises from a CSV file."""
    try:
        df = pd.read_csv(filename)
        return df
    except FileNotFoundError:
        print(f"The file '{filename}' was not found.")
    except pd.errors.EmptyDataError:
        print(f"The file '{filename}' is empty.")
    except pd.errors.ParserError:
        print(f"Error parsing the file '{filename}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_exercises(dataframe):
    exercise_dict = {}
    for _, row in dataframe.iterrows():
        day = row['Day']
        exercise_dict[day] = {
        'group': row['Muscle Group'],
        'exercises': row['Exercises'].split(', ')
        }
    return exercise_dict


def workout_register(exercises_dict, filename):
    data = []
    sorted_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    today_weekday = datetime.now().weekday()
    today_day = sorted_days[today_weekday]
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    muscle_group = exercises_dict.get(today_day, {}).get("group", "rest")
    
    if muscle_group == "rest":
        print(f"Today {today_date} is a rest day.")
        return 
    
    if today_day in exercises_dict:
        datos = exercises_dict[today_day]
        exercises = datos["exercises"]
        
        print(f'Day: {today_day}')
        print(f'Muscle group: {datos["group"]}')
        
        for exercise in exercises:
            print(f"What did you do for {exercise} on {today_date}?")
            
            while True:
                try:
                    sets = int(input("Number of sets: "))
                    if sets <= 0:
                        print("Please enter a number greater than 0.")
                        continue
                    break
                except ValueError:
                    print("Please enter a valid number.")
            
            for i in range(1, sets + 1):
                while True:
                    try:
                        weight = float(input(f"Weight used in set {i} (kg): "))
                        if weight < 0.5:
                            print("Please enter a valid weight.")
                            continue
                        reps = int(input(f"How many reps did you do in set {i}?: "))
                        if reps < 0:
                            print("Please enter a number greater than 0.")
                            continue
                        break
                    except ValueError:
                        print("Please enter a valid number.")
                
                data.append({
                    'Date': today_date,
                    'Exercise': exercise,
                    'Set': i,
                    'Reps': reps,
                    'Weight': weight
                })
    
    df = pd.DataFrame(data)
    
    if not os.path.isfile(filename):
        df.to_csv(filename, mode="w", header=False, index=False)
    else:
        df.to_csv(filename, mode="a", header=False, index=False)
    
    print("Data registered successfully.")



def user_stats(filename):
    while True:
        try:
            df = pd.read_csv(filename)
        
            if "Exercise" not in df.columns or "Weight" not in df.columns or "Reps" not in df.columns:
                print("The file does not contain the required columns.")
                break

            exercise_stat = input("Introduce the exercise you want to check: ").lower()
            df['Exercise'] = df['Exercise'].str.lower()

            if exercise_stat not in df['Exercise'].values:
                print(f"Cannot find {exercise_stat}. Please try again.")
                continue

            exercise_data = df[df['Exercise'] == exercise_stat]
        
            max_weight = exercise_data["Weight"].max()
            max_reps = exercise_data[exercise_data["Weight"] == max_weight]["Reps"].max()

            print("\nThese are your current gym marks for the exercise '{}':".format(exercise_stat))
            print(f"Max weight lifted: {max_weight} kg")
            print(f"Reps with max weight: {max_reps}")

            break

        except FileNotFoundError:
            print("File does not exist.")
            break
        except pd.errors.EmptyDataError:
            print("The file is empty.")
            break
        except pd.errors.ParserError:
            print("Cannot parse file.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break


def call_module(split_name, muscle_group):
    workouts_filename = "/Users/nicolasdominguez/Desktop/Fitness_tracker_2.0/register/workouts.csv"
    split_filename = f"/Users/nicolasdominguez/Desktop/Fitness_tracker_2.0/{split_name}.csv"
    split_data = load_exercises(split_filename)
    
    if split_data is not None:
        exercises_dict = get_exercises(split_data)
        workout_register(exercises_dict, workouts_filename)
    
    user_gym_marks = input("Do you want to see your current gym marks? (yes/no): ").lower()
    if user_gym_marks == "yes":
        user_stats(workouts_filename)
    else:
        print("Thanks for registering your data.")
    
