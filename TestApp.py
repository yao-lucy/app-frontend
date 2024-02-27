from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.utils import rgba
from kivy.uix.textinput import TextInput

import requests
import json

from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, CardTransition

class StocksScreen(Screen):
    def __init__(self, **kwargs):
        super(StocksScreen, self).__init__(**kwargs)
        layout = self.create_layout()
        self.add_widget(layout)
    
    def create_layout(self):
        layout = BoxLayout(orientation = 'vertical', padding = '10dp', spacing = '5dp')
        
        with self.canvas.before:
            Color(0, 0, 0, 1)  # Black color
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)
        
        title = Label(text = '[b]Stocks[/b]', markup = True, font_size = '35sp', size_hint_y = None, height = '35sp')
        title.bind(size = title.setter('text_size'))

        search_input = TextInput(hint_text = 'Search', font_size = '17sp', multiline = False, size_hint_y = None)
        search_input.height = '29dp'

        table = BoxLayout(orientation = 'vertical', padding = '10dp', spacing = '10dp', size_hint_y = None)
        # Make sure the height is such that there is something to scroll.
        table.bind(minimum_height = table.setter('height'))

        test_tickers = ['GOOGL', 'DIS', 'TSLA', 'SNAP', 'PTON', 'LEVI', 'MS', 'ULTA', 'WBD']

        for i in range(len(test_tickers)):
            row = BoxLayout(orientation = 'horizontal', size_hint_y = None, height = '53dp')
            left = BoxLayout(orientation = 'vertical', spacing = '3dp')

            ticker = Label(text = '[b]' + test_tickers[i] + '[/b]', markup = True, font_size = '30sp', size_hint_y = None, height = '30sp')
            ticker.bind(size = ticker.setter('text_size'))

            name = Label(text = 'test', size_hint_y = None, height = '15sp')
            name.bind(size = name.setter('text_size'))

            left.add_widget(ticker)
            left.add_widget(name)

            btn = Button(text=str(i), size_hint = (None, None), size = ('30dp', '30dp'), pos_hint = {'center_y' : 0.5})

            row.add_widget(left)
            row.add_widget(btn)

            table.add_widget(row)

            if i != len(test_tickers) - 1:
                sep = Separator(size_hint_y = None, height = '1dp')
                with sep.canvas.before:
                    Color(rgba = rgba('#808080'))
                    sep.rect = Rectangle(size = sep.size, pos = sep.pos)
                sep.bind(size = sep._update_rect, pos = sep._update_rect)
                table.add_widget(sep)

        scroll = ScrollView()
        scroll.add_widget(table)

        button = Button(text = '[b]Optimize[/b]', markup = True, font_size = '30sp', background_normal = '', background_color = rgba('#0081ED'), size_hint = (None, None),
                        size = ('180sp', '60sp'), pos_hint = {'center_x' : 0.5})
        button.bind(on_press=self.switch_to_optimized)

        layout.add_widget(title)
        layout.add_widget(search_input)
        layout.add_widget(scroll)
        layout.add_widget(button)

        return layout
    
    def switch_to_optimized(self, instance):
        # Switch to the OptimizedScreen
        self.manager.transition = CardTransition(direction='left')
        self.manager.current = 'optimized'
    
    def update_rect(self, instance, value):
        self.rect.size = self.size
        self.rect.pos = self.pos

