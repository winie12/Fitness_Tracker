import pandas as pd
import os
from datetime import datetime

def load_exercises(filename):
    try:
        df = pd.read_csv(filename)
        return df
    except FileNotFoundError:
        print(f"El archivo '{filename}' no se encuentra.")
    except pd.errors.EmptyDataError:
        print(f"El archivo '{filename}' está vacío.")
    except pd.errors.ParserError:
        print(f"Error al analizar el archivo '{filename}'.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

def get_exercises(dataframe):

    exercises_dict = {}
    for _, row in dataframe.iterrows():
        day = row['Day']
        exercises = row['Exercises'].split(', ') 
        exercises_dict[day] = exercises
    return exercises_dict

def workout_register(exercises_dict, filename):
    data = []
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    
    for exercise in exercises_dict.get(today_date, []):
        print(f"\nRegistering data for the exercise {exercise} on {today_date}: ")
        
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
                    reps = int(input(f"How many reps did you do in set {i}?: "))
                    if reps < 0:
                        print("Please enter a number greater than 0.")
                        continue
                    weight = float(input(f"Weight used in set {i} (kg): "))
                    if weight < 0.5:
                            print("Please enter a valid weight.")
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
    df.to_csv(filename, mode="a", header=True, index=False)
    print(f"Data registered")


def User_stats(filename):
    try:
        df = pd.read_csv(filename)
        
        if "Weight" not in df.columns or "Reps" not in df.columns:
            print("El archivo no contiene las columnas necesarias.")
            return
    
        stats = {
            "max weight lift" : df["Weight"].max(),
            "max reps made" : df["Reps"].max()
        }
    
        print("\nThese are your current gym marks: ")
        for key, value in stats.items():
            print(f"{key}: {value} kg" if key == "max weight lift" else f"{key}: {value}" )
    except FileExistsError:
        print("File does not exist")
    except pd.errors.EmptyDataError:
        print("The file is empty")
    except pd.errors.ParserError:
        print("Can not parse file ")
    except Exception as e:
        print(f"An error occurred: {e}")



def call_module(split_name, muscle_group):
    
    split_filename = f'/Users/nicolasdominguez/Desktop/Fitness_tracker_2.0/{split_name}.csv'
    workouts_filename = f'{split_name}_workouts.csv'
    split_data = load_exercises(split_filename)
        
    if split_data is not None:
        exercises_dict = {day: details['exercises'] for day, details in split_data.items() if details['group'] == muscle_group}
        workout_register(exercises_dict, workouts_filename)
        
    User_gym_marks = input("Do you want to see your currect gym marks? (yes/no): ")
    if User_gym_marks == "yes":
        return User_stats(workouts_filename)
    else:
        return "Thanks for register your data."
