import pymorphy2
import re

# Фикс pymorphy2 для Python 3.11
def pymorphy2_311_hotfix():
    from inspect import getfullargspec
    from pymorphy2.units.base import BaseAnalyzerUnit

    def _get_param_names_311(klass):
        if klass.__init__ is object.__init__:
            return []
        args = getfullargspec(klass.__init__).args
        return sorted(args[1:])

    setattr(BaseAnalyzerUnit, '_get_param_names', _get_param_names_311)


class SearchWordsConverter:
    def __init__(self, start_string):
        self.start_string = start_string

    def get_search_words_list(self):
        pymorphy2_311_hotfix()
        morth = pymorphy2.MorphAnalyzer()

        result_list = list()
        functors_pos = {'INTJ', 'PRCL', 'CONJ', 'PREP'}

        lower_start_string = self.start_string.lower()
        raw_list = lower_start_string.split()
        kyr_words = list()
        non_kyr_words = list()

        # Сортируем на слова из кириллических символов и на остальные
        for word in raw_list:
            if not re.search(r'(?i)[^а-яё]', word):
                kyr_words.append(word)
            else:
                non_kyr_words.append(word)

        for word in kyr_words:
            # Берём наиболее вероятный вариант
            parsing_word = morth.parse(word)[0]
            if parsing_word.tag.POS not in functors_pos:
                result_list.append(parsing_word.normal_form)
            else:
                continue

        result_list.extend(non_kyr_words)
        result_list.append(self.start_string)

        return result_list