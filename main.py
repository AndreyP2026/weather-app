from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Triangle, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
import requests
import math
from datetime import datetime

Window.size = (480, 900)

LOCATIONS = {
    "п. Авангард (Находкинский г.о.)": {
        "lat": 42.8911, "lon": 132.7250,
        "sea_points": [(42.885, 132.770), (42.880, 132.780)],
        "desc": "бухта Прибойная"
    },
    "п. Рыбачий (Славянка)": {
        "lat": 43.3750, "lon": 131.8958,
        "sea_points": [(42.850, 131.450), (42.840, 131.470)],
        "desc": "побережье Славянки"
    },
    "бухта Лазурная (Шамора)": {
        "lat": 43.1911, "lon": 132.1206,
        "sea_points": [(43.190, 132.170), (43.185, 132.190)],
        "desc": "Уссурийский залив"
    },
    "с. Андреевка (Хасанский район)": {
        "lat": 42.4300, "lon": 130.7800,
        "sea_points": [(42.4200, 130.8200), (42.4100, 130.8400)],
        "desc": "бухта Витязь"
    }
}

TIMEZONE = "Asia/Vladivostok"


def make_label(text="", size_hint=(1, None), height=dp(28), font_size=dp(13),
               halign='left', valign='middle', bold=False,
               color=(0.1, 0.1, 0.1, 1), padding=(dp(5), 0), **kwargs):
    lbl = Label(
        text=text, size_hint=size_hint, height=height,
        font_size=font_size, halign=halign, valign=valign,
        bold=bold, color=color, padding=padding, **kwargs
    )
    lbl.text_size = (None, None)
    
    def update_text_size(instance, value):
        instance.text_size = (instance.width, instance.height)
    
    lbl.bind(size=update_text_size)
    return lbl


class WeatherIcon(Widget):
    def __init__(self, icon_type="sun", **kwargs):
        super().__init__(**kwargs)
        self.icon_type = icon_type
        self.bind(pos=self._redraw, size=self._redraw)

    def set_icon(self, icon_type):
        self.icon_type = icon_type
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        if self.width < 10 or self.height < 10:
            return
        
        with self.canvas:
            size = min(self.width, self.height)
            cx, cy = self.x + self.width / 2, self.y + self.height / 2
            r = size / 3

            if self.icon_type == "sun":
                Color(1, 0.55, 0, 1)
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    x1 = cx + (r + size * 0.05) * math.cos(rad)
                    y1 = cy + (r + size * 0.05) * math.sin(rad)
                    x2 = cx + (r + size * 0.15) * math.cos(rad)
                    y2 = cy + (r + size * 0.15) * math.sin(rad)
                    Line(points=[x1, y1, x2, y2], width=dp(3))
                Color(1, 0.84, 0, 1)
                Ellipse(pos=(cx - r, cy - r), size=(r * 2, r * 2))
                Color(1, 0.65, 0, 1)
                Line(circle=(cx, cy, r), width=dp(2))

            elif self.icon_type == "cloud":
                Color(0.88, 0.88, 0.88, 1)
                Ellipse(pos=(cx - r * 1.5, cy - r * 0.5), size=(r * 1.5, r * 1.2))
                Color(0.94, 0.94, 0.94, 1)
                Ellipse(pos=(cx - r * 0.8, cy - r * 0.2), size=(r * 1.6, r * 1.3))
                Color(0.88, 0.88, 0.88, 1)
                Ellipse(pos=(cx - r * 0.2, cy - r * 0.5), size=(r * 1.5, r * 1.2))

            elif self.icon_type in ("rain", "drizzle"):
                Color(0.7, 0.7, 0.7, 1)
                Ellipse(pos=(cx - r * 1.5, cy), size=(r * 1.5, r * 1.1))
                Ellipse(pos=(cx - r * 0.8, cy + r * 0.2), size=(r * 1.6, r * 1.2))
                Ellipse(pos=(cx - r * 0.2, cy), size=(r * 1.5, r * 1.1))
                Color(0.25, 0.41, 0.88, 1)
                for i in range(3):
                    dx = cx - r * 0.8 + i * r * 0.8
                    dy = cy - r * 0.3
                    Ellipse(pos=(dx - dp(3), dy - dp(8)), size=(dp(6), dp(12)))

            elif self.icon_type == "snow":
                Color(0.7, 0.7, 0.7, 1)
                Ellipse(pos=(cx - r * 1.5, cy), size=(r * 1.5, r * 1.1))
                Ellipse(pos=(cx - r * 0.8, cy + r * 0.2), size=(r * 1.6, r * 1.2))
                Ellipse(pos=(cx - r * 0.2, cy), size=(r * 1.5, r * 1.1))
                Color(0.53, 0.81, 0.92, 1)
                for i in range(3):
                    sx = cx - r * 0.8 + i * r * 0.8
                    sy = cy - r * 0.4
                    Line(points=[sx - dp(5), sy - dp(5), sx + dp(5), sy + dp(5)], width=dp(2))
                    Line(points=[sx - dp(5), sy + dp(5), sx + dp(5), sy - dp(5)], width=dp(2))

            elif self.icon_type == "thunder":
                Color(0.44, 0.5, 0.56, 1)
                Ellipse(pos=(cx - r * 1.5, cy), size=(r * 1.5, r * 1.1))
                Ellipse(pos=(cx - r * 0.8, cy + r * 0.2), size=(r * 1.6, r * 1.2))
                Ellipse(pos=(cx - r * 0.2, cy), size=(r * 1.5, r * 1.1))
                Color(1, 0.84, 0, 1)
                pts = [cx, cy,
                       cx - dp(8), cy - dp(12),
                       cx + dp(2), cy - dp(12),
                       cx - dp(5), cy - dp(28),
                       cx + dp(10), cy - dp(10),
                       cx, cy - dp(10)]
                Triangle(points=pts[:6])
                Triangle(points=[pts[0], pts[1], pts[8], pts[9], pts[10], pts[11]])

            elif self.icon_type == "fog":
                Color(0.66, 0.66, 0.66, 1)
                for i in range(4):
                    y = cy - dp(15) + i * dp(10)
                    Line(points=[self.x + dp(10), y, self.x + self.width - dp(10), y], width=dp(3))


class ForecastCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(40)
        self.spacing = dp(5)
        self.padding = [dp(5), dp(2)]
        
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        self.day_label = make_label(text="--", size_hint=(0.22, 1),
                                    font_size=dp(10), bold=True, halign='center',
                                    color=(0.1, 0.2, 0.6, 1))
        self.add_widget(self.day_label)
        
        self.icon = WeatherIcon(icon_type="cloud", size_hint=(None, 1), width=dp(30))
        self.add_widget(self.icon)
        
        self.desc_label = make_label(text="--", size_hint=(0.18, 1),
                                     font_size=dp(9), bold=True, halign='left',
                                     color=(0.1, 0.2, 0.5, 1))
        self.add_widget(self.desc_label)
        
        self.temp_label = make_label(text="--", size_hint=(0.13, 1),
                                     font_size=dp(9), bold=True, halign='center',
                                     color=(0.85, 0.15, 0.15, 1))
        self.add_widget(self.temp_label)
        
        self.feels_label = make_label(text="--", size_hint=(0.13, 1),
                                      font_size=dp(9), bold=True, halign='center',
                                      color=(0.55, 0.2, 0.85, 1))
        self.add_widget(self.feels_label)
        
        self.precip_label = make_label(text="--", size_hint=(0.15, 1),
                                       font_size=dp(9), bold=True, halign='center',
                                       color=(0.1, 0.5, 0.9, 1))
        self.add_widget(self.precip_label)
        
        self.wind_label = make_label(text="--", size_hint=(0.15, 1),
                                     font_size=dp(9), bold=True, halign='center',
                                     color=(0.05, 0.35, 0.8, 1))
        self.add_widget(self.wind_label)
    
    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
    
    def set_data(self, day_text, icon_type, desc, temp, feels, precip, wind):
        self.day_label.text = day_text
        self.icon.set_icon(icon_type)
        self.desc_label.text = desc
        self.temp_label.text = f"{temp}°"
        self.feels_label.text = f"{feels}°"
        self.precip_label.text = f"{precip}мм"
        self.wind_label.text = f"{wind}м/с"


def get_weather_icon_and_desc(code):
    if code == 0: return "sun", "Ясно"
    if code in (1, 2, 3): return "cloud", "Облачно"
    if code in (45, 48): return "fog", "Туман"
    if code in (51, 53, 55, 56, 57): return "drizzle", "Морось"
    if code in (61, 63, 65, 66, 67): return "rain", "Дождь"
    if code in (71, 73, 75, 77): return "snow", "Снег"
    if code in (80, 81, 82): return "rain", "Ливень"
    if code in (85, 86): return "snow", "Снегопад"
    if code in (95, 96, 99): return "thunder", "Гроза"
    return "cloud", "Неизвестно"


