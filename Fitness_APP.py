from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.uix.checkbox import CheckBox
from kivy.core.window import Window
from kivy.uix.behaviors.drag import DragBehavior
from babel.dates import format_datetime
from datetime import datetime

class DraggableLabel(DragBehavior, BoxLayout):
    def __init__(self, index, workout_data, update_workout_list_callback, **kwargs):
        super(DraggableLabel, self).__init__(**kwargs)
        self.index = index
        self.workout_data = workout_data
        self.update_workout_list_callback = update_workout_list_callback
        self.orientation = 'horizontal'
        self.drag_timeout = 1000  # ms
        self.drag_distance = 0

        self.label = Label(
            text=f"{self.workout_data[index]['muscle_group']} - {self.workout_data[index]['exercise']} - {self.workout_data[index]['sets']}x{self.workout_data[index]['reps']}",
            size_hint_x=0.9,
            color=[1, 0, 0, 1]  # Цвет шрифта
        )

        self.checkbox = CheckBox(size_hint_x=0.1)
        self.checkbox.bind(active=self.mark_completed)

        self.add_widget(self.label)
        self.add_widget(self.checkbox)

    def mark_completed(self, instance, value):
        self.workout_data[self.index]['completed'] = value
        self.label.color = [0, 1, 0, 1] if value else [1, 0, 0, 1]  # Зеленый цвет для выполненных упражнений

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            new_index = self.parent.children.index(self)
            if new_index != self.index:
                self.workout_data.insert(new_index, self.workout_data.pop(self.index))
                self.update_workout_list_callback()
        return super(DraggableLabel, self).on_touch_up(touch)

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.workout_data = []

        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Добавление фона
        with self.main_layout.canvas.before:
            self.bg = Image(source='background.jpg', allow_stretch=True, keep_ratio=False)
            self.main_layout.bind(size=self._update_background, pos=self._update_background)

        # Верхняя часть с датой и днем недели
        current_date = format_datetime(datetime.now(), "EEEE, d MMMM yyyy", locale='ru')
        self.date_label = Label(text=current_date, size_hint=(1, 0.1))
        self.main_layout.add_widget(self.date_label)

        # Прокручиваемый виджет для отображения добавленных упражнений
        self.workout_scrollview = ScrollView(size_hint=(1, 0.8))
        self.workout_layout = GridLayout(cols=1, size_hint_y=None)
        self.workout_layout.bind(minimum_height=self.workout_layout.setter('height'))
        self.workout_scrollview.add_widget(self.workout_layout)
        self.main_layout.add_widget(self.workout_scrollview)

        # Кнопка для добавления упражнения
        self.add_button = Button(
            text="+",
            size_hint=(None, None),
            size=(50, 50),
            pos_hint={'right': 1, 'bottom': 1},
            background_color=[1, 1, 1, 0.1]  # Максимальная прозрачность
        )
        self.add_button.bind(on_press=self.open_add_exercise_screen)

        anchor_layout = AnchorLayout(anchor_x='right', anchor_y='bottom')
        anchor_layout.add_widget(self.add_button)
        self.main_layout.add_widget(anchor_layout)

        self.add_widget(self.main_layout)

    def _update_background(self, instance, value):
        self.bg.size = (self.main_layout.width, self.main_layout.height)
        self.bg.pos = (self.main_layout.x, self.main_layout.y)

    def open_add_exercise_screen(self, instance):
        self.manager.current = 'add_exercise_screen'

    def add_exercise(self, muscle_group, exercise, sets, reps):
        self.workout_data.append({
            'muscle_group': muscle_group,
            'exercise': exercise,
            'sets': sets,
            'reps': reps,
            'completed': False
        })
        self.update_workout_list()

    def update_workout_list(self):
        self.workout_layout.clear_widgets()
        for index, entry in enumerate(self.workout_data):
            draggable_label = DraggableLabel(index, self.workout_data, self.update_workout_list)
            self.workout_layout.add_widget(draggable_label)

