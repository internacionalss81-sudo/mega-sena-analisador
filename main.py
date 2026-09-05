import json, os, random
from collections import Counter
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

APP_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(APP_DIR, "history.json")

SAMPLE_RESULTS = [
    [4,11,23,37,44,58],[2,9,18,31,47,53],[7,14,21,32,45,60],
    [1,12,26,35,41,54],[5,16,22,34,49,57],[3,10,27,38,43,55],
    [6,15,24,36,48,52],[8,13,20,29,42,59],[11,17,25,33,46,56],
    [4,19,28,30,40,51]
]

def normalize_result(nums):
    nums = sorted(set(int(x) for x in nums))
    if len(nums) != 6 or any(x < 1 or x > 60 for x in nums):
        raise ValueError("Digite 6 números diferentes entre 1 e 60.")
    return nums

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_history():
    if not os.path.exists(HISTORY_FILE):
        save_history(SAMPLE_RESULTS)
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return [normalize_result(x) for x in json.load(f)]
    except Exception:
        return SAMPLE_RESULTS[:]

def frequency(history):
    c = Counter()
    for draw in history:
        c.update(draw)
    return c

def score_game(game, history):
    freq = frequency(history)
    avg = sum(freq.values()) / 60.0
    freq_score = 100 - min(100, sum(abs(freq[x]-avg) for x in game) / max(1, len(history)*0.45))
    odd = sum(x % 2 for x in game)
    parity_score = 100 if odd in (2,3,4) else 55
    decades = [sum(1 for x in game if start <= x <= start+9) for start in (1,11,21,31,41,51)]
    distribution_score = 100 if max(decades) <= 2 else 75 if max(decades) == 3 else 45
    total = sum(game)
    sum_score = 100 if 120 <= total <= 240 else 65
    runs = sum(1 for a,b in zip(game, game[1:]) if b == a+1)
    consecutive_score = 100 if runs <= 1 else 70 if runs == 2 else 45
    return max(0, min(100, round(
        .30*freq_score + .20*parity_score + .20*distribution_score +
        .15*sum_score + .15*consecutive_score)))

def generate_game(history):
    freq = frequency(history)
    pool = list(range(1,61))
    weights = [max(1, freq[x]+2) for x in pool]
    while True:
        g = tuple(sorted(random.choices(pool, weights=weights, k=6)))
        if len(set(g)) == 6:
            return g

def generate_best(history, amount=10):
    candidates, seen = [], set()
    for _ in range(max(300, amount*80)):
        g = generate_game(history)
        if g not in seen:
            seen.add(g)
            candidates.append((score_game(g, history), g))
    candidates.sort(reverse=True)
    result = []
    for score, game in candidates:
        if all(len(set(game)&set(old)) <= 4 for _,old in result):
            result.append((score,game))
        if len(result) >= amount:
            break
    return result

class MegaAnalyzer(App):
    title = "Mega Analyzer"

    def build(self):
        self.history = load_history()
        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        root.add_widget(Label(text="[b]MEGA ANALYZER[/b]\nAnalisador estatístico",
                              markup=True, size_hint_y=None, height=dp(65), font_size="20sp"))
        self.output = Label(text="", markup=True, halign="left", valign="top",
                            size_hint_y=None, font_size="15sp")
        self.output.bind(texture_size=lambda o,s:setattr(o,"height",s[1]+dp(20)))
        scroll = ScrollView()
        scroll.add_widget(self.output)
        root.add_widget(scroll)
        buttons = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(5))
        for text, cb in [("Gerar 1",self.generate_one),("Gerar 10",self.generate_ten),
                         ("Analisar",self.analyze),("Adicionar",self.add_result)]:
            b=Button(text=text); b.bind(on_release=cb); buttons.add_widget(b)
        root.add_widget(buttons)
        self.refresh_home()
        return root

    def refresh_home(self):
        f=frequency(self.history)
        hot=sorted(range(1,61),key=lambda x:(-f[x],x))[:10]
        cold=sorted(range(1,61),key=lambda x:(f[x],x))[:10]
        self.output.text=(f"[b]Concursos cadastrados:[/b] {len(self.history)}\n\n"
                          f"[b]Mais frequentes:[/b] {', '.join(f'{x:02d}' for x in hot)}\n"
                          f"[b]Menos frequentes:[/b] {', '.join(f'{x:02d}' for x in cold)}\n\n"
                          "[i]O índice não é probabilidade de acerto.[/i]")

    def generate_one(self,*_):
        score,nums=generate_best(self.history,1)[0]
        self.output.text=(f"[b]JOGO GERADO[/b]\n\n[b]{' - '.join(f'{x:02d}' for x in nums)}[/b]\n\n"
                          f"Índice estatístico: [b]{score}/100[/b]\n\n"
                          "Não significa 80% de chance de ganhar.")

    def generate_ten(self,*_):
        games=generate_best(self.history,10)
        self.output.text="[b]10 JOGOS GERADOS[/b]\n\n" + "\n".join(
            f"{i:02d}. {' - '.join(f'{x:02d}' for x in nums)}  ({score}/100)"
            for i,(score,nums) in enumerate(games,1))

    def analyze(self,*_):
        f=frequency(self.history)
        hot=sorted(range(1,61),key=lambda x:(-f[x],x))[:15]
        cold=sorted(range(1,61),key=lambda x:(f[x],x))[:15]
        self.output.text=(f"[b]ANÁLISE[/b]\n\nConcursos: {len(self.history)}\n\n"
                          "[b]Mais frequentes[/b]\n"+", ".join(f"{x:02d} ({f[x]})" for x in hot)+
                          "\n\n[b]Menos frequentes[/b]\n"+", ".join(f"{x:02d} ({f[x]})" for x in cold))

    def add_result(self,*_):
        from kivy.uix.popup import Popup
        box=BoxLayout(orientation="vertical",padding=dp(10),spacing=dp(8))
        inp=TextInput(hint_text="Ex.: 04 11 23 37 44 58",multiline=False,
                      size_hint_y=None,height=dp(50))
        box.add_widget(Label(text="Digite os 6 números:")); box.add_widget(inp)
        btn=Button(text="Salvar",size_hint_y=None,height=dp(50)); box.add_widget(btn)
        popup=Popup(title="Adicionar concurso",content=box,size_hint=(.9,.45))
        def save(*_):
            try:
                nums=normalize_result(inp.text.replace(","," ").split())
                self.history.append(nums); save_history(self.history)
                popup.dismiss(); self.refresh_home()
            except Exception as e:
                inp.text=""; inp.hint_text=str(e)
        btn.bind(on_release=save); popup.open()

if __name__ == "__main__":
    MegaAnalyzer().run()
