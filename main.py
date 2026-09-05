import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
os.environ['KIVY_NO_ARGS'] = '1'

import random
import json
from datetime import datetime
import urllib.request

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle

Window.clearcolor = (0.06, 0.09, 0.16, 1)

class StyledButton(Button):
    def __init__(self, bg_color=(0.06, 0.72, 0.51, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.bg_color = bg_color
        self.font_size = '14sp'
        self.bold = True
        self.color = (1, 1, 1, 1)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[8])

class MegaSenaApp(App):
    def build(self):
        self.history_file = "history.json"
        self.load_history()

        root = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # Adiciona a imagem de fundo (marca d'água)
        with root.canvas.before:
            Color(1, 1, 1, 0.12)  # Transparência suave para não atrapalhar a leitura
            if os.path.exists('logo.png'):
                self.bg_image = Rectangle(source='logo.png', pos=root.pos, size=root.size)
            else:
                self.bg_image = Rectangle(pos=root.pos, size=root.size)

        def update_bg(instance, value):
            self.bg_image.pos = instance.pos
            self.bg_image.size = instance.size

        root.bind(pos=update_bg, size=update_bg)

        # Cabeçalho
        title = Label(
            text="[b]MEGA-SENA ANALISADOR PRO[/b]", 
            markup=True, 
            font_size='20sp', 
            color=(0.22, 0.74, 0.97, 1),
            size_hint_y=None, 
            height=35
        )
        root.add_widget(title)

        # Painel de Destaque
        self.game_panel = Label(
            text="Escolha uma opção abaixo para começar",
            font_size='14sp',
            color=(0.95, 0.96, 0.98, 1),
            size_hint_y=None,
            height=50
        )
        root.add_widget(self.game_panel)

        # Campo para quantidade de jogos múltiplos
        multi_input_layout = BoxLayout(spacing=10, size_hint_y=None, height=40)
        input_label = Label(text="Qtd de jogos:", font_size='13sp', size_hint_x=0.4, color=(0.8, 0.85, 0.9, 1))
        self.qty_input = TextInput(text="5", multiline=False, input_filter='int', size_hint_x=0.3, font_size='14sp')
        
        btn_multi = StyledButton(text="⚡ Gerar Vários", bg_color=(0.55, 0.27, 0.88, 1), size_hint_x=0.5)
        btn_multi.bind(on_press=self.generate_multiple_games)
        
        multi_input_layout.add_widget(input_label)
        multi_input_layout.add_widget(self.qty_input)
        multi_input_layout.add_widget(btn_multi)
        root.add_widget(multi_input_layout)

        # Botões Principais
        btn_layout = BoxLayout(spacing=8, size_hint_y=None, height=45)
        
        btn_generate = StyledButton(text="🎲 1 Jogo", bg_color=(0.06, 0.72, 0.51, 1))
        btn_generate.bind(on_press=self.generate_single_game)
        
        btn_check = StyledButton(text="🌐 Conferir API", bg_color=(0.15, 0.39, 0.92, 1))
        btn_check.bind(on_press=self.check_online_results)

        btn_clear = StyledButton(text="🗑️ Limpar", bg_color=(0.85, 0.25, 0.25, 1))
        btn_clear.bind(on_press=self.clear_history)
        
        btn_layout.add_widget(btn_generate)
        btn_layout.add_widget(btn_check)
        btn_layout.add_widget(btn_clear)
        root.add_widget(btn_layout)

        # Status
        self.status_label = Label(
            text="Status: Pronto", 
            font_size='12sp', 
            color=(0.58, 0.64, 0.72, 1),
            size_hint_y=None, 
            height=25
        )
        root.add_widget(self.status_label)

        # Histórico
        hist_title = Label(
            text="[b]📜 Histórico de Apostas Salvas[/b]", 
            markup=True, 
            font_size='15sp', 
            color=(0.95, 0.96, 0.98, 1),
            size_hint_y=None, 
            height=25
        )
        root.add_widget(hist_title)

        scroll = ScrollView()
        self.history_layout = GridLayout(cols=1, spacing=6, size_hint_y=None)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        scroll.add_widget(self.history_layout)
        root.add_widget(scroll)

        self.refresh_history_ui()
        return root

    def generate_single_game(self, instance):
        self._add_game()
        self.status_label.text = "Status: 1 jogo gerado e salvo!"
        self.refresh_history_ui()

    def generate_multiple_games(self, instance):
        try:
            qty = int(self.qty_input.text)
            qty = max(1, min(qty, 50))
        except ValueError:
            qty = 5

        for _ in range(qty):
            self._add_game()

        self.status_label.text = f"Status: {qty} jogos gerados e salvos com sucesso!"
        self.game_panel.text = f"Gerados [b]{qty}[/b] novos jogos no histórico abaixo!"
        self.game_panel.markup = True
        self.refresh_history_ui()

    def _add_game(self):
        numbers = sorted(random.sample(range(1, 61), 6))
        str_numbers = " - ".join(f"{n:02d}" for n in numbers)
        now = datetime.now().strftime("%d/%m %H:%M")

        game_data = {"data": now, "dezenas": numbers, "str_dezenas": str_numbers}
        self.history.insert(0, game_data)
        self.save_history()

        self.game_panel.text = f"Último Jogo: [b][color=34d399]{str_numbers}[/color][/b]"
        self.game_panel.markup = True

    def check_online_results(self, instance):
        self.status_label.text = "Status: Buscando resultado oficial..."
        try:
            url = "https://loteriascaixa-api.herokuapp.com/api/megasena/latest"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
            dezenas_sorteadas = [int(n) for n in data.get('dezenas', [])]
            concurso = data.get('concurso', 'N/A')
            
            if not dezenas_sorteadas:
                raise Exception("Erro ao ler API")

            str_sorteadas = " - ".join(f"{n:02d}" for n in dezenas_sorteadas)
            self.status_label.text = f"Concurso {concurso}: {str_sorteadas}"
            self.refresh_history_ui(dezenas_sorteadas)

        except Exception:
            self.status_label.text = "Erro: Sem conexão com a API de loterias."

    def clear_history(self, instance):
        self.history = []
        self.save_history()
        self.status_label.text = "Status: Histórico apagado."
        self.game_panel.text = "Histórico limpo com sucesso."
        self.refresh_history_ui()

    def refresh_history_ui(self, sorteadas=None):
        self.history_layout.clear_widgets()
        if not self.history:
            lbl = Label(text="Nenhum jogo salvo.", color=(0.58, 0.64, 0.72, 1), size_hint_y=None, height=30)
            self.history_layout.add_widget(lbl)
            return

        for idx, item in enumerate(self.history, 1):
            dezenas = item.get('dezenas', [])
            str_dezenas = item.get('str_dezenas', '')
            data_str = item.get('data', '')
            
            card_text = f"#{idx} [{data_str}] {str_dezenas}"
            
            if sorteadas:
                acertos = set(dezenas).intersection(set(sorteadas))
                qtd = len(acertos)
                if qtd >= 4:
                    card_text += f" -> 🎯 [color=34d399][b]GANHOU ({qtd} ACERTOS)[/b][/color]"
                else:
                    card_text += f" -> 📊 Acertos: {qtd}"

            card = Label(
                text=card_text, 
                markup=True,
                font_size='12sp', 
                size_hint_y=None, 
                height=35,
                color=(0.88, 0.91, 0.95, 1)
            )
            self.history_layout.add_widget(card)

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.history = [x for x in data if isinstance(x, dict)]
            except:
                self.history = []
        else:
            self.history = []

    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)

if __name__ == '__main__':
    MegaSenaApp().run()