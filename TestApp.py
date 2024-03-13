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
        self.table.parent.scroll_y = 1

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
        # Post to /stocks
        body = {'selected_stocks' : [{'symbol' : stock} for stock in self.manager.portfolio]}

        try:
            resp = requests.post('http://127.0.0.1/stocks', data = json.dumps(body))
            resp.raise_for_status()
        except requests.exceptions.ConnectionError:
            print('Error: Could not connect to /stocks endpoint.')
            return
        except requests.exceptions.HTTPError as err:
            print('Posting to /stocks failed. Error Code:')
            print(err.response.status_code)
            return
        except requests.exceptions.Timeout:
            print('Request to /stocks timed out.')
            return
        except requests.exceptions.TooManyRedirects:
            print('Bad URL. Too many redirects to /stocks.')
            return

        # Post to /optimize
        try:
            resp = requests.post('http://127.0.0.1/optimize')
            resp.raise_for_status()
        except requests.exceptions.ConnectionError:
            print('Error: Could not connect to /optimize endpoint.')
            return
        except requests.exceptions.HTTPError as err:
            print('Posting to /optimize failed. Error Code:')
            print(err.response.status_code)
            return
        except requests.exceptions.Timeout:
            print('Request to /optimize timed out.')
            return
        except requests.exceptions.TooManyRedirects:
            print('Bad URL. Too many redirects to /optimize.')
            return

        # Get to /portfolio
        try:
            resp = requests.get('http://127.0.0.1/portfolio')
            resp.raise_for_status()
        except requests.exceptions.ConnectionError:
            print('Error: Could not connect to /portfolio endpoint.')
            return
        except requests.exceptions.HTTPError as err:
            print('Get to /portfolio failed. Error Code:')
            print(err.response.status_code)
            return
        except requests.exceptions.Timeout:
            print('Request to /portfolio timed out.')
            return
        except requests.exceptions.TooManyRedirects:
            print('Bad URL. Too many redirects to /portfolio.')
            return

        portfolio = resp.json()['portfolio']
        # portfolio = {'portfolio' : [{"symbol": "GOOGL", "allocation": 0.2}, {"symbol": "TSLA", "allocation": 0.2},
        #             {"symbol": "LEVI", "allocation": 0.2}, {"symbol": "MS", "allocation": 0.05}, {"symbol": "META", "allocation": 0.1},
        #             {"symbol": "SNAP", "allocation": 0.25}]}['portfolio']
        # portfolio = {'portfolio' : [{"symbol": stock, "allocation": 1 / len(self.manager.portfolio)} for stock in self.manager.portfolio]}['portfolio']
        sorted_port = sorted(portfolio, key = lambda x: x['allocation'], reverse = True)

        self.manager.portfolio = [stock['symbol'] for stock in sorted_port]
        self.manager.get_screen('optimized').sizes = [stock['allocation'] for stock in sorted_port]

        # Switch to the OptimizedScreen
        self.manager.transition = CardTransition(direction='left')
        self.manager.get_screen('optimized').visualize()
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

        self.tickers = ['INTC', 'JPM', 'CCI', 'DHI', 'FLIR', 'AIV', 'UAL', 'IVZ', 'NFLX', 'LPX', 'XRX', 'APTV', 'GOOG', 'DHR', 'BR', 'CNC', 'ZTS', 'VAR', 'APH', 'DD', 'CIEN', 'ALGN', 'STZ', 'STT', 'SPG', 'ORCL', 'NRG', 'WHR', 'DLTR', 'AJG', 'RAD', 'AYI', 'EL', 'HST', 'CPRI', 'MRO', 'COP', 'MDT', 'TSCO', 'CCL', 'REGN', 'ASH', 'BGG', 'JNJ', 'ALTR', 'BC', 'WAB', 'AVY', 'AKAM', 'KEYS', 'PYPL', 'BRK.B', 'CMG', 'PXD', 'CTXS', 'BMY', 'SWK', 'SWN', 'RLGY', 'SANM', 'NLSN', 'BEAM', 'HII', 'TYL', 'PCG', 'EQT', 'SBUX', 'CNX', 'AWK', 'PBCT', 'ADP', 'SO', 'FE', 'CLF', 'CMA']#, 'CAT', 'BDX', 'NAV', 'PGR', 'EIX', 'SCI', 'CRM', 'PBI', 'AMT', 'BWA', 'CMS', 'PPL', 'WBA', 'AON', 'RF', 'AZO', 'TT', 'MDP', 'CF', 'RSG', 'HSBC', 'NKTR', 'WPX', 'BKNG', 'MSFT', 'WMB', 'LNT', 'MHK', 'CTL', 'HAL', 'FANG', 'DISCK', 'AAL', 'EQ', 'KMB', 'ODP', 'WRB', 'AEE', 'ALB', 'EMN', 'MCHP', 'TMO', 'UIS', 'NLOK', 'O', 'TKR', 'NCR', 'EOG', 'CBOE', 'SNA', 'TPR', 'VIAV', 'MTB', 'AMAT', 'BF.B', 'RCL', 'BBBY', 'KEY', 'AVB', 'AXP', 'QCOM', 'GS', 'RHI', 'PKG', 'LYB', 'SHW', 'CERN', 'TGNA', 'VLO', 'MRK', 'DVN', 'QRVO', 'CTLT', 'KO', 'ITT', 'ENPH', 'COG', 'K', 'PWR', 'DLX', 'USB', 'VMC', 'SJM', 'CL', 'ETSY', 'LMT', 'VC', 'IGT', 'FSLR', 'PRGO', 'CSCO', 'UNP', 'BIG', 'KHC', 'SSP', 'JBHT', 'UDR', 'IPGP', 'VIAC', 'EMR', 'ICE', 'VRSN', 'DO', 'PDCO', 'HES', 'MSCI', 'GPC', 'MTD', 'DNR', 'CVS', 'NSC', 'NOV', 'PM', 'WAT', 'RRC', 'XEC', 'HWM', 'HRL', 'NWSA', 'ZION', 'AGN', 'JCI', 'OKE', 'CHIR', 'IQV', 'CBRE', 'PFE', 'BEN', 'FL', 'GHC', 'ADSK', 'C', 'AMZN', 'HOLX', 'NEE', 'FTI', 'EHC', 'WLTW', 'SWKS', 'HFC', 'EW', 'TJX', 'HOG', 'FAST', 'BBY', 'OMC', 'SLM', 'LIN', 'XLNX', 'D', 'FTNT', 'FISV', 'BIO', 'NVR', 'GRA', 'DOW', 'FCX', 'TDG', 'PSX', 'KBH', 'DISH', 'DELL', 'SLB', 'COF', 'TMUS', 'SYY', 'ENDP', 'MTG', 'LNC', 'SPXC', 'NCLH', 'RTN', 'ROL', 'SEE', 'TFC', 'TSN', 'MCD', 'URI', 'BA', 'SRCL', 'PEP', 'DXCM', 'PNW', 'NC', 'HBAN', 'HON', 'TEX', 'CB', 'RMD', 'WDC', 'TDC', 'TXN', 'FOSL', 'BXP', 'DXC', 'XYL', 'IRM', 'ILMN', 'OXY', 'BSX', 'GWW', 'MNST', 'J', 'FRT', 'YUM', 'SNPS', 'SPGI', 'ADI', 'ABT', 'FB', 'WU', 'AOS', 'EXR', 'PG', 'SPY', 'AKS', 'TUP', 'CPB', 'LHX', 'KSS', 'HUM', 'FOXA', 'CXO', 'DFS', 'NVDA', 'UN', 'GIS', 'VNO', 'KR', 'IP', 'ES', 'FLT', 'FLR', 'GOOGL', 'JEF', 'EQR', 'UNH', 'CHRW', 'JWN', 'CME', 'HRB', 'PFG', 'CNP', 'MPC', 'APA', 'UTX', 'BIIB', 'EVRG', 'SYF', 'TDY', 'NKE', 'CPRT', 'HP', 'F', 'QEP', 'HCA', 'NWS', 'ZBRA', 'LM', 'ABMD', 'FFIV', 'NUE', 'MDLZ', 'LUV', 'TIF', 'GILD', 'AIG', 'ADBE', 'TRMB', 'RIG', 'FHN', 'VTR', 'ATI', 'AMP', 'IPG', 'ALK', 'BLK', 'ZBH', 'LEG', 'VRTX', 'CVX', 'DDS', 'ANF', 'CSX', 'FLS', 'AAPL', 'PLL', 'WRK', 'RE', 'AMG', 'JKHY', 'ECL', 'TTWO', 'HLT', 'MAT', 'AMCR', 'GPS', 'LW', 'CCK', 'LOW', 'WMT', 'TER', 'TAP', 'L', 'HPQ', 'MUR', 'AMD', 'MAS', 'SRE', 'GRMN', 'MMC', 'WM', 'S', 'MO', 'PEG', 'CHK', 'FTV', 'AME', 'JNPR', 'PAYC', 'MCK', 'R', 'TSLA', 'EXC', 'GE', 'T', 'CLX', 'WELL', 'RJF', 'ALLE', 'LYV', 'BAX', 'MMM', 'IDXX', 'IAC', 'NTAP', 'MKTX', 'ALXN', 'NYT', 'BAC', 'HIG', 'TGT', 'MS', 'MET', 'CAG', 'DVA', 'GME', 'MA', 'MTW', 'ARE', 'FDX', 'STX', 'RRD', 'AVGO', 'THC', 'SAN', 'CTAS', 'UAA', 'PHM', 'LH', 'PSA', 'ETN', 'ABBV', 'TXT', 'CFG', 'LKQ', 'MU', 'CDW', 'ETFC', 'GPN', 'DIS', 'EBAY', 'FITB', 'WYNN', 'PKI', 'ANSS', 'NOC', 'DOV', 'NTRS', 'CINF', 'AFL', 'PPG', 'EQIX', 'XRAY', 'AAP', 'POOL', 'FBHS', 'SIG', 'PCAR', 'JCP', 'TRIP', 'KMI', 'LDOS', 'PAYX', 'TROW', 'PTC', 'DPZ', 'EFX', 'NBR', 'COTY', 'STE', 'HSIC', 'ANET', 'GT', 'ALL', 'CAR', 'BK', 'CE', 'WOR', 'BHF', 'PH', 'KMX', 'HSY', 'OI', 'ROP', 'MAR', 'RL', 'DGX', 'UHS', 'PLD', 'ANTM', 'CMI', 'KLAC', 'PRU', 'CTB', 'NAVI', 'IT', 'TEL', 'DUK', 'AES', 'NE', 'VAL', 'DAL', 'DLR', 'ED', 'INTU', 'TEN', 'URBN', 'IBM', 'IFF', 'UPS', 'MKC', 'ATVI', 'JBL', 'AMGN', 'ROK', 'MGM', 'CDNS', 'VZ', 'PCH', 'TWTR', 'COO', 'LLY', 'ORLY', 'EA', 'A', 'PVH', 'BKR', 'ADS', 'REG', 'AEP', 'TRV', 'FTR', 'HD', 'LVS', 'GOLD', 'HBI', 'EXPD', 'MCO', 'MAA', 'SBAC', 'LB', 'AIZ', 'LEN', 'LRCX', 'GM', 'HAS', 'CHTR', 'MLM', 'PNC', 'TFX', 'FMC', 'WFC', 'UNM', 'ADM', 'KDP', 'NDAQ', 'XOM', 'DE', 'GL', 'GNW', 'FIS', 'NI', 'EXPE', 'SCHW', 'MOS', 'CR', 'CI', 'ROST', 'AN', 'IEX', 'DRI', 'KIM', 'SNV', 'MNK', 'GD', 'SITC', 'FRC', 'ISRG', 'ABC', 'CTVA', 'APD', 'DTE', 'VFC', 'FOX', 'NWL', 'XEL', 'CMCSA', 'WST', 'ESS', 'DRE', 'SIVB', 'PNR', 'ODFL', 'BVSN', 'CHD', 'MYL', 'ETR', 'INFO', 'NEM', 'COST', 'ATO', 'ATGE', 'SYK', 'IR', 'ULTA', 'WEC', 'M', 'NBL', 'ITW', 'MSI', 'HCR', 'HPE', 'SLG', 'INCY', 'BLL', 'MBI', 'NOW', 'KSU', 'PEAK', 'MXIM', 'ACN', 'PD', 'V', 'CTSH', 'CAH', 'GLW', 'MAC', 'DG', 'X', 'WY', 'VRSK']
    
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
    
    def switch_to_stocks(self, instance):
        # Switch to the StocksScreen
        self.manager.transition = CardTransition(direction = 'down')
        self.manager.get_screen('stocks').draw_table()
        self.manager.current = 'stocks'