class OptimizedScreen(Screen):
    def __init__(self, **kwargs):
        super(OptimizedScreen, self).__init__(**kwargs)
        layout = self.create_layout()
        self.add_widget(layout)
    
    def create_layout(self):
        
        layout = BoxLayout(orientation = 'vertical', padding = '10dp', spacing = '5dp')
        
        with self.canvas.before:
            Color(0, 0, 0, 1)  # Black color
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        button = Button(text = 'Back', color = rgba('#4FACF9'), background_color = [0, 0, 0, 0], size_hint = (None, None), size = ('40dp', '20dp'))
        button.bind(on_press=self.switch_to_stocks)

        title = Label(text = '[b]Portfolio[/b]', markup = True, font_size = '35sp', size_hint_y = None, height = '35sp')
        title.bind(size = title.setter('text_size'))
        
        #test_resp = json.dumps({'portfolio' : [{"symbol": "AAPL", "allocation": 0.4}, {"symbol": "GOOGL", "allocation": 0.3}, {"symbol": "MSFT", "allocation": 0.3}]})

        #portfolio = test_resp.json()['portfolio']

        portfolio = {'portfolio' : [{"symbol": "GOOGL", "allocation": 0.2}, {"symbol": "TSLA", "allocation": 0.2},
                    {"symbol": "LEVI", "allocation": 0.2}, {"symbol": "MS", "allocation": 0.05}, {"symbol": "META", "allocation": 0.1},
                    {"symbol": "SNAP", "allocation": 0.25}]}['portfolio']
        sorted_port = sorted(portfolio, key = lambda x: x['allocation'], reverse = True)
        
        tickers = [stock['symbol'] for stock in sorted_port]
        sizes = [stock['allocation'] for stock in sorted_port]  # Sizes or proportions of each slice
        colors = ['#0081ED', '#4FACF9', '#FF9502', '#F9C200', '#35C759', 'white']  # Colors for each slice

        # Plot
        fig, ax = plt.subplots(facecolor = 'black')
        ax.pie(x = sizes, labels = tickers, colors = colors, autopct = '%1.1f%%', startangle = 90, counterclock = False, textprops = {'color' : 'white'})
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Create a FigureCanvasKivyAgg widget to display the pie chart
        canvas = FigureCanvasKivyAgg(figure = fig)

        title_bar = BoxLayout(orientation = 'horizontal', padding = ['10dp', 0], size_hint_y = None, height = '15sp')

        title_left = Label(text = '[b]Stock[/b]', markup = True, size_hint_y = None, height = '15sp')
        title_left.bind(size = title_left.setter('text_size'))

        title_right = Label(text = '[b]Allocation[/b]', markup = True, size_hint_y = None, height = '15sp', halign = 'right')
        title_right.bind(size = title_right.setter('text_size'))

        title_bar.add_widget(title_left)
        title_bar.add_widget(title_right)

        table = BoxLayout(orientation = 'vertical', padding = '10dp', spacing = '10dp', size_hint_y = None)
        # Make sure the height is such that there is something to scroll.
        table.bind(minimum_height = table.setter('height'))

        for i in range(len(tickers)):
            row = BoxLayout(orientation = 'horizontal', size_hint_y = None, height = '53dp')
            left = BoxLayout(orientation = 'vertical', spacing = '3dp')

            ticker = Label(text = '[b]' + tickers[i] + '[/b]', markup = True, font_size = '30sp', size_hint_y = None, height = '30sp')
            ticker.bind(size = ticker.setter('text_size'))

            name = Label(text = 'test', size_hint_y = None, height = '15sp')
            name.bind(size = name.setter('text_size'))

            left.add_widget(ticker)
            left.add_widget(name)

            pct = Label(text = f"{sizes[i]:.1%}", font_size = '30sp', size_hint_y = None, height = '30sp', halign = 'right', pos_hint = {'center_y' : 0.5})
            pct.bind(size = pct.setter('text_size'))

            row.add_widget(left)
            row.add_widget(pct)

            table.add_widget(row)

            if i != len(tickers) - 1:
                sep = Separator(size_hint_y = None, height = '1dp')
                with sep.canvas.before:
                    Color(rgba = rgba('#808080'))
                    sep.rect = Rectangle(size = sep.size, pos = sep.pos)
                sep.bind(size = sep._update_rect, pos = sep._update_rect)
                table.add_widget(sep)

        scroll = ScrollView()
        scroll.add_widget(table)

        layout.add_widget(button)
        layout.add_widget(title)
        layout.add_widget(canvas)
        layout.add_widget(title_bar)
        layout.add_widget(scroll)

        return layout

    def switch_to_stocks(self, instance):
        # Switch to the StocksScreen
        self.manager.transition = CardTransition(direction='right')
        self.manager.current = 'stocks'
        
    def update_rect(self, instance, value):
        self.rect.size = self.size
        self.rect.pos = self.pos

class Separator(BoxLayout):

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(Separator, self).__init__(**kwargs)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class TestApp(App):

    def build(self):
        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(StocksScreen(name='stocks'))
        sm.add_widget(OptimizedScreen(name='optimized'))

        return sm

if __name__ == '__main__':
    TestApp().run()