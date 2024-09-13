import os
import pandas as pd
from abc import ABC, abstractmethod
from register.routine_register import call_module
from datetime import datetime


class DaySelector:
    @staticmethod
    def get_valid_day():
        """Prompts the user to select a valid day of the week."""
        days_options = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        while True:
            selected_day = input("Select a day of the week: ").title()
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
    def __init__(self, split_name):
        self.dic_user_routine = {} 
        self.split_name = split_name

    def collect_muscle_groups_by_day(self, gym_days, predefined_groups = None):
        for i, day in enumerate(gym_days):
            if predefined_groups:
                muscle_group = predefined_groups[i]
                exercises = self.collect_exercises(muscle_group)
                self.dic_user_routine[day] = {
                "group": muscle_group,
                'exercises': exercises
                }
            else:
                print("\nFor each day, select the muscle group you want to train.")
                muscle_group = input(f"What will you train on {day}? ").title()
                exercises = self.collect_exercises(muscle_group)
                self.dic_user_routine[day] = {
                "group": muscle_group,
                'exercises': exercises
                }
        self.display_schedule()
        self.write_to_csv()
        user_routine = WorkoutTracker(self.split_name)
        user_routine.dic_user_routine = self.dic_user_routine
        user_routine.register()

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
        print("\nYour training schedule:")
        for day, details in self.dic_user_routine.items():
            print(f"{day}: {details['group']} - Exercises: {', '.join(details['exercises'])}")

    def write_to_csv(self):
        filename = f"{self.split_name}.csv"
        if os.path.exists(filename):
            os.remove(filename)
        
        data = []
        for day, details in self.dic_user_routine.items():
            data.append({
                "Day": day,
                "Muscle Group": details["group"],
                "Exercises": ", ".join(details["exercises"])
            })
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data has been written")

class CreateSplit:
    def __init__(self):
        self.split_name = ""
        self.gym_days = []  

    def create_custom_split(self):
        #Creates a new custom split and prompts for weekly days.
        new_split_name = input("Enter the name for the new split: ")  
        self.split_name = new_split_name
        print(f"Custom split '{new_split_name}' created.")

        self.gym_days = DaySelector.sorted_days()
        print(f"Custom split '{new_split_name}' includes the following days: {', '.join(self.gym_days)}")

        self.select_muscle_distribution()

    def select_muscle_distribution(self):
        #Collects muscle groups and exercises for the selected days.
        exercise_selector = SelectMuscleGroupsAndExercises(self.split_name)
        exercise_selector.collect_muscle_groups_by_day(self.gym_days)

class ArnoldSplit(SelectMuscleGroupsAndExercises):    
    def __init__(self):
        super().__init__("Arnold split")
        self.predefined_groups = ["Chest and back", "Arms and shoulders", "Leg", "Chest and back", "Arms and shoulders", "Leg"]
    
    def collect_muscle_groups_by_day(self, gym_days):
       super().collect_muscle_groups_by_day(gym_days, predefined_groups = self.predefined_groups)

class PplSplit(SelectMuscleGroupsAndExercises):    
    def __init__(self):
        super().__init__("PPL")
        self.predefined_groups = ["Chest, triceps and shoulders", "Back, biceps and forearms", "Leg", "Chest, triceps and shoulders", "Back, biceps and forearms", "Leg"]
    
    def collect_muscle_groups_by_day(self, gym_days):
       super().collect_muscle_groups_by_day(gym_days, predefined_groups = self.predefined_groups)


class MainMenu:
    def __init__(self):
        self.splits = {
            1: ("Push, Pull, Legs", PplSplit),
            2: ("Arnold split", ArnoldSplit),
            3: ("Personalized split", CreateSplit),
            4: ("Access your routines", AccessUserRoutine),
            5: ("Exit", None)
        }
        self.default_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
       
    def start(self):
        """Displays the main menu and handles user input."""
        print("\nWelcome to the fitness tracker\nSelect an option\n")
        
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
                        elif user_choice == 4:
                            instance = split_class()
                            instance.access_routine()  
                    else:   
                        print("Thanks for using the fitness tracker. Goodbye!")
                    break  
                else:
                    print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

