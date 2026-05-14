import json
import os
import time
from dataclasses import dataclass, asdict, field
from typing import List

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

QUIZ_FILE = os.path.join(DATA_DIR, 'quizzes.json')
RESULTS_FILE = os.path.join(DATA_DIR, 'results.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

@dataclass
class Question:
    prompt: str
    choices: List[str]
    answer: str
    points: float = 1

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return Question(
            prompt=data['prompt'],
            choices=data['choices'],
            answer=data['answer'],
            points=data.get('points', 1)
        )


@dataclass
class Quiz:
    title: str
    description: str
    timer: int
    questions: List[Question] = field(default_factory=list)

    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'timer': self.timer,
            'questions': [q.to_dict() for q in self.questions]
        }

    @staticmethod
    def from_dict(data):
        return Quiz(
            title=data['title'],
            description=data.get('description', ''),
            timer=data.get('timer', 60),
            questions=[Question.from_dict(q) for q in data.get('questions', [])]
        )


class QuizManager:

    def __init__(self):

        self.quizzes = []
        self.results = []
        self.users = {}

        self.load_quizzes()
        self.load_results()
        self.load_users()


    def load_quizzes(self):

        if os.path.exists(QUIZ_FILE):

            with open(QUIZ_FILE, 'r') as file:

                data = json.load(file)

                self.quizzes = [Quiz.from_dict(q) for q in data]


    def save_quizzes(self):

        with open(QUIZ_FILE, 'w') as file:

            json.dump(
                [q.to_dict() for q in self.quizzes],
                file,
                indent=4
            )


    def load_results(self):

        if os.path.exists(RESULTS_FILE):

            with open(RESULTS_FILE, 'r') as file:

                self.results = json.load(file)

    def save_results(self):

        with open(RESULTS_FILE, 'w') as file:

            json.dump(self.results, file, indent=4)


    def load_users(self):

        if os.path.exists(USERS_FILE):

            with open(USERS_FILE, 'r') as file:

                self.users = json.load(file)

        else:

            self.users = {
                "admin": {
                    "password": "admin123",
                    "role": "admin"
                }
            }

            self.save_users()

    def save_users(self):

        with open(USERS_FILE, 'w') as file:

            json.dump(self.users, file, indent=4)

    def register_user(self):

        username = input("Enter Username: ").strip()

        if username in self.users:

            print("User already exists.")
            return

        password = input("Enter Password: ").strip()

        self.users[username] = {
            "password": password,
            "role": "student"
        }

        self.save_users()

        print("User Registered Successfully!")

    def login(self):

        username = input("Username: ").strip()
        password = input("Password: ").strip()

        if username in self.users:

            if self.users[username]["password"] == password:

                print("Login Successful!")

                return username, self.users[username]["role"]

        print("Invalid Username or Password.")

        return None, None

    def add_quiz(self):

        title = input("Quiz Title: ")
        description = input("Quiz Description: ")

        timer = int(input("Enter Quiz Time (seconds): "))

        quiz = Quiz(title, description, timer)

        self.quizzes.append(quiz)

        self.save_quizzes()

        print("Quiz Added Successfully!")

    def delete_quiz(self):

        self.list_quizzes()

        choice = input("Enter Quiz Number to Delete: ")

        if not choice.isdigit():
            return

        index = int(choice) - 1

        if 0 <= index < len(self.quizzes):

            del self.quizzes[index]

            self.save_quizzes()

            print("Quiz Deleted Successfully!")


    def list_quizzes(self):

        if not self.quizzes:
            print("No quizzes available.")
            return

        print("\nAvailable Quizzes:")

        for idx, quiz in enumerate(self.quizzes, start=1):

            print(
                f"{idx}. {quiz.title} "
                f"({quiz.timer} sec)"
            )

    def add_question(self):

        self.list_quizzes()

        choice = input("Select Quiz Number: ")

        if not choice.isdigit():
            return
        index = int(choice) - 1

        if not (0 <= index < len(self.quizzes)):
            return
        prompt = input("Question: ")

        options = []

        while True:
            option = input(f"Option {len(options)+1}: ").strip()

            if option == "":
                break

            options.append(option)

        if len(options) < 2:
            print("At least 2 options are required.")
            return

        print("\nOptions:")

        for i, option in enumerate(options, start=1):
            print(f"{i}. {option}")

        answer_index = input("Correct Option Number: ")

        if not answer_index.isdigit():
            print("Invalid Input.")
            return

        answer_index = int(answer_index)

        if not (1 <= answer_index <= len(options)):
            print("Invalid Option Number.")
            return

        try:
            points = float(input("Points: "))

        except ValueError:

            print("Invalid Points.")
            return

        question = Question(
            prompt=prompt,
            choices=options,
            answer=options[answer_index - 1],
            points=points
        )

        self.quizzes[index].questions.append(question)

        self.save_quizzes()

        print("Question Added Successfully!")


    def take_quiz(self, username):

        if not self.quizzes:

            print("No quizzes available.")
            return

        self.list_quizzes()

        choice = input("Select Quiz Number: ")

        if not choice.isdigit():
            return

        index = int(choice) - 1

        if not (0 <= index < len(self.quizzes)):
            return

        quiz = self.quizzes[index]

        if not quiz.questions:
            print("This quiz has no questions.")
            return

        score = 0
        max_score = sum(q.points for q in quiz.questions)

        print(f"\nStarting Quiz: {quiz.title}")
        total_time = quiz.timer
        start_time = time.time()

        for q_no, question in enumerate(quiz.questions, start=1):
            elapsed = time.time() - start_time
            remaining = total_time - elapsed

            if remaining <= 0:
                print("\nTime Up!")
                break

            print(f"\nTime Remaining: {int(remaining)} seconds")

            print(f"\nQ{q_no}. {question.prompt}")

            for idx, option in enumerate(question.choices, start=1):
                print(f"{idx}. {option}")

            answer = input("Your Answer (or q to quit): ").strip()

            if answer.lower() == 'q':
                print("Quiz Exited.")
                break

            if answer.isdigit():
                selected = int(answer)

                if 1 <= selected <= len(question.choices):
                    selected_answer = question.choices[selected - 1]

                    if selected_answer == question.answer:
                        score += question.points
                        print("Correct!")

                    else:
                        print(
                            f"Wrong! Correct Answer: "
                            f"{question.answer}"
                        )

                else:
                    print("Invalid Option.")

            else:
                print("Invalid Input.")

        print(f"\nFinal Score: {score}/{max_score}")

        self.record_result(
            username,
            quiz.title,
            score,
            max_score
        )

    def record_result(
        self,
        username,
        quiz_title,
        score,
        max_score
    ):

        result = {
            "username": username,
            "quiz_title": quiz_title,
            "score": score,
            "max_score": max_score
        }

        self.results.append(result)
        self.save_results()
        print("Result Saved Successfully!")

    def view_results(self):

        if not self.results:
            print("No Results Found.")
            return

        print("\n===== RESULTS =====")

        for result in self.results:
            print(
                f"{result['username']} scored "
                f"{result['score']}/{result['max_score']} "
                f"in {result['quiz_title']}"
            )