class OptimizedScreen(Screen):

    def __init__(self, **kwargs):
        super(OptimizedScreen, self).__init__(**kwargs)

        self.sizes = []

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

        # Plot
        fig, self.ax = plt.subplots(facecolor = 'black')
        self.ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Create a FigureCanvasKivyAgg widget to display the pie chart
        canvas = FigureCanvasKivyAgg(figure = fig)

        title_bar = BoxLayout(orientation = 'horizontal', padding = ['10dp', 0], size_hint_y = None, height = '15sp')

        title_left = Label(text = '[b]Stock[/b]', markup = True, size_hint_y = None, height = '15sp')
        title_left.bind(size = title_left.setter('text_size'))

        title_right = Label(text = '[b]Allocation[/b]', markup = True, size_hint_y = None, height = '15sp', halign = 'right')
        title_right.bind(size = title_right.setter('text_size'))

        title_bar.add_widget(title_left)
        title_bar.add_widget(title_right)

        self.table = BoxLayout(orientation = 'vertical', padding = '10dp', spacing = '10dp', size_hint_y = None)
        # Make sure the height is such that there is something to scroll.
        self.table.bind(minimum_height = self.table.setter('height'))

        scroll = ScrollView()
        scroll.add_widget(self.table)

        layout.add_widget(button)
        layout.add_widget(title)
        layout.add_widget(canvas)
        layout.add_widget(title_bar)
        layout.add_widget(scroll)

        return layout
    
    def visualize(self):
        
        colors = ['#0081ED', '#4FACF9', '#FF9502', '#F9C200', '#35C759', 'white']  # Colors for each slice
        
        self.ax.clear()
        _, _, autotexts = self.ax.pie(x = self.sizes, labels = self.manager.portfolio, colors = colors, autopct = '%1.1f%%', startangle = 90, counterclock = False,
                textprops = {'color' : 'white', 'weight' : 'heavy'}, pctdistance = 0.8, radius = 1.4)
        for i in range(len(autotexts)):
            autotexts[i].set_fontweight('normal')
            if (i + 1) % 6 == 0:
                autotexts[i].set_color('black')
        plt.draw()
        
        self.table.clear_widgets()
        self.table.parent.scroll_y = 1

        for i in range(len(self.manager.portfolio)):
            row = BoxLayout(orientation = 'horizontal', size_hint_y = None, height = '53dp')
            left = BoxLayout(orientation = 'vertical', spacing = '3dp')

            ticker = Label(text = '[b]' + self.manager.portfolio[i] + '[/b]', markup = True, font_size = '30sp', size_hint_y = None, height = '30sp')
            ticker.bind(size = ticker.setter('text_size'))

            name = Label(text = 'test', size_hint_y = None, height = '15sp')
            name.bind(size = name.setter('text_size'))

            left.add_widget(ticker)
            left.add_widget(name)

            pct = Label(text = f"{self.sizes[i]:.1%}", font_size = '30sp', size_hint_y = None, height = '30sp', halign = 'right', pos_hint = {'center_y' : 0.5})
            pct.bind(size = pct.setter('text_size'))

            row.add_widget(left)
            row.add_widget(pct)

            self.table.add_widget(row)

            if i != len(self.manager.portfolio) - 1:
                sep = Background(size_hint_y = None, height = '1dp')
                with sep.canvas.before:
                    Color(rgba = rgba('#808080'))
                    sep.rect = Rectangle(size = sep.size, pos = sep.pos)
                sep.bind(size = sep._update_rect, pos = sep._update_rect)
                self.table.add_widget(sep)

    def switch_to_stocks(self, instance):
        # Switch to the StocksScreen
        self.manager.transition = CardTransition(direction='right')
        self.manager.get_screen('stocks').draw_table()
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