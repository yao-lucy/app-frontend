from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.utils import rgba
from kivy.uix.textinput import TextInput

import re
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

        # Makes black background
        layout = Background(orientation = 'vertical', padding = '10dp', spacing = '5dp')
        with layout.canvas.before:
            Color(0, 0, 0)
            layout.rect = Rectangle(size = layout.size, pos = layout.pos)
        layout.bind(size = layout._update_rect, pos = layout._update_rect)

        title_bar = BoxLayout(orientation = 'horizontal', size_hint_y = None, height = '35sp')
                
        title = Label(text = '[b]Stocks[/b]', markup = True, font_size = '35sp', size_hint_y = None, height = '35sp')
        title.bind(size = title.setter('text_size'))

        button = Button(text = 'Clear All', color = rgba('#4FACF9'), background_color = [0, 0, 0, 0], size_hint = (None, None), size = ('60dp', '20dp'),
                        pos_hint = {'center_y' : 0.5})
        button.bind(on_release = self.clear_stocks)

        title_bar.add_widget(title)
        title_bar.add_widget(button)

        # Search bar switches to search when clicked
        search_input = TextInput(hint_text = 'Search', font_size = '17sp', multiline = False, size_hint_y = None, height = '29dp')
        search_input.bind(focus = self.switch_to_search)

        self.table = BoxLayout(orientation = 'vertical', padding = '10dp', spacing = '10dp', size_hint_y = None)
        # Make sure the height is such that there is something to scroll.
        self.table.bind(minimum_height = self.table.setter('height'))

        scroll = ScrollView()
        scroll.add_widget(self.table)

        button = Button(text = '[b]Optimize[/b]', markup = True, font_size = '30sp', background_normal = '', background_color = rgba('#0081ED'), size_hint = (None, None),
                        size = ('180sp', '60sp'), pos_hint = {'center_x' : 0.5})
        button.bind(on_release = self.switch_to_optimized)

        layout.add_widget(title_bar)
        layout.add_widget(search_input)
        layout.add_widget(scroll)
        layout.add_widget(button)

        return layout
    
    def draw_table(self):

        self.table.clear_widgets()

        for i in range(len(self.manager.portfolio)):
            row = BoxLayout(orientation = 'horizontal', size_hint_y = None, height = '53dp')
            left = BoxLayout(orientation = 'vertical', spacing = '3dp')

            ticker = Label(text = '[b]' + self.manager.portfolio[i] + '[/b]', markup = True, font_size = '30sp', size_hint_y = None, height = '30sp')
            ticker.bind(size = ticker.setter('text_size'))

            name = Label(text = 'test', size_hint_y = None, height = '15sp')
            name.bind(size = name.setter('text_size'))

            left.add_widget(ticker)
            left.add_widget(name)

            btn = Button(text=str(i), size_hint = (None, None), size = ('30dp', '30dp'), pos_hint = {'center_y' : 0.5})
            btn.bind(on_release = self.remove_stock)

            row.add_widget(left)
            row.add_widget(btn)

            self.table.add_widget(row)

            if i != len(self.manager.portfolio) - 1:
                sep = Background(size_hint_y = None, height = '1dp')
                with sep.canvas.before:
                    Color(rgba = rgba('#808080'))
                    sep.rect = Rectangle(size = sep.size, pos = sep.pos)
                sep.bind(size = sep._update_rect, pos = sep._update_rect)
                self.table.add_widget(sep)
    
    def remove_stock(self, instance):
        # Gets referenced stock
        stock = instance.parent.children[1].children[1].text.removeprefix('[b]').removesuffix('[/b]')
        self.manager.portfolio.remove(stock)
        self.draw_table()
        if self.table.parent.scroll_y == 0:
            self.table.parent.scroll_y += 1e-8
    
    def clear_stocks(self, instance):
        # Clears stocks
        self.manager.portfolio = []
        self.draw_table()
    
    def switch_to_optimized(self, instance):
        # Switch to the OptimizedScreen
        self.manager.transition = CardTransition(direction='left')
        self.manager.current = 'optimized'

    def switch_to_search(self, instance, value):
        # Focus on new text box and switch to the SearchScreen
        textbox = self.manager.get_screen('search').children[0].children[1].children[1]

        textbox.focus = True
        self.manager.transition = CardTransition(direction='up')
        self.manager.get_screen('search').suggest(instance = None, value = textbox.text)
        self.manager.current = 'search'


