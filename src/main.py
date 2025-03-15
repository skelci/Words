import os
import random
from enum import IntEnum



class Lang(IntEnum):
    ENG = 0
    SLO = 1



class Word:
    def __init__(self, eng):
        self.word = eng.lower().strip()


    def __str__(self):
        return self.word



class Words:
    def __init__(self, words_file, cache_file, learning_factor=1.1):
        self.words_file = words_file
        self.cache_file = cache_file
        self.learning_factor = learning_factor

        self.__load_words()
        self.__load_cache()


    def __del__(self):
        self.__save_cache()
        

    def __load_words(self):
        with open(self.words_file, 'r') as f:
            words = f.read().splitlines()

            self.__words_eng = {}
            self.__words_slo = {}
            for word in words:
                eng, slo = word.split(',')
                self.__words_slo[eng] = Word(slo)
                self.__words_eng[slo] = Word(eng)


    def __load_cache(self):
        if not os.path.exists(self.cache_file):
            os.mkdir(self.cache_file)
            self.__cache = {}
            return
        
        with open(self.cache_file, 'r') as f:
            lines = f.read()
            self.__cache = {word: int(learned) for word, learned in lines.split('|')}


    def __save_cache(self):
        with open(self.cache_file, 'w') as f:
            f.write('|'.join([f'{word} {learned}' for word, learned in self.__cache.items()]))


    def get_random_word(self):
        learned_sum = sum(self.__cache.values())
        rnd_num = random.randrange(0, learned_sum)

        for word, learned in self.__cache.items():
            rnd_num -= learned
            if rnd_num <= 0:
                if random.random() < 0.5:
                    return word, Lang.ENG
                else:
                    return self.__words_slo[word], Lang.SLO
            

    def check_word(self, word_eng, word_slo, original_lang):
        if original_lang == Lang.ENG:
            word = self.__words_slo[word_eng]
            key_word = word_eng
            if word.word == word_slo:
                correct = True
        else:
            word = self.__words_eng[word_slo]
            key_word = word
            if word.word == word_eng:
                correct = True

        self.__cache[key_word] *= self.learning_factor if correct else 1 / self.learning_factor



def main():
    wordlearn = Words('res/words.txt', 'res/cache.txt')

    while True:
        word, lang = wordlearn.get_random_word()
        print(f'Word: {word} ({"ENG" if lang == Lang.ENG else "SLO"})')
        answer = input('Answer: ')
        if answer == ';':
            break
        wordlearn.check_word(word, answer, lang)

