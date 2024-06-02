from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from plyer import filechooser, email

class WorkoutApp(App):
    def build(self):
        self.workout_data = []

        self.exercises_dict = {
            'Грудь': ['Жим лежа', 'Разводка гантелей', 'Отжимания'],
            'Спина': ['Тяга верхнего блока', 'Тяга гантели', 'Подтягивания'],
            'Ноги': ['Приседания', 'Выпады', 'Становая тяга'],
            'Плечи': ['Жим гантелей сидя', 'Разведение гантелей в стороны', 'Тяга штанги к подбородку'],
            'Руки': ['Сгибание рук с гантелями', 'Разгибание рук на блоке', 'Подъемы на бицепс со штангой']
        }

        self.main_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.muscle_group_spinner = Spinner(
            text='Выберите группу мышц',
            values=tuple(self.exercises_dict.keys()),
            size_hint=(1, None),
            height=44
        )
        self.muscle_group_spinner.bind(text=self.update_exercise_spinner)
        self.main_layout.add_widget(self.muscle_group_spinner)

        self.exercise_spinner = Spinner(
            text='Выберите упражнение',
            values=[],
            size_hint=(1, None),
            height=44
        )
        self.main_layout.add_widget(self.exercise_spinner)

        self.sets_input = TextInput(
            hint_text='Введите количество подходов',
            multiline=False,
            size_hint=(1, None),
            height=44
        )
        self.main_layout.add_widget(self.sets_input)

        self.reps_input = TextInput(
            hint_text='Введите количество повторений',
            multiline=False,
            size_hint=(1, None),
            height=44
        )
        self.main_layout.add_widget(self.reps_input)

        self.add_button = Button(
            text="Добавить упражнение",
            size_hint=(1, None),
            height=50
        )
        self.add_button.bind(on_press=self.add_exercise)
        self.main_layout.add_widget(self.add_button)

        self.workout_scrollview = ScrollView(size_hint=(1, 1))
        self.workout_layout = GridLayout(cols=1, size_hint_y=None)
        self.workout_layout.bind(minimum_height=self.workout_layout.setter('height'))
        self.workout_scrollview.add_widget(self.workout_layout)
        self.main_layout.add_widget(self.workout_scrollview)

        self.save_button = Button(
            text="Сохранить программу",
            size_hint=(1, None),
            height=50
        )
        self.save_button.bind(on_press=self.save_workout)
        self.main_layout.add_widget(self.save_button)

        self.share_button = Button(
            text="Отправить программу",
            size_hint=(1, None),
            height=50
        )
        self.share_button.bind(on_press=self.share_workout)
        self.main_layout.add_widget(self.share_button)

        return self.main_layout

    def update_exercise_spinner(self, spinner, text):
        self.exercise_spinner.values = self.exercises_dict[text]
        self.exercise_spinner.text = 'Выберите упражнение'

    def add_exercise(self, instance):
        muscle_group = self.muscle_group_spinner.text
        exercise = self.exercise_spinner.text
        sets = self.sets_input.text
        reps = self.reps_input.text

        if muscle_group != 'Выберите группу мышц' and exercise != 'Выберите упражнение' and sets and reps:
            self.workout_data.append({
                'muscle_group': muscle_group,
                'exercise': exercise,
                'sets': sets,
                'reps': reps
            })
            self.sets_input.text = ""
            self.reps_input.text = ""
            self.update_workout_list()

    def update_workout_list(self):
        self.workout_layout.clear_widgets()
        for entry in self.workout_data:
            workout_label = Label(
                text=f"{entry['muscle_group']} - {entry['exercise']} - {entry['sets']}x{entry['reps']}",
                size_hint_y=None,
                height=40
            )
            self.workout_layout.add_widget(workout_label)

    def save_workout(self, instance):
        if not self.workout_data:
            return

        file_path = filechooser.save_file()
        if file_path:
            with open(file_path[0], 'w') as file:
                for entry in self.workout_data:
                    file.write(f"{entry['muscle_group']} - {entry['exercise']} - {entry['sets']}x{entry['reps']}\n")

    def share_workout(self, instance):
        if not self.workout_data:
            return

        workout_summary = ""
        for entry in self.workout_data:
            workout_summary += f"{entry['muscle_group']} - {entry['exercise']} - {entry['sets']}x{entry['reps']}\n"

        email.send(
            recipient='',
            subject='Моя программа тренировок',
            text=workout_summary
        )

if __name__ == "__main__":
    WorkoutApp().run()
