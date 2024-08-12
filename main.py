import os
import pandas as pd
from abc import ABC, abstractmethod

class DaySelector:
    @staticmethod
    def get_valid_day():
        """Prompts the user to select a valid day of the week."""
        days_options = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        while True:
            selected_day = input("Select a day of the week: ").capitalize()
            if selected_day in days_options:
                return selected_day
            print("Please select a valid day.")

    @staticmethod
    def sorted_days():
        days_options = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        while True:
            try:
                user_split_week = int(input("How many days a week will you go to the gym?: "))
                if 1 <= user_split_week <= 7:
                    unique_days = set()
                    while len(unique_days) < user_split_week:
                        day = DaySelector.get_valid_day()
                        if day in unique_days:
                            print(f"The day '{day}' has already been selected. Please choose a different day.")
                        else:
                            unique_days.add(day)
                    return list(sorted(unique_days, key=days_options.index))
                print("Please enter a number between 1 and 7.")
            except ValueError:
                print("Please enter a valid number.")

class SelectMuscleGroupsAndExercises(ABC):
    def __init__(self):
        self.muscular_groups_by_day = {}

    def collect_muscle_groups_by_day(self, days_gym):
        add_exercise = input("Do you want to add exercises?(yes/no): ")
        if add_exercise == "yes":
            print("\nFor each day, select the muscular group you want to train:")
            for day in days_gym:
                muscular_group = input(f"What will you train on {day}? ").capitalize()
                exercises = self.collect_exercises(muscular_group)
                self.muscular_groups_by_day[day] = {
                    'group': muscular_group,
                    'exercises': exercises
                }
            self.display_schedule()
            self.write_to_csv()
        else:
            filename = 'split.csv'
        
            if os.path.exists(filename):
                os.remove(filename)
        
            data = []
            for day, details in self.muscular_groups_by_day.items():
                data.append({
                'Day': day,
                'Muscle Group': details['group'],
                })
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            print(f"Data has been written to {filename}")
            return_main = MainMenu()
            return_main.start()

    def collect_exercises(self, group):
        print(f"\nEnter exercises for {group} (type 'done' when finished):")
        exercises = []
        while True:
            exercise = input("Enter an exercise: ")
            if exercise.lower() == 'done':
                break
            if exercise:
                exercises.append(exercise)
            else:
                print("Exercise cannot be empty. Please enter a valid exercise.")
        return exercises

    def display_schedule(self):
        print("\nYour training schedule:")
        for day, details in self.muscular_groups_by_day.items():
            print(f"{day}: {details['group']} - Exercises: {', '.join(details['exercises'])}")
        
            
    def write_to_csv(self):
        filename = 'split.csv'
        # Remove the file if it already exists
        if os.path.exists(filename):
            os.remove(filename)
        
        data = []
        for day, details in self.muscular_groups_by_day.items():
            data.append({
                'Day': day,
                'Muscle Group': details['group'],
                'Exercises': ', '.join(details['exercises'])
            })
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data has been written to {filename}")

class CreateSplit:
    def __init__(self):
        self.name_split = []
        self.days_gym = []

    def create_custom_split(self):
        """Creates a new custom split and prompts for weekly days."""
        new_split = input("Enter the name for the new split: ")
        self.name_split.append(new_split)
        print(f"Custom split '{new_split}' created.")

        self.days_gym = DaySelector.sorted_days()
        print(f"Custom split '{new_split}' includes the following days: {', '.join(self.days_gym)}")

        self.select_muscle_distribution()

    def select_muscle_distribution(self):
        current_exercises = SelectMuscleGroupsAndExercises()
        current_exercises.collect_muscle_groups_by_day(self.days_gym)

class ArnoldSplit(SelectMuscleGroupsAndExercises):    
    pass  

class PplSplit(SelectMuscleGroupsAndExercises):    
    pass  


class MainMenu:
    def __init__(self):
        self.splits = {
            1: ("Push, Pull, Legs", PplSplit),
            2: ("Arnold split", ArnoldSplit),
            3: ("Personalized split", CreateSplit),
            4: ("Exit", None)
        }
        self.days_gym_ppl_and_arnoldSplit = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    def start(self):
        print("\nWelcome to the fitness tracker\nSelect your split please\n")
        
        for i, (name, _) in self.splits.items():
            print(f"{i}: {name}")

        while True:
            try:
                user_split = int(input("Enter the number of your choice: "))
                if user_split in self.splits:
                    split_name, split_class = self.splits[user_split]
                    if split_class:
                        if user_split in [1, 2]:
                            instance = split_class()
                            instance.collect_muscle_groups_by_day(self.days_gym_ppl_and_arnoldSplit)
                        elif user_split == 3:
                         instance = split_class()
                         instance.create_custom_split()
                    else:   
                        print("Thanks for using the fitness tracker. Goodbye!")
                    return  # Ends the program
                else:
                    print("Please enter a number between 1 and 4.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

if __name__ == "__main__":
    menu = MainMenu()
    menu.start()

