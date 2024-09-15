import os
import pandas as pd
from abc import ABC, abstractmethod
from datetime import datetime
from register.routine_register import call_module

class DaySelector:
    DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    @staticmethod
    def get_valid_day():
        """Prompts the user to select a valid day of the week."""
        while True:
            selected_day = input("Select a day of the week: ").title()
            if selected_day in DaySelector.DAYS_OF_WEEK:
                return selected_day
            print("Please select a valid day.")

    @staticmethod
    def sorted_days():
        """Prompts the user for the number of gym days and returns a sorted list of unique days."""
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
                    return list(sorted(unique_days, key=DaySelector.DAYS_OF_WEEK.index))
                print("Please enter a number between 1 and 7.")
            except ValueError:
                print("Please enter a valid number.")


class RoutineManager(ABC):
    def __init__(self, split_name):
        self.dic_user_routine = {}
        self.split_name = split_name

    @abstractmethod
    def collect_muscle_groups_by_day(self, gym_days):
        """Collect muscle groups and exercises for each day."""
        pass

    def collect_exercises(self, muscle_group):
        """Collect exercises for a given muscle group."""
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

        data = [{
            "Day": day,
            "Muscle Group": details["group"],
            "Exercises": ", ".join(details["exercises"])
        } for day, details in self.dic_user_routine.items()]

        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data has been written to {filename}")


class CustomSplit(RoutineManager):
    def __init__(self):
        super().__init__("Custom split")

    def collect_muscle_groups_by_day(self, gym_days, predefined_groups=None):
        for i, day in enumerate(gym_days):
            if predefined_groups:
                muscle_group = predefined_groups[i]
            else:
                print("\nFor each day, select the muscle group you want to train.")
                muscle_group = input(f"What will you train on {day}? ").title()
            exercises = self.collect_exercises(muscle_group)
            self.dic_user_routine[day] = {"group": muscle_group, 'exercises': exercises}
        self.display_schedule()
        self.write_to_csv()
        WorkoutTracker(self.split_name, self.dic_user_routine).register()


class ArnoldSplit(RoutineManager):
    def __init__(self):
        predefined_groups = ["Chest and back", "Arms and shoulders", "Leg", "Chest and back", "Arms and shoulders", "Leg"]
        super().__init__("Arnold split")
        self.predefined_groups = predefined_groups

    def collect_muscle_groups_by_day(self, gym_days):
        super().collect_muscle_groups_by_day(gym_days, predefined_groups=self.predefined_groups)


class PplSplit(RoutineManager):
    def __init__(self):
        predefined_groups = ["Chest, triceps and shoulders", "Back, biceps and forearms", "Leg", "Chest, triceps and shoulders", "Back, biceps and forearms", "Leg"]
        super().__init__("PPL")
        self.predefined_groups = predefined_groups

    def collect_muscle_groups_by_day(self, gym_days):
        super().collect_muscle_groups_by_day(gym_days, predefined_groups=self.predefined_groups)


class MainMenu:
    def __init__(self):
        self.splits = {
            1: ("Push, Pull, Legs", PplSplit),
            2: ("Arnold split", ArnoldSplit),
            3: ("Personalized split", CustomSplit),
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
                        instance = split_class()
                        if user_choice in [1, 2]:
                            instance.collect_muscle_groups_by_day(self.default_days)
                        elif user_choice == 3:
                            instance.create_custom_split()
                        elif user_choice == 4:
                            instance.access_routine()
                    else:
                        print("Thanks for using the fitness tracker. Goodbye!")
                    break
                else:
                    print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")


class AccessUserRoutine:
    def access_routine(self):
        user_routine_name = input(f"Introduce the name of your routine/split: ").title()
        file = f"{user_routine_name}.csv"
        if os.path.isfile(file):
            try:
                user_routine = WorkoutTracker(user_routine_name)
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
            MainMenu().start()

    def load_routine(self, file):
        """Loads routine data from CSV file."""
        try:
            df = pd.read_csv(file)
            routine_data = {
                row['Day']: {
                    'group': row['Muscle Group'],
                    'exercises': row['Exercises'].split(', ')
                } for _, row in df.iterrows()
            }
            return routine_data
        except Exception as e:
            print(f"Error loading routine: {e}")
            return {}

class WorkoutTracker(RoutineManager):
    def __init__(self, split_name):
        super().__init__(split_name)
        self.dic_user_routine = {}
        self.sorted_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
    def collect_muscle_groups_by_day(self, gym_days, predefined_groups=None):
        pass

    def register(self):
        today_date = datetime.now().strftime("%Y-%m-%d")
        today_weekday = datetime.now().weekday()
        today_day = self.sorted_days[today_weekday]

        muscle_group = self.dic_user_routine.get(today_day, {}).get("group", "rest")

        if muscle_group == "rest":
            modify = input("Today is rest day, Do you want to modify your routine? (yes/no): ")
            if modify == "yes":
                self.modify_routine()
            else:
                return MainMenu().start()
        else:
            print(f"Today is {muscle_group} day.")
            user_register = input(f"\nDo you want to register today's routine ({today_date})? (yes/no): ").lower()
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
                    MainMenu().start()

    def modify_routine(self):
        if not self.dic_user_routine:
            print("No routine available to modify, add a new routine.")
            MainMenu().start()

        actions = ["add a day", "remove day", "modify a day"]
        for i, action in enumerate(actions, start=1):
            print(f"{i}: {action}")

        while True:
            try:
                user_modify_option = int(input("\nIntroduce the number of the action you want to do: "))
                if 1 <= user_modify_option <= 3:
                    break
                else:
                    print("Please introduce a number between 1-3")
            except ValueError:
                print("Please introduce a valid number")

        if user_modify_option == 1:
            self.add_day()
        elif user_modify_option == 2:
            self.remove_day()
        elif user_modify_option == 3:
            self.modify_day()

    def add_day(self):
        print("\nCurrent routine:")
        self.display_schedule()

        while True:
            add_day = DaySelector.get_valid_day()
            if add_day in self.dic_user_routine:
                print("This day was already selected, please introduce another day.")
                continue
            else:
                new_muscle_group = input(f"Enter the new muscle group for {add_day}: ").title()
                new_exercises = self.collect_exercises(new_muscle_group)
                self.dic_user_routine[add_day] = {'group': new_muscle_group, 'exercises': new_exercises}
                self.write_to_csv()
                self.display_schedule()
                self.register()
            break

    def remove_day(self):
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
                print("Some of the days you entered are not in the routine. Please check and try again.")

    def modify_day(self):
        print("\nCurrent routine:")
        self.display_schedule()

        while True:
            day_to_modify = input("Enter the day you want to modify: ").title()
            if day_to_modify not in self.dic_user_routine:
                print(f"No routine found for {day_to_modify}.")
            else:
                new_muscle_group = input(f"Enter the new muscle group for {day_to_modify}: ").title()
                new_exercises = self.collect_exercises(new_muscle_group)
                self.dic_user_routine[day_to_modify] = {'group': new_muscle_group, 'exercises': new_exercises}
                self.write_to_csv()
                self.display_schedule()
                self.register()
            break


if __name__ == "__main__":
    MainMenu().start()
