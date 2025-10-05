import os
import shutil
import random
from enum import IntEnum



class Lang(IntEnum):
    ENG = 0
    SLO = 1

ANSI_CLS = "\x1b[2J\x1b[3J\x1b[H"
ANSI_GOTO_UP = lambda n: f"\x1b[{n}A"
ANSI_GOTO_COL = lambda x: f"\x1b[{x}G"
ANSI_GOTO = lambda x, y: f"\x1b[{y};{x}H"

ANSI_BG_RED = "\x1b[41m"
ANSI_BG_GREEN = "\x1b[42m"
ANSI_BG_BLACK = "\x1b[40m"
ANSI_BG_RESET = "\x1b[49m"

ANSI_TEXT_RED = "\x1b[31m"
ANSI_TEXT_GREEN = "\x1b[32m"
ANSI_TEXT_WHITE = "\x1b[97m"
ANSI_TEXT_GRAY = "\x1b[90m"

# Unicode box parts
UNCB = {
    'TLD': '╔',
    'TRD': '╗',
    'BLD': '╚',
    'BRD': '╝',
    'HD':  '═',
    'VD':  '║',
    'TL':  '┌',
    'TR':  '┐',
    'BL':  '└',
    'BR':  '┘',
    'H':   '─',
    'V':   '│',
    'TJ':  '┬',
    'BJ':  '┴',
}


class Words:
    def __init__(self, words_file, cache_file, learning_factor=1.5):
        self.words_file = words_file
        self.cache_file = cache_file
        self.learning_factor = learning_factor

        self.__load_words()
        self.__load_cache()


    def __del__(self):
        self.__save_cache()


    @staticmethod
    def __format_word(word):
        return word.lower().strip()
        

    def __load_words(self):
        with open(self.words_file, 'r') as f:
            words = f.read().splitlines()

            self.__words_eng = {}
            self.__words_slo = {}
            for word in words:
                try:
                    eng, slo = word.split('-')
                    eng = self.__format_word(eng)
                    slo = self.__format_word(slo)
                except ValueError:
                    print(f'Invalid word: {word}')
                    continue
                self.__words_slo[eng] = slo
                self.__words_eng[slo] = eng


    def __load_cache(self):
        self.__cache = {word: 1.0 for word in self.__words_eng.values()}
        if not os.path.isfile(self.cache_file):
            return
        
        with open(self.cache_file, 'r') as f:
            lines = f.read().splitlines()
            for line in lines:
                if not line:
                    continue
                try:
                    word, learned = line.split('|')
                except ValueError:
                    print(f'Invalid cache line: {line}')
                    continue
                self.__cache[word] = float(learned)


    def __save_cache(self):
        with open(self.cache_file, 'w') as f:
            f.write('\n'.join([f'{word}|{learned}' for word, learned in self.__cache.items()]))


    def get_random_word(self):
        learned_sum = sum(self.__cache.values())
        rnd_num = random.random() * learned_sum

        for word, learned in self.__cache.items():
            rnd_num -= learned
            if rnd_num <= 0:
                if random.random() < 0.5:
                    return word, Lang.ENG
                else:
                    return self.__words_slo[word], Lang.SLO
            

    def check_word(self, word, answer, original_lang):
        if original_lang == Lang.ENG:
            word_eng = word
            word_slo = answer
            word_key = word_eng
        else:
            word_eng = answer
            word_slo = word
            word_key = self.__words_eng[word_slo]
        correct = False

        if original_lang == Lang.ENG:
            tmp_word = self.__words_slo[word_eng]
            if tmp_word == word_slo:
                correct = True
        else:
            tmp_word = self.__words_eng[word_slo]
            if tmp_word == word_eng:
                correct = True

        self.__cache[word_key] /= self.learning_factor if correct else 1 / self.learning_factor

        success_message = 'Correct!' if correct else 'Wrong!'
        learned_message = f'Learned: {1 / self.__cache[word_key]}'
        if not correct:
            guessing_word_message = f'Guessing word: {word}'
            correct_ans_message = f'Correct answer: {self.__words_eng[word_slo] if original_lang == Lang.SLO else self.__words_slo[word_eng]}'
            print(ANSI_BG_RED)
        else:
            print(ANSI_BG_GREEN)

        print(ANSI_GOTO(1, 14))
        print(UNCB['TL'] + UNCB['H'] * 72 + UNCB['TR'])
        print(f'{UNCB["V"]} {success_message:<70} {UNCB["V"]}')
        if not correct:   
            print(f'{UNCB["V"]} {guessing_word_message:<70} {UNCB["V"]}')
            print(f'{UNCB["V"]} {f"Your answer: {answer}":<70} {UNCB["V"]}')
            print(f'{UNCB["V"]} {correct_ans_message:<70} {UNCB["V"]}')
        print(f'{UNCB["V"]} {learned_message:<70} {UNCB["V"]}')
        print(UNCB['BL'] + UNCB['H'] * 72 + UNCB['BR'])
        print(ANSI_BG_RESET, end='')
        if correct:
            print(" " * 74)
            print(" " * 74)
            print(" " * 74)

    def print_stats(self):
        learned = sum((1 / item for item in self.__cache.values()))
        learned_sum = sum((1 for item in self.__cache.values() if item < 1))
        avg_learned = learned / len(self.__cache)
        min_learned = min(self.__cache.values())
        max_learned = max(self.__cache.values())

        STAT_OFFSET_X = 20

        def get_formated_column(stat_name, stat_value):
            return f'{" " * STAT_OFFSET_X}{UNCB["VD"]} {stat_name:<20}{round(stat_value, 4):>10} {UNCB["VD"]}'
        
        print(" " * STAT_OFFSET_X + UNCB['TLD'] + UNCB['HD'] * 32 + UNCB['TRD'])
        print(get_formated_column('Learned', learned))
        print(get_formated_column('Avg learned', avg_learned))
        print(get_formated_column('Min learned', 1 / max_learned))
        print(get_formated_column('Max learned', 1 / min_learned))
        print(get_formated_column('Words to learn', len(self.__cache) - learned_sum))
        print(get_formated_column('Total words', len(self.__cache)))
        print(" " * STAT_OFFSET_X + UNCB['BLD'] + UNCB['HD'] * 32 + UNCB['BRD'])



