from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.utils import rgba

import requests
import json

from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt


class OptyApp(App):

    def build(self):
        
        layout = BoxLayout(orientation = 'vertical', padding = '10dp', spacing = '5dp')

        button = Button(text = 'Back', color = rgba('#4FACF9'), background_color = [0, 0, 0, 0], size_hint = (None, None), size = ('40dp', '20dp'))

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

class Separator(BoxLayout):

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(Separator, self).__init__(**kwargs)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

if __name__ == '__main__':
    OptyApp().run()