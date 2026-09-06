import os
os.environ['KIVY_NO_ARGS'] = '1'

import random
import json
from collections import Counter
from datetime import datetime
import urllib.request
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle

Window.clearcolor = (0.06, 0.09, 0.16, 1)

# Configuração de cada modalidade suportada
GAMES = {
    "mega_sena": {
        "label": "🎰 Mega-Sena",
        "titulo": "MEGA-SENA",
        "range_max": 60,
        "qtd_dezenas": 6,
        "api_slug": "megasena",
        "cor": (0.06, 0.72, 0.51, 1),
    },
    "lotofacil": {
        "label": "🍀 Lotofácil",
        "titulo": "LOTOFÁCIL",
        "range_max": 25,
        "qtd_dezenas": 15,
        "api_slug": "lotofacil",
        "cor": (0.94, 0.58, 0.10, 1),
    },
}


class StyledButton(Button):
    def __init__(self, bg_color=(0.06, 0.72, 0.51, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.bg_color = bg_color
        self.font_size = '13sp'
        self.bold = True
        self.color = (1, 1, 1, 1)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[8])

    def set_bg_color(self, color):
        self.bg_color = color
        self.update_canvas()


class MegaSenaApp(App):
    def build(self):
        self.history_file = os.path.join(self.user_data_dir, "history.json")
        self.current_game = "mega_sena"
        self.load_history()

        root = BoxLayout(orientation='vertical', padding=15, spacing=8)

        # Adiciona a imagem de fundo (marca d'água)
        with root.canvas.before:
            Color(1, 1, 1, 0.12)
            if os.path.exists('logo.png'):
                self.bg_image = Rectangle(source='logo.png', pos=root.pos, size=root.size)
            else:
                self.bg_image = Rectangle(pos=root.pos, size=root.size)

        def update_bg(instance, value):
            self.bg_image.pos = instance.pos
            self.bg_image.size = instance.size

        root.bind(pos=update_bg, size=update_bg)

        # Cabeçalho
        self.title_label = Label(
            text="[b]ANALISADOR DE LOTERIAS PRO[/b]",
            markup=True,
            font_size='19sp',
            color=(0.22, 0.74, 0.97, 1),
            size_hint_y=None,
            height=32
        )
        root.add_widget(self.title_label)

        # Seletor de modalidade
        game_selector = BoxLayout(spacing=8, size_hint_y=None, height=42)
        self.btn_mega = StyledButton(text=GAMES["mega_sena"]["label"], bg_color=GAMES["mega_sena"]["cor"])
        self.btn_mega.bind(on_press=lambda inst: self.select_game("mega_sena"))
        self.btn_loto = StyledButton(text=GAMES["lotofacil"]["label"], bg_color=(0.25, 0.29, 0.38, 1))
        self.btn_loto.bind(on_press=lambda inst: self.select_game("lotofacil"))
        game_selector.add_widget(self.btn_mega)
        game_selector.add_widget(self.btn_loto)
        root.add_widget(game_selector)

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
        btn_layout = BoxLayout(spacing=6, size_hint_y=None, height=45)

        btn_generate = StyledButton(text="🎲 1 Jogo", bg_color=(0.06, 0.72, 0.51, 1))
        btn_generate.bind(on_press=self.generate_single_game)

        btn_check = StyledButton(text="🌐 Conferir", bg_color=(0.15, 0.39, 0.92, 1))
        btn_check.bind(on_press=self.check_online_results)

        btn_analise = StyledButton(text="📊 Análise", bg_color=(0.83, 0.68, 0.10, 1))
        btn_analise.bind(on_press=self.show_analysis)

        btn_clear = StyledButton(text="🗑️ Limpar", bg_color=(0.85, 0.25, 0.25, 1))
        btn_clear.bind(on_press=self.clear_history)

        btn_layout.add_widget(btn_generate)
        btn_layout.add_widget(btn_check)
        btn_layout.add_widget(btn_analise)
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
        self.hist_title = Label(
            text="[b]📜 Histórico - Mega-Sena[/b]",
            markup=True,
            font_size='15sp',
            color=(0.95, 0.96, 0.98, 1),
            size_hint_y=None,
            height=25
        )
        root.add_widget(self.hist_title)

        scroll = ScrollView()
        self.history_layout = GridLayout(cols=1, spacing=6, size_hint_y=None)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        scroll.add_widget(self.history_layout)
        root.add_widget(scroll)

        self.update_selector_visual()
        self.refresh_history_ui()
        return root

    # ---------- Seleção de modalidade ----------

    def select_game(self, game_key):
        self.current_game = game_key
        cfg = GAMES[game_key]
        self.hist_title.text = f"[b]📜 Histórico - {cfg['titulo'].title()}[/b]"
        self.game_panel.text = f"Modalidade: {cfg['label']} — escolha uma opção abaixo"
        self.status_label.text = "Status: Pronto"
        self.update_selector_visual()
        self.refresh_history_ui()

    def update_selector_visual(self):
        ativo = GAMES[self.current_game]["cor"]
        inativo = (0.25, 0.29, 0.38, 1)
        self.btn_mega.set_bg_color(ativo if self.current_game == "mega_sena" else inativo)
        self.btn_loto.set_bg_color(ativo if self.current_game == "lotofacil" else inativo)

    # ---------- Geração de jogos ----------

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
        cfg = GAMES[self.current_game]
        numbers = sorted(random.sample(range(1, cfg["range_max"] + 1), cfg["qtd_dezenas"]))
        str_numbers = " - ".join(f"{n:02d}" for n in numbers)
        now = datetime.now().strftime("%d/%m %H:%M")

        game_data = {
            "jogo": self.current_game,
            "data": now,
            "dezenas": numbers,
            "str_dezenas": str_numbers,
        }
        self.history.insert(0, game_data)
        self.save_history()

        self.game_panel.text = f"Último Jogo ({cfg['titulo'].title()}): [b][color=34d399]{str_numbers}[/color][/b]"
        self.game_panel.markup = True

    # ---------- Conferência online ----------

    def check_online_results(self, instance):
        cfg = GAMES[self.current_game]
        self.status_label.text = "Status: Buscando resultado oficial..."
        try:
            url = f"https://loteriascaixa-api.herokuapp.com/api/{cfg['api_slug']}/latest"
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

    # ---------- Análise de frequência ----------

    def show_analysis(self, instance):
        cfg = GAMES[self.current_game]
        jogos = [item for item in self.history if item.get("jogo", "mega_sena") == self.current_game]

        if not jogos:
            self.status_label.text = f"Status: Sem jogos salvos de {cfg['titulo'].title()} para analisar."
            return

        contador = Counter()
        for item in jogos:
            for n in item.get("dezenas", []):
                contador[n] += 1

        total_numeros_possiveis = cfg["range_max"]
        mais_comuns = contador.most_common()
        menos_comuns = sorted(contador.items(), key=lambda x: x[1])

        nunca_saiu = [n for n in range(1, total_numeros_possiveis + 1) if n not in contador]

        linhas = []
        linhas.append(f"[b]Análise — {cfg['titulo'].title()}[/b]")
        linhas.append(f"Baseado em {len(jogos)} jogo(s) gerado(s)\n")

        linhas.append("[b][color=34d399]🔥 Mais frequentes:[/color][/b]")
        for numero, qtd in mais_comuns[:8]:
            linhas.append(f"  {numero:02d}  —  {qtd}x")

        linhas.append("")
        linhas.append("[b][color=f97316]❄️ Menos frequentes:[/color][/b]")
        for numero, qtd in menos_comuns[:8]:
            linhas.append(f"  {numero:02d}  —  {qtd}x")

        if nunca_saiu:
            linhas.append("")
            preview = ", ".join(f"{n:02d}" for n in nunca_saiu[:15])
            extra = "..." if len(nunca_saiu) > 15 else ""
            linhas.append(f"[b]🚫 Nunca gerados ({len(nunca_saiu)}):[/b] {preview}{extra}")

        texto_final = "\n".join(linhas)

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        scroll = ScrollView()
        label = Label(
            text=texto_final,
            markup=True,
            font_size='13sp',
            color=(0.92, 0.94, 0.97, 1),
            size_hint_y=None,
            halign='left',
            valign='top',
        )
        label.bind(width=lambda inst, w: setattr(label, 'text_size', (w, None)))
        label.bind(texture_size=lambda inst, ts: setattr(label, 'height', ts[1]))
        scroll.add_widget(label)
        content.add_widget(scroll)

        btn_fechar = StyledButton(text="Fechar", bg_color=(0.15, 0.39, 0.92, 1), size_hint_y=None, height=42)
        content.add_widget(btn_fechar)

        popup = Popup(
            title=f"📊 Análise de Frequência",
            content=content,
            size_hint=(0.9, 0.8),
        )
        btn_fechar.bind(on_press=popup.dismiss)
        popup.open()

    # ---------- Histórico ----------

    def clear_history(self, instance):
        cfg = GAMES[self.current_game]
        self.history = [item for item in self.history if item.get("jogo", "mega_sena") != self.current_game]
        self.save_history()
        self.status_label.text = f"Status: Histórico de {cfg['titulo'].title()} apagado."
        self.game_panel.text = "Histórico limpo com sucesso."
        self.refresh_history_ui()

    def refresh_history_ui(self, sorteadas=None):
        self.history_layout.clear_widgets()

        jogos = [item for item in self.history if item.get("jogo", "mega_sena") == self.current_game]

        if not jogos:
            lbl = Label(text="Nenhum jogo salvo nesta modalidade.", color=(0.58, 0.64, 0.72, 1), size_hint_y=None, height=30)
            self.history_layout.add_widget(lbl)
            return

        for idx, item in enumerate(jogos, 1):
            dezenas = item.get('dezenas', [])
            str_dezenas = item.get('str_dezenas', '')
            data_str = item.get('data', '')

            card_text = f"#{idx} [{data_str}] {str_dezenas}"

            if sorteadas:
                acertos = set(dezenas).intersection(set(sorteadas))
                qtd = len(acertos)
                minimo_premio = 11 if self.current_game == "lotofacil" else 4
                if qtd >= minimo_premio:
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
