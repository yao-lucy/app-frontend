from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.utils import rgba


class OptyApp(App):

    def build(self):
        
        layout = BoxLayout(orientation = 'vertical', padding = '10dp', spacing = '5dp')
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

        layout.add_widget(title)
        layout.add_widget(search_input)
        layout.add_widget(scroll)
        layout.add_widget(button)

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