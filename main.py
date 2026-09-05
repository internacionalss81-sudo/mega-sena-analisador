import random
import json
import os
from datetime import datetime
import urllib.request

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle

Window.clearcolor = (0.06, 0.09, 0.16, 1)

class StyledButton(Button):
    def __init__(self, bg_color=(0.06, 0.72, 0.51, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.bg_color = bg_color
        self.font_size = '16sp'
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

        root = BoxLayout(orientation='vertical', padding=15, spacing=12)

        # Header
        title = Label(
            text="[b]MEGA-SENA ANALISADOR[/b]", 
            markup=True, 
            font_size='22sp', 
            color=(0.22, 0.74, 0.97, 1),
            size_hint_y=None, 
            height=40
        )
        root.add_widget(title)

        # Painel do Jogo Atual
        self.game_panel = Label(
            text="Clique em 'Gerar Novo Jogo' para iniciar",
            font_size='15sp',
            color=(0.95, 0.96, 0.98, 1),
            size_hint_y=None,
            height=60
        )
        root.add_widget(self.game_panel)

        # Botões de Ação
        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height=50)
        
        btn_generate = StyledButton(text="🎲 Gerar Novo Jogo", bg_color=(0.06, 0.72, 0.51, 1))
        btn_generate.bind(on_press=self.generate_game)
        
        btn_check = StyledButton(text="🌐 Conferir Resultados", bg_color=(0.15, 0.39, 0.92, 1))
        btn_check.bind(on_press=self.check_online_results)
        
        btn_layout.add_widget(btn_generate)
        btn_layout.add_widget(btn_check)
        root.add_widget(btn_layout)

        # Status / Feedback
        self.status_label = Label(
            text="Status: Pronto", 
            font_size='13sp', 
            color=(0.58, 0.64, 0.72, 1),
            size_hint_y=None, 
            height=30
        )
        root.add_widget(self.status_label)

        # Área de Histórico
        hist_title = Label(
            text="[b]Meus Jogos Salvos e Resultados[/b]", 
            markup=True, 
            font_size='16sp', 
            color=(0.95, 0.96, 0.98, 1),
            size_hint_y=None, 
            height=30
        )
        root.add_widget(hist_title)

        scroll = ScrollView()
        self.history_layout = GridLayout(cols=1, spacing=8, size_hint_y=None)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        scroll.add_widget(self.history_layout)
        root.add_widget(scroll)

        self.refresh_history_ui()
        return root

    def generate_game(self, instance):
        numbers = sorted(random.sample(range(1, 61), 6))
        str_numbers = " - ".join(f"{n:02d}" for n in numbers)
        now = datetime.now().strftime("%d/%m/%Y %H:%M")

        game_data = {"data": now, "dezenas": numbers, "str_dezenas": str_numbers}
        self.history.insert(0, game_data)
        self.save_history()

        self.game_panel.text = f"Novo Jogo Gerado:\n[b][color=34d399]{str_numbers}[/color][/b]"
        self.game_panel.markup = True
        self.status_label.text = "Status: Jogo gerado e salvo com sucesso!"
        self.refresh_history_ui()

    def check_online_results(self, instance):
        self.status_label.text = "Status: Conectando à API da Loterias Caixa..."
        try:
            url = "https://loteriascaixa-api.herokuapp.com/api/megasena/latest"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
            dezenas_sorteadas = [int(n) for n in data.get('dezenas', [])]
            concurso = data.get('concurso', 'N/A')
            
            if not dezenas_sorteadas:
                raise Exception("Dados inválidos recebidos.")

            str_sorteadas = " - ".join(f"{n:02d}" for n in dezenas_sorteadas)
            self.status_label.text = f"Concurso {concurso} | Sorteio: {str_sorteadas}"
            self.refresh_history_ui(dezenas_sorteadas)

        except Exception as e:
            self.status_label.text = f"Erro na conexão: Não foi possível obter o resultado."

    def refresh_history_ui(self, sorteadas=None):
        self.history_layout.clear_widgets()
        if not self.history:
            lbl = Label(text="Nenhum jogo salvo ainda.", color=(0.58, 0.64, 0.72, 1), size_hint_y=None, height=30)
            self.history_layout.add_widget(lbl)
            return

        for item in self.history:
            dezenas = item['dezenas']
            str_dezenas = item['str_dezenas']
            data_str = item['data']
            
            card_text = f" Data: {data_str} | Apostas: {str_dezenas}"
            
            if sorteadas:
                acertos = set(dezenas).intersection(set(sorteadas))
                qtd = len(acertos)
                if qtd >= 4:
                    card_text += f"\n 🎯 [color=34d399][b]GANHOU! {qtd} ACERTOS![/b][/color]"
                else:
                    card_text += f"\n 📊 Acertos: {qtd}"

            card = Label(
                text=card_text, 
                markup=True,
                font_size='13sp', 
                size_hint_y=None, 
                height=50,
                color=(0.88, 0.91, 0.95, 1)
            )
            self.history_layout.add_widget(card)

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except:
                self.history = []
        else:
            self.history = []

    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)

if __name__ == '__main__':
    MegaSenaApp().run()
