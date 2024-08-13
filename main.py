import os
import pandas as pd
from abc import ABC, abstractmethod
import register.routine_register as stats

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
        """Prompts the user for the number of gym days and returns a sorted list of unique days."""
        days_options = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        while True:
            try:
                number_of_days = int(input("How many days a week will you go to the gym?: "))
                if 1 <= number_of_days <= 7:
                    unique_days = set()
                    while len(unique_days) < number_of_days:
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
        self.muscle_groups_by_day = {} 

    def collect_muscle_groups_by_day(self, gym_days):
        print("\nFor each day, select the muscle group you want to train:")
        for day in gym_days:
                muscle_group = input(f"What will you train on {day}? ").capitalize()
                exercises = self.collect_exercises(muscle_group)
                self.muscle_groups_by_day[day] = {
                    'group': muscle_group,
                    'exercises': exercises
                }
        self.display_schedule()
        self.write_to_csv()
        User_rutine = UserRoutine()
        User_rutine.register()

    def collect_exercises(self, muscle_group):
        """Collects exercises for a given muscle group."""
        print(f"\nEnter exercises for {muscle_group} (type 'done' when finished):")
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
        """Displays the training schedule."""
        print("\nYour training schedule:")
        for day, details in self.muscle_groups_by_day.items():
            print(f"{day}: {details['group']} - Exercises: {', '.join(details['exercises'])}")

    def write_to_csv(self):
        """Writes the training schedule to a CSV file."""
        filename = 'split.csv'
        if os.path.exists(filename):
            os.remove(filename)
        
        data = []
        for day, details in self.muscle_groups_by_day.items():
            data.append({
                'Day': day,
                'Muscle Group': details['group'],
                'Exercises': ', '.join(details['exercises'])
            })
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data has been written")

class CreateSplit:
    def __init__(self):
        self.split_names = [] 
        self.gym_days = []  

    def create_custom_split(self):
        """Creates a new custom split and prompts for weekly days."""
        new_split_name = input("Enter the name for the new split: ")  
        self.split_names.append(new_split_name)
        print(f"Custom split '{new_split_name}' created.")

        self.gym_days = DaySelector.sorted_days()
        print(f"Custom split '{new_split_name}' includes the following days: {', '.join(self.gym_days)}")

        self.select_muscle_distribution()

    def select_muscle_distribution(self):
        """Collects muscle groups and exercises for the selected days."""
        exercise_selector = SelectMuscleGroupsAndExercises()
        exercise_selector.collect_muscle_groups_by_day(self.gym_days)

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
        self.default_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]  

    def start(self):
        """Displays the main menu and handles user input."""
        print("\nWelcome to the fitness tracker\nSelect your split please\n")
        
        for i, (name, _) in self.splits.items():
            print(f"{i}: {name}")

        while True:
            try:
                user_choice = int(input("Enter the number of your choice: "))  
                if user_choice in self.splits:
                    split_name, split_class = self.splits[user_choice]
                    if split_class:
                        if user_choice in [1, 2]:
                            instance = split_class()
                            instance.collect_muscle_groups_by_day(self.default_days)  
                        elif user_choice == 3:
                            instance = split_class()
                            instance.create_custom_split()
                    else:   
                        print("Thanks for using the fitness tracker. Goodbye!")
                    return  
                else:
                    print("Please enter a number between 1 and 4.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
                
            
class UserRoutine(SelectMuscleGroupsAndExercises):
    def __init__(self):
        super().__init__()
        self.muscle_groups_by_day = {}

    
    def register(self):
        user_register = input("Do you want to register your last workouts? (yes/no): ").lower()
        if user_register == "yes":
            stats.call_module()
        else:
            user_routines = input("Do you want to modify your routine? (yes/no): ").lower()
            if user_routines == "yes":
                self.modify_routine()
            else:
                return_main_menu = MainMenu()
                return_main_menu.start()
            
    def modify_routine(self): 
        """Allows the user to modify the existing routine."""
        if not self.muscle_groups_by_day:
            print("No routine available to modify, add a new routine.")
            return_main_menu = MainMenu()
            return return_main_menu.start()

        print("\nCurrent routine:")
        self.display_schedule()

        while True: 
            day_to_modify = input("Enter the day you want to modify: ").capitalize()
            if day_to_modify not in self.muscle_groups_by_day:
                print(f"No routine found for {day_to_modify}.")
            break


        new_muscle_group = input(f"Enter the new muscle group for {day_to_modify}: ").capitalize()
        new_exercises = self.collect_exercises(new_muscle_group)

        self.muscle_groups_by_day[day_to_modify] = {
            'group': new_muscle_group,
            'exercises': new_exercises
        }
        
        self.display_schedule()
        self.write_to_csv()
        self.register()
    
if __name__ == "__main__":
    menu = MainMenu()
    menu.start()
