import pandas as pd
import os

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
    
    for day, exercises in exercises_dict.items():
        for exercise in exercises:
            print(f"\nRegistering data for the exercise {exercise} on {day}: ")
            
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
                        weight = float(input(f"Weight used in set {i}: "))
                        if weight < 0.5:
                            print("Please enter a valid weight.")
                            continue
                        break
                    except ValueError:
                        print("Please enter a valid number.")
                
                data.append({
                    'Day': day,
                    'Exercise': exercise,
                    'Set': i,
                    'Reps': reps,
                    'Weight': weight
                })
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data registered")
   

if __name__ == "__main__":

    split_filename = '/Users/nicolasdominguez/Desktop/Graficos proyecto/split.csv'
    workouts_filename = '/Users/nicolasdominguez/Desktop/Graficos proyecto/register/workouts.csv'

    split_data = load_exercises(split_filename)
    if split_data is not None:
        exercises_dict = get_exercises(split_data)
        workout_register(exercises_dict, workouts_filename)
