# Программа получает на вход слова с морфологическими анализами

# пример:
# ^The<det><def><sp>$ ^text<n><sg>$ ^of<pr>$ ^the<det><def><sp>$ ^Law<n><sg>$
# ^will<vaux><inf>$ ^be<vbser><inf>$ ^publish<vblex><pp>$ ^in<pr>$
# ^the<det><def><sp>$ ^press<n><sg>$^.<sent>$

# Возвращает:
# - перевод слова, сделанный Apertium
# - теги для перевода (сейчас делаются по таблице, потом будут делаться НС)

# ==========
# imports
# ==========

import sys
from collections import namedtuple

# импортируем таблицы структурных преобразований
from tables import kaz_tags, eng_tags
# импортируем таблицы словаря
from eng_kaz_dic import eng, kaz

# ==========
# functions
# ==========


def table_struct_transform(direction: str, source_morph: str) -> str:
    """
    Функция принимает на вход морфологический разбор одного языка.
    Возвращает соответствующий ему морфологический разбор другого языка.
    Параметры:
        direction: str - направление преобразования (kaz-eng, eng-kaz)
        source_morph: str - морфологический разбор входного языка
    """

    # определяем направление перевода
    if direction == "kaz-eng":
        source_table = kaz_tags
        target_table = eng_tags

    elif direction == "eng-kaz":
        source_table = eng_tags
        target_table = kaz_tags

    # если направление перевода задано неверно, выбросить exception
    else:
        raise ValueError("Неправильно задано направление перевода")

    # определяем индекс морфологического разбора в таблице
    if source_morph in source_table:
        idx = source_table.index(source_morph)
    else:
        return "<unknown_tags>"

    # возвращаем выходной морфологический разбор, соответствующий индексу
    return target_table[idx]


def get_first_tag(tags: str) -> str:
    """
    Функция получает список тегов и возвращает первый из них.
    <det><def><sp> -> <det>
    """
    if tags == "<unknown_tags>":
        return None

    idx = tags.index('>')
    return tags[0:idx + 1]


def table_translate(direction: str, source_word: str) -> str:
    """
    Функция принимает на вход основу слова на одном языке.
    Возвращает соответствующую ей основу слова на другом языке.
    Параметры:
        direction: str - направление перевода (kaz-eng, eng-kaz)
        source_word: str - основа слова на входном языке
    """

    # определяем направление перевода
    if direction == "kaz-eng":
        source_table = kaz
        target_table = eng

    elif direction == "eng-kaz":
        source_table = eng
        target_table = kaz

    # если направление перевода задано неверно, выбросить exception
    else:
        raise ValueError("Неправильно задано направление перевода")

    # определяем индекс основы слова в таблице
    if source_word in source_table:
        idx = source_table.index(source_word)
        # возвращаем выходную основу слова, соответствующую индексу
        return target_table[idx]
    else:
        return "unknown_word"


def compare_tags(tag1: str, tag2: str) -> bool:
    """
    Функция, сравнивающая теги с учетом разных вариантов для глагола.
    <vblex> - <v>
    <vbmod> - <v>
    <vbhaver> - <v>
    <vaux> - <vaux>
    """
    if (tag1 == "<v>" or tag1 == "<vblex>" or tag1 == "<vbmod>" or tag1 == "<vbhaver>") \
            and (tag2 == "<v>" or tag2 == "<vblex>" or tag2 == "<vbmod>" or tag2 == "<vbhaver>"):
        return True
    elif tag1 == tag2:
        return True
    else:
        return False

# ==========
# code
# ==========


cur_direction = "eng-kaz"
if cur_direction == "eng-kaz":
    source_table = eng_tags
    target_table = kaz_tags
elif cur_direction == "kaz-eng":
    source_table = kaz_tags
    target_table = eng_tags


# test = ["^you<prn><subj><p2><mf><sp>$ ^know<vblex><pres>$ ^that<det><dem><sg>$ \
    # ^housing<n><sg>$ ^build<vblex><ger>$ ^have<vbhaver><pres><p3><sg>$ \
    # ^become<vblex><pp>$ ^the<det><def><sp>$ ^drive<vblex><subs>$ \
    # ^force<vblex><pres>$ ^of<pr>$ ^kazakhstan<np><top><sg>$ ^'s<gen>$ \
    # ^economy<n><sg>$^.<sent>$"]
# for line in test:

co = 0
# из stdin получеам слова с морфологическими анализами
for line in sys.stdin:
    # разбиваем строку по символу '^'
    splitted_input_str = line.split('^')

    source_words_with_tags = []
    # убираем из входной строки пустые слова, знаки препинания и пробелы
    for item in splitted_input_str:
        if item != "" and "sent" not in item:
            source_words_with_tags.append(item.strip())

    source_words = []
    source_tags = []
    # разделяем слова и теги
    for item in source_words_with_tags:
        # определяем, индекс символа, с которого начинаются теги
        if '<' in item:
            tag_idx = item.index('<')
        else:
            continue

        source_words.append(item[:tag_idx])
        source_tags.append(item[tag_idx:])

    # определяем, границы групп тегов
    tag_borders = []
    # tag_borders[0] = 0
    current_tag = 0
    while current_tag < len(source_tags):
        found = False
        if len(source_tags) - current_tag >= 6:
            max_len = 6
        else:
            max_len = len(source_tags) - current_tag

        for tags_len in range(max_len, 0, -1):
            if ' '.join(source_tags[current_tag: current_tag + tags_len]) in source_table:
                tag_borders.append(current_tag)
                current_tag += tags_len
                found = True
                break
        if not found:
            tag_borders.append(current_tag)
            current_tag += 1

    tag_borders.append(len(source_tags))

    # группируем слова, исходные теги и целевые теги в одну структуру
    # namedtupple - аналог struct
    # words - source tags - target tags
    w_s_t = namedtuple(typename="w_s_t",
                       field_names=["words", "source_tags", "target_tags"])

    w_s_t_list = []
    for i in range(len(tag_borders) - 1):
        # группируем слова
        tmp_words = ' '.join(source_words[tag_borders[i]:tag_borders[i + 1]])
        # группируем теги на исходном языке
        tmp_source = ' '.join(source_tags[tag_borders[i]:tag_borders[i + 1]])
        # получаем теги на целевом языке
        tmp_target = table_struct_transform(direction=cur_direction,
                                            source_morph=tmp_source)
        
        while len(tmp_words.split()) < len(tmp_target.split()):
            tmp_words += " extra_word"

        # объединяем сгруппированное в структуру
        tmp_struct = w_s_t(words=tmp_words, source_tags=tmp_source,
                           target_tags=tmp_target)
        w_s_t_list.append(tmp_struct)

    # сначала переводим теги
    # потом из исходных слов выбираем те части речи, которые соответствуют
    # частям речи в выходных тегах
    # пример:
    # you<prn> are<vbser> with<prep> your<det> books<n>
    # ↓
    # <prn> <vbser> <prep> <det> <n>
    # ↓
    # <prn> <n>
    # ↓
    # сен<prn> кітаптарыңмен<n>

    for i in range(len(w_s_t_list)):
        tmp_words_list = w_s_t_list[i].words.split()
        tmp_target_list = w_s_t_list[i].target_tags.split()
        if len(tmp_words_list) != len(tmp_target_list):
            tmp_source_list = w_s_t_list[i].source_tags.split()
            tmp_new_words_list = []

            for tar_tags in tmp_target_list:
                for sour_tags in tmp_source_list:
                    if compare_tags(get_first_tag(tar_tags),
                                    get_first_tag(sour_tags)):
                        idx = tmp_source_list.index(sour_tags)
                        tmp_new_words_list.append(tmp_words_list[idx])
                        break

            w_s_t_list[i] = w_s_t_list[i]._replace(words=' '.join(tmp_new_words_list))

    # переводим слова
    for i in range(len(w_s_t_list)):
        tmp_words_list = w_s_t_list[i].words.split()
        tmp_translations = []
        for word in tmp_words_list:
            tmp_tran = table_translate(direction=cur_direction, source_word=word)
            tmp_translations.append(tmp_tran)

        w_s_t_list[i] = w_s_t_list[i]._replace(words=' '.join(tmp_translations))

    # готовим результат для вывода
    output = ""
    for item in w_s_t_list:
        tmp_words_list = item.words.split()
        tmp_target_list = item.target_tags.split()
        for i in range(len(tmp_words_list)):
            output += tmp_words_list[i]
            output += tmp_target_list[i]
            output += ' '

    output = output.rstrip()
    output += '\n'

    co += 1
    sys.stdout.write(str(co) + ": " + output)