def admin_panel(manager):

    while True:
        print("\n===== ADMIN PANEL =====")

        print("1. Add Quiz")
        print("2. Delete Quiz")
        print("3. Add Question")
        print("4. View Results")
        print("5. Logout")

        choice = input("Enter Choice: ")

        if choice == '1':
            manager.add_quiz()

        elif choice == '2':
            manager.delete_quiz()

        elif choice == '3':
            manager.add_question()

        elif choice == '4':
            manager.view_results()

        elif choice == '5':
            break

        else:
            print("Invalid Choice")

def student_panel(manager, username):

    while True:
        print(f"\n===== STUDENT PANEL ({username}) =====")

        print("1. Take Quiz")
        print("2. View Results")
        print("3. Logout")

        choice = input("Enter Choice: ")
        if choice == '1':
            manager.take_quiz(username)
        elif choice == '2':
            manager.view_results()
        elif choice == '3':
            break
        else:
            print("Invalid Choice")

def main():
    manager = QuizManager()

    while True:
        print("\n===== QUIZ MANAGEMENT SYSTEM =====")

        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter Choice: ")

        if choice == '1':
            manager.register_user()

        elif choice == '2':
            username, role = manager.login()

            if username:
                if role == "admin":
                    admin_panel(manager)

                else:
                    student_panel(manager, username)

        elif choice == '3':
            print("Quiz Management System Exited.")
            break

        else:
            print("Invalid Choice")

if __name__ == "__main__":
    main()