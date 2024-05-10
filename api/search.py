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
    # Исключаемые по краям символы
    trim_symbols = ":;-–—.,<>\'\\\""
    
    # Вес слова в зависимости от его части речи
    part_of_speach_weight = {
            'NOUN': 5,
            'VERB': 5,
            'ADJF': 3,
            'ADVB': 3
        }
    
    # Служебные части речи для исключения
    functors_pos = {'INTJ', 'PRCL', 'CONJ', 'PREP'}
    
    # Инициализация объекта pymorphy2
    pymorphy2_311_hotfix()
    morth = pymorphy2.MorphAnalyzer()
    
    def __init__(self, start_string):
        self.start_string = start_string

    def get_search_words_list_with_weight(self):
        # pymorphy2_311_hotfix()
        # morth = pymorphy2.MorphAnalyzer()
        result_list = list()
        
        raw_list = self.start_string.lower().split()

        # Сортируем на слова из кириллических символов и на остальные
        for word in raw_list:
            trim_word = word.strip(self.trim_symbols)
            if not re.search(r'(?i)[^а-яё]', trim_word):
                parsing_word = self.morth.parse(trim_word)[0]
                if parsing_word.tag.POS not in self.functors_pos:
                    if parsing_word.tag.POS in self.part_of_speach_weight:
                        weight = self.part_of_speach_weight[parsing_word.tag.POS]
                    else:
                        weight = 1
                    
                    result_list.append([parsing_word.normal_form, weight])
            else:
                result_list.append([trim_word, 10])
                
        return result_list
    
    def get_search_words_list(self):
        # pymorphy2_311_hotfix()
        # morth = pymorphy2.MorphAnalyzer()
        result_list = list()
        
        raw_list = self.start_string.lower().split()

        # Сортируем на слова из кириллических символов и на остальные
        for word in raw_list:
            trim_word = word.strip(self.trim_symbols)
            # Если слово состоит из кириллических символов
            if not re.search(r'(?i)[^а-яё]', trim_word):
                # Берём наиболее вероятный вариант
                parsing_word = self.morth.parse(trim_word)[0]
                if parsing_word.tag.POS not in self.functors_pos:
                    result_list.append(parsing_word.normal_form)
            # Если слово состоит из некириллических символов, то просто добавляем
            else:
                result_list.append(trim_word)

        return result_list
        
        