def get_wind_direction(degrees):
    directions = ["С", "ССВ", "СВ", "ВСВ", "В", "ВЮВ", "ЮВ", "ЮЮВ",
                  "Ю", "ЮЮЗ", "ЮЗ", "ЗЮЗ", "З", "ЗСЗ", "СЗ", "ССЗ"]
    idx = int((degrees + 11.25) / 22.5) % 16
    return directions[idx]


def fetch_marine_data(sea_points, timeout=10):
    """Получает температуру моря, высоту и период волны"""
    for lat, lon in sea_points:
        try:
            r = requests.get("https://marine-api.open-meteo.com/v1/marine", params={
                "latitude": lat, "longitude": lon,
                "current": "sea_surface_temperature,wave_height,wave_period",
                "timezone": TIMEZONE
            }, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            sea_current = data.get("current", {})
            
            sea_temp = sea_current.get("sea_surface_temperature")
            wave_height = sea_current.get("wave_height")
            wave_period = sea_current.get("wave_period")
            
            if sea_temp is not None:
                return {
                    "temp": sea_temp,
                    "wave_height": wave_height,
                    "wave_period": wave_period
                }
        except Exception:
            continue
    return None


class WeatherApp(App):
    def build(self):
        self.title = "Погода Приморья"
        
        root = BoxLayout(orientation='vertical', spacing=dp(5), padding=dp(10))
        
        # === ЗАГОЛОВОК ===
        header = make_label(text="Погода в Приморском крае", size_hint=(1, None),
                            height=dp(45), font_size=dp(18), bold=True,
                            halign='center', color=(1, 1, 1, 1))
        with header.canvas.before:
            Color(0, 0.47, 0.84, 1)
            self.header_bg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self._update_header_bg, size=self._update_header_bg)
        root.add_widget(header)
        
        # === ВЫБОР ЛОКАЦИИ ===
        loc_box = BoxLayout(orientation='vertical', size_hint=(1, None),
                            height=dp(60), spacing=dp(3), padding=[0, dp(5)])
        loc_box.add_widget(make_label(text="Выберите местоположение:",
                                      size_hint=(1, None), height=dp(20),
                                      font_size=dp(12), bold=True,
                                      color=(0.1, 0.2, 0.5, 1)))
        self.spinner = Spinner(text=list(LOCATIONS.keys())[0],
                               values=list(LOCATIONS.keys()),
                               size_hint=(1, None), height=dp(35),
                               font_size=dp(13))
        self.spinner.bind(text=self.on_location_change)
        loc_box.add_widget(self.spinner)
        root.add_widget(loc_box)
        
        # === ПРОКРУЧИВАЕМАЯ ОБЛАСТЬ ===
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(orientation='vertical', size_hint_y=None,
                                 spacing=dp(10), padding=[0, dp(5)])
        self.content.bind(minimum_height=self.content.setter('height'))
        scroll.add_widget(self.content)
        root.add_widget(scroll)
        
        # --- Блок текущей погоды ---
        # Увеличил высоту с 200 до 225, чтобы поместилась влажность
        current_box = BoxLayout(orientation='horizontal', size_hint_y=None,
                                height=dp(225), spacing=dp(10), padding=dp(5))
        
        left_box = BoxLayout(orientation='vertical', size_hint=(0.35, 1), spacing=dp(5))
        self.current_icon = WeatherIcon(icon_type="sun", size_hint=(1, 0.75))
        left_box.add_widget(self.current_icon)
        self.current_desc = make_label(text="Загрузка...", size_hint=(1, 0.25),
                                       font_size=dp(14), bold=True, halign='center',
                                       color=(0.1, 0.2, 0.7, 1))
        left_box.add_widget(self.current_desc)
        current_box.add_widget(left_box)
        
        right_box = BoxLayout(orientation='vertical', size_hint=(0.65, 1), spacing=dp(4))
        
        self.current_temp = make_label(text="--", size_hint=(1, None), height=dp(60),
                                       font_size=dp(38), bold=True, halign='left',
                                       color=(0.1, 0.4, 0.9, 1))
        right_box.add_widget(self.current_temp)
        
        self.feels_like = make_label(text="Ощущается как: --", size_hint=(1, None),
                                     height=dp(26), font_size=dp(12),
                                     color=(0.55, 0.2, 0.85, 1))
        right_box.add_widget(self.feels_like)
        
        self.wind_label = make_label(text="Ветер: --", size_hint=(1, None),
                                     height=dp(26), font_size=dp(12),
                                     color=(0.05, 0.35, 0.8, 1))
        right_box.add_widget(self.wind_label)
        
        self.clouds_label = make_label(text="Облачность: --", size_hint=(1, None),
                                       height=dp(26), font_size=dp(12),
                                       color=(0.2, 0.45, 0.8, 1))
        right_box.add_widget(self.clouds_label)
        
        self.precip_label = make_label(text="Осадки: --", size_hint=(1, None),
                                       height=dp(26), font_size=dp(12),
                                       color=(0.1, 0.5, 0.9, 1))
        right_box.add_widget(self.precip_label)
        
        # === НОВАЯ МЕТКА: ВЛАЖНОСТЬ ===
        # Зелёный цвет — ассоциируется с влагой/природой, хорошо контрастирует
        self.humidity_label = make_label(text="Влажность: --", size_hint=(1, None),
                                         height=dp(26), font_size=dp(12),
                                         color=(0.1, 0.6, 0.3, 1))
        right_box.add_widget(self.humidity_label)
        
        current_box.add_widget(right_box)
        self.content.add_widget(current_box)
        
        # --- Блок информации о море ---
        self.sea_box = BoxLayout(orientation='vertical', size_hint=(1, None),
                                 height=dp(75), spacing=dp(2), padding=[dp(10), dp(5)])
        
        with self.sea_box.canvas.before:
            Color(0.88, 0.97, 0.98, 1)
            self.sea_bg = Rectangle(pos=self.sea_box.pos, size=self.sea_box.size)
        self.sea_box.bind(pos=self._update_sea_bg, size=self._update_sea_bg)
        
        self.sea_title = make_label(text="Море (загрузка...)", size_hint=(1, None),
                                    height=dp(20), font_size=dp(12), bold=True,
                                    halign='center', color=(0, 0.35, 0.45, 1))
        self.sea_box.add_widget(self.sea_title)
        
        sea_params = BoxLayout(orientation='horizontal', size_hint=(1, 1), spacing=dp(10))
        
        self.sea_temp_label = make_label(text="--\nТемпература", size_hint=(1, 1),
                                         font_size=dp(11), bold=True, halign='center',
                                         color=(0, 0.45, 0.55, 1))
        sea_params.add_widget(self.sea_temp_label)
        
        self.wave_height_label = make_label(text="--\nВысота волны", size_hint=(1, 1),
                                            font_size=dp(11), bold=True, halign='center',
                                            color=(0.1, 0.4, 0.8, 1))
        sea_params.add_widget(self.wave_height_label)
        
        self.wave_period_label = make_label(text="--\nПериод волны", size_hint=(1, 1),
                                            font_size=dp(11), bold=True, halign='center',
                                            color=(0.2, 0.6, 0.9, 1))
        sea_params.add_widget(self.wave_period_label)
        
        self.sea_box.add_widget(sea_params)
        self.content.add_widget(self.sea_box)
        
        # --- Прогноз на 6 дней ---
        self.content.add_widget(make_label(text="Прогноз на 6 дней", size_hint=(1, None),
                                           height=dp(30), font_size=dp(14), bold=True,
                                           color=(0.1, 0.2, 0.6, 1)))
        
        headers = BoxLayout(orientation='horizontal', size_hint=(1, None),
                           height=dp(28), spacing=dp(5), padding=[dp(5), 0])
        
        with headers.canvas.before:
            Color(0.1, 0.3, 0.7, 1)
            self.headers_bg = Rectangle(pos=headers.pos, size=headers.size)
        headers.bind(pos=self._update_headers_bg, size=self._update_headers_bg)
        
        headers.add_widget(make_label(text="День", size_hint=(0.22, 1), font_size=dp(10),
                                     bold=True, halign='center', color=(1, 1, 1, 1)))
        headers.add_widget(Widget(size_hint=(None, 1), width=dp(30)))
        headers.add_widget(make_label(text="Погода", size_hint=(0.18, 1), font_size=dp(10),
                                     bold=True, halign='left', color=(1, 1, 1, 1)))
        headers.add_widget(make_label(text="Днем", size_hint=(0.13, 1), font_size=dp(10),
                                     bold=True, halign='center', color=(1, 1, 1, 1)))
        headers.add_widget(make_label(text="Ощущ.", size_hint=(0.13, 1), font_size=dp(10),
                                     bold=True, halign='center', color=(1, 1, 1, 1)))
        headers.add_widget(make_label(text="Осадки", size_hint=(0.15, 1), font_size=dp(10),
                                     bold=True, halign='center', color=(1, 1, 1, 1)))
        headers.add_widget(make_label(text="Ветер", size_hint=(0.15, 1), font_size=dp(10),
                                     bold=True, halign='center', color=(1, 1, 1, 1)))
        self.content.add_widget(headers)
        
        self.forecast_box = BoxLayout(orientation='vertical', size_hint_y=None,
                                      spacing=dp(3))
        self.forecast_box.bind(minimum_height=self.forecast_box.setter('height'))
        
        self.forecast_cards = []
        for i in range(6):
            card = ForecastCard()
            self.forecast_box.add_widget(card)
            self.forecast_cards.append(card)
        self.content.add_widget(self.forecast_box)
        
        # === НИЖНЯЯ ПАНЕЛЬ ===
        bottom_box = BoxLayout(orientation='vertical', size_hint=(1, None),
                               height=dp(75), spacing=dp(5))
        
        self.update_btn = Button(text="Обновить сейчас", size_hint=(1, None),
                                 height=dp(40), font_size=dp(14),
                                 background_color=(0, 0.47, 0.84, 1),
                                 color=(1, 1, 1, 1))
        self.update_btn.bind(on_press=lambda x: self.fetch_weather())
        bottom_box.add_widget(self.update_btn)
        
        self.status_label = make_label(text="Ожидание загрузки...", size_hint=(1, None),
                                       height=dp(25), font_size=dp(11), bold=True,
                                       halign='center', color=(0.1, 0.2, 0.5, 1))
        bottom_box.add_widget(self.status_label)
        
        root.add_widget(bottom_box)
        
        Clock.schedule_once(lambda dt: self.fetch_weather(), 0.5)
        self.update_event = Clock.schedule_interval(lambda dt: self.fetch_weather(), 30 * 60)
        
        return root
    
    def _update_header_bg(self, instance, value):
        self.header_bg.pos = instance.pos
        self.header_bg.size = instance.size
    
    def _update_headers_bg(self, instance, value):
        self.headers_bg.pos = instance.pos
        self.headers_bg.size = instance.size
    
    def _update_sea_bg(self, instance, value):
        self.sea_bg.pos = instance.pos
        self.sea_bg.size = instance.size
    
    def on_location_change(self, spinner, text):
        self.fetch_weather()
    
    def fetch_weather(self):
        self.status_label.text = "Загрузка данных..."
        self.status_label.color = (0.1, 0.2, 0.5, 1)
        self.sea_title.text = "Море (загрузка...)"
        self.sea_temp_label.text = "--\nТемпература"
        self.wave_height_label.text = "--\nВысота волны"
        self.wave_period_label.text = "--\nПериод волны"
        self.humidity_label.text = "Влажность: --"  # Сброс влажности
        
        selected = self.spinner.text
        loc = LOCATIONS[selected]
        
        def do_fetch(dt):
            try:
                # === ДОБАВЛЕН relative_humidity_2m В ЗАПРОС ===
                r1 = requests.get("https://api.open-meteo.com/v1/forecast", params={
                    "latitude": loc["lat"], "longitude": loc["lon"],
                    "current": "temperature_2m,apparent_temperature,precipitation,cloud_cover,wind_speed_10m,wind_direction_10m,weather_code,relative_humidity_2m",
                    "daily": "weather_code,temperature_2m_max,apparent_temperature_max,precipitation_sum,wind_speed_10m_max",
                    "wind_speed_unit": "ms", "timezone": TIMEZONE, "forecast_days": 7
                }, timeout=10)
                r1.raise_for_status()
                data_w = r1.json()
                
                current = data_w.get("current", {})
                daily = data_w.get("daily", {})
                
                temp = current.get("temperature_2m")
                feels = current.get("apparent_temperature")
                self.current_temp.text = f"{temp}°C" if temp is not None else "--"
                self.feels_like.text = f"Ощущается как: {feels}°C" if feels is not None else "Ощущается как: --"
                
                wind_s = current.get("wind_speed_10m")
                wind_d = current.get("wind_direction_10m")
                if wind_s is not None and wind_d is not None:
                    self.wind_label.text = f"Ветер: {wind_s:.1f} м/с, {get_wind_direction(wind_d)}"
                
                cc = current.get("cloud_cover")
                self.clouds_label.text = f"Облачность: {cc}%" if cc is not None else "Облачность: --"
                
                pr = current.get("precipitation")
                self.precip_label.text = f"Осадки: {pr:.1f} мм/ч" if pr is not None else "Осадки: 0.0 мм/ч"
                
                # === ОБНОВЛЕНИЕ ВЛАЖНОСТИ ===
                humidity = current.get("relative_humidity_2m")
                if humidity is not None:
                    self.humidity_label.text = f"Влажность: {humidity}%"
                else:
                    self.humidity_label.text = "Влажность: --"
                
                code = current.get("weather_code", 0)
                icon_type, desc = get_weather_icon_and_desc(code)
                self.current_icon.set_icon(icon_type)
                self.current_desc.text = desc
                
                try:
                    marine_data = fetch_marine_data(loc["sea_points"])
                    if marine_data is not None:
                        self.sea_title.text = f"Море ({loc['desc']})"
                        self.sea_title.color = (0, 0.35, 0.45, 1)
                        
                        sea_t = marine_data["temp"]
                        self.sea_temp_label.text = f"{sea_t:.1f}°C\nТемпература"
                        
                        wave_h = marine_data.get("wave_height")
                        if wave_h is not None:
                            self.wave_height_label.text = f"{wave_h:.1f} м\nВысота волны"
                        else:
                            self.wave_height_label.text = "нет\nВысота волны"
                        
                        wave_p = marine_data.get("wave_period")
                        if wave_p is not None:
                            self.wave_period_label.text = f"{wave_p:.0f} с\nПериод волны"
                        else:
                            self.wave_period_label.text = "нет\nПериод волны"
                    else:
                        self.sea_title.text = f"Море ({loc['desc']}): нет данных"
                        self.sea_title.color = (0.7, 0.35, 0, 1)
                except Exception:
                    self.sea_title.text = f"Море ({loc['desc']}): ошибка"
                    self.sea_title.color = (0.85, 0.15, 0.15, 1)
                
                weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
                
                times = daily.get("time", [])
                for card_idx in range(6):
                    api_idx = card_idx + 1
                    card = self.forecast_cards[card_idx]
                    
                    if api_idx < len(times):
                        try:
                            dt = datetime.fromisoformat(times[api_idx])
                            date_str = dt.strftime("%d.%m")
                            weekday_name = weekdays[dt.weekday()]
                            
                            if card_idx == 0:
                                day_name = f"Завтра\n{date_str}"
                            else:
                                day_name = f"{weekday_name}\n{date_str}"
                        except:
                            date_str = times[api_idx]
                            day_name = f"День {api_idx}\n{date_str}"
                        
                        d_code = daily["weather_code"][api_idx]
                        d_icon, d_desc = get_weather_icon_and_desc(d_code)
                        
                        d_max = daily["temperature_2m_max"][api_idx]
                        d_feels = daily["apparent_temperature_max"][api_idx]
                        d_precip = daily["precipitation_sum"][api_idx]
                        d_wind = daily["wind_speed_10m_max"][api_idx]
                        
                        card.set_data(
                            day_name,
                            d_icon,
                            d_desc,
                            f"{d_max:.0f}",
                            f"{d_feels:.0f}",
                            f"{d_precip:.1f}",
                            f"{d_wind:.1f}"
                        )
                
                now_str = datetime.now().strftime("%H:%M:%S")
                self.status_label.text = f"Обновлено в {now_str}. Автообновление через 30 мин."
                self.status_label.color = (0, 0.55, 0, 1)
                
            except requests.exceptions.Timeout:
                self.status_label.text = "Превышено время ожидания"
                self.status_label.color = (0.85, 0.15, 0.15, 1)
            except Exception as e:
                self.status_label.text = f"Ошибка: {str(e)[:60]}"
                self.status_label.color = (0.85, 0.15, 0.15, 1)
        
        from threading import Thread
        Thread(target=lambda: Clock.schedule_once(do_fetch, 0), daemon=True).start()


if __name__ == '__main__':
    WeatherApp().run()