class AddExerciseScreen(Screen):
    def __init__(self, **kwargs):
        super(AddExerciseScreen, self).__init__(**kwargs)

        self.exercises_dict = {
            'Грудь': ['Жим лежа', 'Разводка гантелей', 'Отжимания'],
            'Спина': ['Тяга верхнего блока', 'Тяга гантели', 'Подтягивания'],
            'Ноги': ['Приседания', 'Выпады', 'Становая тяга'],
            'Плечи': ['Жим гантелей сидя', 'Разведение гантелей в стороны', 'Тяга штанги к подбородку'],
            'Руки': ['Сгибание рук с гантелями', 'Разгибание рук на блоке', 'Подъемы на бицепс со штангой']
        }

        self.layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Добавление фона
        with self.layout.canvas.before:
            self.bg = Image(source='background.jpg', allow_stretch=True, keep_ratio=False)
            self.layout.bind(size=self._update_background, pos=self._update_background)

        # Спиннер для выбора группы мышц
        self.muscle_group_spinner = Spinner(
            text='Выберите группу мышц',
            values=tuple(self.exercises_dict.keys()),
            size_hint=(1, None),
            height=44,
            background_color=[1, 1, 1, 0.1]  # Максимальная прозрачность
        )
        self.muscle_group_spinner.bind(text=self.update_exercise_spinner)
        self.layout.add_widget(self.muscle_group_spinner)

        # Спиннер для выбора упражнения
        self.exercise_spinner = Spinner(
            text='Выберите упражнение',
            values=[],
            size_hint=(1, None),
            height=44,
            background_color=[1, 1, 1, 0.1]  # Максимальная прозрачность
        )
        self.layout.add_widget(self.exercise_spinner)

        # Поле ввода для количества подходов
        self.sets_input = TextInput(
            hint_text='Введите количество подходов',
            multiline=False,
            size_hint=(1, None),
            height=44,
            background_color=[1, 1, 1, 0.1]  # Максимальная прозрачность
        )
        self.layout.add_widget(self.sets_input)

        # Поле ввода для количества повторений
        self.reps_input = TextInput(
            hint_text='Введите количество повторений',
            multiline=False,
            size_hint=(1, None),
            height=44,
            background_color=[1, 1, 1, 0.1]  # Максимальная прозрачность
        )
        self.layout.add_widget(self.reps_input)

        # Кнопка добавления упражнения
        self.add_button = Button(
            text="Добавить упражнение",
            size_hint=(1, None),
            height=50,
            background_color=[1, 1, 1, 0.1]  # Максимальная прозрачность
        )
        self.add_button.bind(on_press=self.add_exercise)
        self.layout.add_widget(self.add_button)

        # Кнопка для возвращения на главный экран
        self.back_button = Button(
            text="<",
            size_hint=(None, None),
            size=(50, 50),
            pos_hint={'right': 1, 'bottom': 1},
            background_color=[1, 1, 1, 0.1]  # Максимальная прозрачность
        )
        self.back_button.bind(on_press=self.go_back)

        anchor_layout = AnchorLayout(anchor_x='right', anchor_y='bottom')
        anchor_layout.add_widget(self.back_button)
        self.layout.add_widget(anchor_layout)

        self.add_widget(self.layout)

    def _update_background(self, instance, value):
        self.bg.size = (self.layout.width, self.layout.height)
        self.bg.pos = (self.layout.x, self.layout.y)

    def update_exercise_spinner(self, spinner, text):
        self.exercise_spinner.values = self.exercises_dict[text]
        self.exercise_spinner.text = 'Выберите упражнение'

    def add_exercise(self, instance):
        muscle_group = self.muscle_group_spinner.text
        exercise = self.exercise_spinner.text
        sets = self.sets_input.text
        reps = self.reps_input.text

        if muscle_group != 'Выберите группу мышц' and exercise != 'Выберите упражнение' and sets and reps:
            self.manager.get_screen('main_screen').add_exercise(muscle_group, exercise, sets, reps)
            self.go_back(instance)

    def go_back(self, instance):
        self.manager.current = 'main_screen'

class WorkoutApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main_screen'))
        sm.add_widget(AddExerciseScreen(name='add_exercise_screen'))
        return sm

if __name__ == "__main__":
    WorkoutApp().run()

