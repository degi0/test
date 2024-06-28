import random
import tkinter as tk
from tkinter import messagebox
import requests
import xml.etree.ElementTree as ET


class WordSearchGame:
    def __init__(self, width=6, height=4):
        self.width = width
        self.height = height
        self.words = self.get_random_words(3)
        self.grid = [['' for _ in range(width)] for _ in range(height)]
        self.directions = {"가로": (0, 1), "세로": (1, 0), "대각선": (1, 1)}
        self.word_positions = {}
        self.fill_grid()

    def get_random_words(self, num_words):
        api_key = "0B84E79369ABE67D8DC67897156550E9"
        url = f"https://krdict.korean.go.kr/api/search?key={api_key}&part=word&sort=popular&num=100&method=GET"

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            items = root.findall(".//item")

            if items:
                words = [item.find('word').text for item in items if len(item.find('word').text) <= 4]
                if len(words) >= num_words:
                    return random.sample(words, num_words)

            print("API에서 적절한 단어를 찾지 못했습니다. 기본 단어 목록을 사용합니다.")
        except (requests.RequestException, ET.ParseError) as e:
            print(f"API 호출 중 오류 발생: {e}")
            print("기본 단어 목록을 사용합니다.")

        default_words = ["사과", "바나나", "딸기", "포도", "키위", "망고", "오렌지", "레몬", "수박", "참외", "자두", "복숭아"]
        return random.sample(default_words, num_words)

    def fill_grid(self):
        self.grid = [['' for _ in range(self.width)] for _ in range(self.height)]
        self.word_positions = {}
        for word in self.words:
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                direction, (dy, dx) = random.choice(list(self.directions.items()))
                if direction == "가로":
                    y = random.randint(0, self.height - 1)
                    x = random.randint(0, self.width - len(word))
                elif direction == "세로":
                    y = random.randint(0, self.height - len(word))
                    x = random.randint(0, self.width - 1)
                else:  # 대각선
                    y = random.randint(0, self.height - len(word))
                    x = random.randint(0, self.width - len(word))

                if all(self.grid[y + i * dy][x + i * dx] == '' or self.grid[y + i * dy][x + i * dx] == word[i] for i in
                       range(len(word))):
                    for i in range(len(word)):
                        self.grid[y + i * dy][x + i * dx] = word[i]
                    self.word_positions[word] = [(y + i * dy, x + i * dx) for i in range(len(word))]
                    placed = True
                attempts += 1

            if not placed:
                print(f"'{word}'를 배치하는 데 실패했습니다. 게임을 재시작합니다.")
                return self.fill_grid()  # 재귀적으로 다시 시도

        # 빈 공간을 의미 없는 한글 음절로 채우기
        self.fill_empty_spaces()

    def fill_empty_spaces(self):
        # 자주 사용되는 초성, 중성, 종성 목록
        cho = 'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ'
        jung = 'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'
        jong = 'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ'  # 종성에는 빈 문자('')도 포함될 수 있음

        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == '':
                    # 초성, 중성, 종성을 무작위로 선택
                    c = random.choice(cho)
                    j = random.choice(jung)
                    o = random.choice(jong + ' ')  # 종성이 없을 수도 있음

                    # 유니코드 조합을 사용하여 한글 음절 생성
                    if o == ' ':
                        syllable = chr(0xAC00 + cho.index(c) * 588 + jung.index(j) * 28)
                    else:
                        syllable = chr(0xAC00 + cho.index(c) * 588 + jung.index(j) * 28 + jong.index(o) + 1)

                    self.grid[y][x] = syllable

    def get_hints(self):
        hints = []
        for word, positions in self.word_positions.items():
            y, x = positions[0]
            if positions[-1][0] == y:
                direction = "가로"
            elif positions[-1][1] == x:
                direction = "세로"
            else:
                direction = "대각선"
            hints.append(f"{word}: {direction} 방향 ({y + 1}, {x + 1})에서 시작")
        return hints

    def restart(self):
        self.words = self.get_random_words(3)
        self.fill_grid()


class GameGUI:
    def __init__(self, master, game):
        self.master = master
        self.game = game
        self.labels = []
        self.create_widgets()

    def create_widgets(self):
        self.frame = tk.Frame(self.master)
        self.frame.pack(padx=10, pady=10)

        self.create_grid()

        tk.Button(self.master, text="힌트 보기", command=self.show_hints).pack(pady=5)
        tk.Button(self.master, text="정답 보기", command=self.show_answer).pack(pady=5)
        tk.Button(self.master, text="재시작", command=self.restart_game).pack(pady=5)

    def create_grid(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.labels = []
        for y in range(self.game.height):
            row = []
            for x in range(self.game.width):
                label = tk.Label(self.frame, text=self.game.grid[y][x], width=2, height=1,
                                 borderwidth=1, relief="solid", font=('Malgun Gothic', 14))
                label.grid(row=y, column=x)
                row.append(label)
            self.labels.append(row)

    def show_hints(self):
        hints = self.game.get_hints()
        messagebox.showinfo("힌트", "\n".join(hints))

    def show_answer(self):
        colors = ['red', 'blue', 'green']
        for word, positions in self.game.word_positions.items():
            color = colors.pop(0)
            for y, x in positions:
                self.labels[y][x].config(fg=color)

    def restart_game(self):
        self.game.restart()
        self.create_grid()


def main():
    game = WordSearchGame()
    root = tk.Tk()
    root.title("숨은 단어 찾기 게임")
    GameGUI(root, game)
    root.mainloop()


if __name__ == "__main__":
    main()