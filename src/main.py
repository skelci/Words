import os
import random
from enum import IntEnum



class Lang(IntEnum):
    ENG = 0
    SLO = 1



class Words:
    def __init__(self, words_file, cache_file, learning_factor=1.1):
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
        if not os.path.exists(self.cache_file):
            os.mkdir(self.cache_file)
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
            

    def check_word(self, word, anwser, original_lang):
        if original_lang == Lang.ENG:
            word_eng = word
            word_slo = anwser
            word_key = word_eng
        else:
            word_eng = anwser
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

        print('Correct!' if correct else 'Wrong!')
        if not correct:
            print(f'Correct answer: {self.__words_eng[word_slo] if original_lang == Lang.SLO else self.__words_slo[word_eng]}')
        print(f'Learned: {1 / self.__cache[word_key]}')

    def print_stats(self):
        learned = sum((1 / item for item in self.__cache.values()))
        avg_learned = learned / len(self.__cache)
        min_learned = min(self.__cache.values())
        max_learned = max(self.__cache.values())
        print(f'Learned: {learned}')
        print(f'Avg learned: {avg_learned}')
        print(f'Min learned: {1 / max_learned}')
        print(f'Max learned: {1 / min_learned}')



def main():
    wordlearn = Words('res/words.txt', 'res/cache.txt')

    def print_stats():
        print("\n------------------------------------------------\n")
        wordlearn.print_stats()
        print("\n------------------------------------------------\n")

    while True:
        word, lang = wordlearn.get_random_word()
        print(f'Word: {word} ({"ENG" if lang == Lang.ENG else "SLO"})')
        answer = input('Answer: ')
        if answer == ',':
            print_stats()
            continue
        if answer == ';':
            break
        wordlearn.check_word(word, answer, lang)
        print("------------------\n")

    print_stats()


if __name__ == '__main__':
    main()