def main():
    wordlearn = Words('res/words.txt', 'res/cache.txt')
    running = True

    def ask_word():
        word, lang = wordlearn.get_random_word()
        answer = get_answer(word, lang)
        wordlearn.check_word(word, answer, lang)
        

    def get_answer(word, lang):
        lang_str = 'ENG' if lang == Lang.ENG else 'SLO'

        print(ANSI_GOTO(1, 10))
        print(UNCB['TL'] + UNCB['H'] * 73 + UNCB['TR'])
        print(f'{UNCB["V"]} {ANSI_TEXT_GRAY}Word to guess: {ANSI_TEXT_WHITE}{word:<50} {ANSI_TEXT_GRAY}({lang_str}) {ANSI_TEXT_WHITE}{UNCB["V"]}')
        print(f'{UNCB["V"]} {ANSI_TEXT_GRAY}Answer: {ANSI_TEXT_WHITE}{" " * 63} {UNCB["V"]}')
        print(UNCB['BL'] + UNCB['H'] * 73 + UNCB['BR'], end='')
        print(ANSI_GOTO_UP(1)+ANSI_GOTO_COL(11), end='')

        answer = input()
        if answer == ';':
            print(ANSI_GOTO(1, 22) + ANSI_TEXT_GRAY + 'Pending exit...' + ANSI_TEXT_WHITE + ' ' * 40, end='')
            answer = get_answer(word, lang)
            nonlocal running
            running = False
        return answer

    print(ANSI_CLS)
    while True:
        cols, rows = shutil.get_terminal_size(fallback=(80, 22))
        if cols < 80 or rows < 22:
            print('Terminal size is too small. Please resize to at least 80x22 and press Enter.')
            print(f'Current size: {cols}x{rows}')
            input()
            print(ANSI_CLS)
        else:
            break

    print(ANSI_GOTO(1, 22) + ANSI_TEXT_GRAY + 'Type ";" as your answer to exit.' + ANSI_TEXT_WHITE, end='')

    while running:
        print(ANSI_GOTO(1, 1))
        wordlearn.print_stats()
        print('\n')
        ask_word()

    print(ANSI_GOTO(1, 1))
    wordlearn.print_stats()
    print(ANSI_GOTO(1, 21))


if __name__ == '__main__':
    main()