class SearchScreen(Screen):

    def __init__(self, **kwargs):
        super(SearchScreen, self).__init__(**kwargs)

        self.tickers = ['GOOGL', 'DIS', 'TSLA', 'SNAP', 'PTON', 'LEVI', 'MS', 'ULTA', 'WBD']
    
        self.suggestions = []

        layout = self.create_layout()
        self.add_widget(layout)
    
    def create_layout(self):

        # Makes black background
        layout = Background(orientation = 'vertical', padding = '10dp', spacing = '5dp')
        with layout.canvas.before:
            Color(0, 0, 0)
            layout.rect = Rectangle(size = layout.size, pos = layout.pos)
        layout.bind(size = layout._update_rect, pos = layout._update_rect)

        title_bar = BoxLayout(orientation = 'horizontal', spacing = '5dp', size_hint_y = None, height = '29dp')

        search_input = TextInput(hint_text = 'Search', font_size = '17sp', multiline = False, size_hint_y = None, height = '29dp')
        search_input.bind(text = self.suggest)

        button = Button(text = 'Done', color = rgba('#4FACF9'), background_color = [0, 0, 0, 0], size_hint = (None, None), size = ('40dp', '20dp'),
                        pos_hint = {'center_y' : 0.5})
        button.bind(on_release = self.switch_to_stocks)

        title_bar.add_widget(search_input)
        title_bar.add_widget(button)

        self.table = BoxLayout(orientation = 'vertical', padding = '10dp', spacing = '10dp', size_hint_y = None)
        # Make sure the height is such that there is something to scroll.
        self.table.bind(minimum_height = self.table.setter('height'))

        scroll = ScrollView()
        scroll.add_widget(self.table)

        layout.add_widget(title_bar)
        layout.add_widget(scroll)

        return layout

    def switch_to_stocks(self, instance):
        # Switch to the StocksScreen
        self.manager.transition = CardTransition(direction = 'down')
        self.manager.get_screen('stocks').draw_table()
        self.manager.current = 'stocks'
    
    def suggest(self, instance, value):
        # Regular expression pattern
        pattern = re.compile(value.upper())

        # Filter list elements matching the pattern
        self.suggestions = [elem for elem in self.tickers if pattern.search(elem)]

        self.table.clear_widgets()
        self.table.parent.scroll_y = 1

        for i in range(len(self.suggestions)):
            
            row = BoxLayout(orientation = 'horizontal', size_hint_y = None, height = '53dp')
            left = BoxLayout(orientation = 'vertical', spacing = '3dp')

            ticker = Label(text = '[b]' + self.suggestions[i] + '[/b]', markup = True, font_size = '30sp', size_hint_y = None, height = '30sp')
            ticker.bind(size = ticker.setter('text_size'))

            name = Label(text = 'test', size_hint_y = None, height = '15sp')
            name.bind(size = name.setter('text_size'))

            left.add_widget(ticker)
            left.add_widget(name)

            row.add_widget(left)

            if self.suggestions[i] in self.manager.portfolio:
                x = '**placeholder**'
            else:
                btn = Button(text=str(i), size_hint = (None, None), size = ('30dp', '30dp'), pos_hint = {'center_y' : 0.5})
                btn.bind(on_release = self.add_stock)
                row.add_widget(btn)

            self.table.add_widget(row)

            if i != len(self.suggestions) - 1:
                sep = Background(size_hint_y = None, height = '1dp')
                with sep.canvas.before:
                    Color(rgba = rgba('#808080'))
                    sep.rect = Rectangle(size = sep.size, pos = sep.pos)
                sep.bind(size = sep._update_rect, pos = sep._update_rect)
                self.table.add_widget(sep)

    def add_stock(self, instance):
        # Gets referenced stock
        stock = instance.parent.children[1].children[1].text.removeprefix('[b]').removesuffix('[/b]')
        self.manager.portfolio.append(stock)
        instance.parent.remove_widget(instance)


class OptimizedScreen(Screen):

    def __init__(self, **kwargs):
        super(OptimizedScreen, self).__init__(**kwargs)
        layout = self.create_layout()
        self.add_widget(layout)
    
    def create_layout(self):
        
        # Makes black background
        layout = Background(orientation = 'vertical', padding = '10dp', spacing = '5dp')
        with layout.canvas.before:
            Color(0, 0, 0)
            layout.rect = Rectangle(size = layout.size, pos = layout.pos)
        layout.bind(size = layout._update_rect, pos = layout._update_rect)
        
        button = Button(text = 'Back', color = rgba('#4FACF9'), background_color = [0, 0, 0, 0], size_hint = (None, None), size = ('40dp', '20dp'))
        button.bind(on_release=self.switch_to_stocks)

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
                sep = Background(size_hint_y = None, height = '1dp')
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

class Background(BoxLayout):

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(Background, self).__init__(**kwargs)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class PortfolioManager(ScreenManager):

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(PortfolioManager, self).__init__(**kwargs)

        self.portfolio = []

class TestApp(App):

    def build(self):
        # Create the screen manager
        sm = PortfolioManager()
        sm.add_widget(StocksScreen(name = 'stocks'))
        sm.add_widget(SearchScreen(name = 'search'))
        sm.add_widget(OptimizedScreen(name = 'optimized'))

        return sm

if __name__ == '__main__':
    TestApp().run()