class AccessUserRoutine():
    def access_routine(self):
        User_routine_name = input(f"Introduce the name of your routine/split: ").title()
        file = f"{User_routine_name}.csv"
        if os.path.isfile(file):
            try:
                user_routine = WorkoutTracker(User_routine_name)
                user_routine.dic_user_routine = self.load_routine(file)
                user_routine.register()
            except pd.errors.EmptyDataError:
                print("The file is empty.")
            except pd.errors.ParserError:
                print("Cannot parse file.")
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("Cannot find file or routine does not exist.")
            return_main_menu = MainMenu()
            return_main_menu.start()

    def load_routine(self, file):
        """Loads routine data from CSV file."""
        try:
            df = pd.read_csv(file)
            routine_data = {}
            for _, row in df.iterrows():
                day = row['Day']
                routine_data[day] = {
                    'group': row['Muscle Group'],
                    'exercises': row['Exercises'].split(', ')
                }
            return routine_data
        except Exception as e:
            print(f"Error loading routine: {e}")
            return {}

                      
class WorkoutTracker(SelectMuscleGroupsAndExercises):
    def __init__(self, split_name):
        super().__init__(split_name)
        self.dic_user_routine = {}
        self.sorted_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
   
    
    def register(self):
        today_date = datetime.now().strftime("%Y-%m-%d")
        today_weekday = datetime.now().weekday()
        today_day = self.sorted_days[today_weekday]
        
        muscle_group = self.dic_user_routine.get(today_day, {}).get("group", "rest")
        
        if muscle_group ==  "rest":
            print(f"\nToday is rest day")
            return_main_menu = MainMenu()
            return return_main_menu.start()
        else:   
            print(f"Today is {muscle_group} day.")
       
            user_register = input(f"\nDo you want to register todays routine ({today_date})? (yes/no): ").lower()
            if user_register == "yes":
                try: 
                    call_module(self.split_name, muscle_group)
                except Exception as e:
                    print(f"Error : {e}")
            else:
                user_routines = input("Do you want to modify your routine? (yes/no): ").lower()
                if user_routines == "yes":
                    self.modify_routine()
                else:
                    return_main_menu = MainMenu()
                    return return_main_menu.start()
            
    def modify_routine(self): 
        if not self.dic_user_routine:
            print("No routine available to modify, add a new routine.")
            return_main_menu = MainMenu()
            return return_main_menu.start() 
        
        actions = ["add a day", "remove day", "modify a day"]
        
        for i,action in enumerate(actions, start=1):
            print(f"{i}: {action}")
            
        while True:
            try:
                user_modify_option = int(input("\nIntroduce the number of the action you want to do: "))
                if 1 <= user_modify_option <= 3: 
                    break
                else:
                    print("please introduce a number bewtween 1-3")
            except ValueError:
                print("please introduce a valid number")
        
        #add day 
        if user_modify_option == 1:
            print("\nCurrent routine:")
            self.display_schedule()
            
            while True:
                add_day = DaySelector.get_valid_day()
                if add_day in self.dic_user_routine:
                    print("This day was already selected, please introduce other day.")
                    continue
                else:
                    new_muscle_group = input(f"Enter the new muscle group for {add_day}: ").title()
                    new_exercises = self.collect_exercises(new_muscle_group)

                    self.dic_user_routine[add_day] = {
                        'group': new_muscle_group,
                        'exercises': new_exercises
                    }
                    self.write_to_csv()
                    self.display_schedule()
                    self.register()
                break
     
        #remove day
        elif user_modify_option == 2:
            print("\nCurrent routine:")
            self.display_schedule()

            while True:
                remove_days = [day.strip().title() for day in input("Enter the days you want to remove, separated by commas: ").split(",")]
                if all(day in self.dic_user_routine for day in remove_days):
                    for day in remove_days:
                        if day in self.dic_user_routine:
                            del self.dic_user_routine[day]

                    self.write_to_csv()
                    self.display_schedule()
                    self.register()
                    break
                else:
                    print(f"Some of the days you entered are not in the routine. Please check and try again.")

        #modify a day 
        elif user_modify_option == 3:
            print("\nCurrent routine:")
            self.display_schedule()

            while True: 
                day_to_modify = input("Enter the day you want to modify: ").title()
                if day_to_modify not in self.dic_user_routine:
                    print(f"No routine found for {day_to_modify}.")
                else:
                    new_muscle_group = input(f"Enter the new muscle group for {day_to_modify}: ").title()
                    new_exercises = self.collect_exercises(new_muscle_group)

                    self.dic_user_routine[day_to_modify] = {
                        'group': new_muscle_group,
                        'exercises': new_exercises
                    }

                    self.write_to_csv()
                    self.display_schedule()
                    self.register()
                break
            

        
if __name__ == "__main__":
    menu = MainMenu()
    menu.start()
