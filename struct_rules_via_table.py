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
    # определяем индекс морфологического разбора в таблице
    if source_morph in source_table:
        idx = source_table.index(source_morph)
    # если индекс морфологического разбора отсутствует в таблице,
    # вернуть <unknown_tags>
    # нижнее подчеркивание обязательно, чтобы позже при split() это не стало
    # 2 отдельными строками
    else:
        return "<unknown_tags>"

    # возвращаем выходной морфологический разбор, соответствующий индексу
    return target_table[idx]


def get_first_tag(tags: str) -> str:
    """
    Функция получает список тегов и возвращает первый из них.
    пример: <det><def><sp> -> <det>
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
    elif direction == "kaz-rus":
        source_table = kaz
        target_table = rus
    elif direction == "rus-kaz":
        source_table = rus
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
        # если индекс основы слова отсутствует в таблице,
        # вернуть unknown_word
        # нижнее подчеркивание обязательно, чтобы позже при split() это не
        # стало 2 отдельными строками
        return "unknown_word"


def compare_tags(tag1: str, tag2: str) -> bool:
    """
    Функция, сравнивающая теги с учетом разных вариантов для глагола.
    <vblex> - <v>
    <vbmod> - <v>
    <vbhaver> - <v>
    <vaux> - <vaux>
    <vbser> - <vbser>
    """
    if (tag1 == "<v>" or
        tag1 == "<vblex>" or
        tag1 == "<vbmod>" or
        tag1 == "<vbhaver>") \
            and (tag2 == "<v>" or
                 tag2 == "<vblex>" or
                 tag2 == "<vbmod>" or
                 tag2 == "<vbhaver>"):
        return True
    elif tag1 == tag2:
        return True
    else:
        return False

# ==========
# code
# ==========

# определяем направление перевода
cur_direction = "eng-kaz"
if cur_direction == "eng-kaz":
    source_table = eng_tags
    target_table = kaz_tags
elif cur_direction == "kaz-eng":
    source_table = kaz_tags
    target_table = eng_tags
elif cur_direction == "rus-kaz":
    source_table = rus_tags
    target_table = kaz_tags
elif cur_direction == "kaz-rus":
    source_table = kaz_tags
    target_table = rus_tags
# если направление перевода задано неверно, выбросить exception
else:
    raise ValueError("Неправильно задано направление перевода")

# test = ["^you<prn><subj><p2><mf><sp>$ ^know<vblex><pres>$ \
    # ^that<det><dem><sg>$  # ^housing<n><sg>$ ^build<vblex><ger>$
    # ^have<vbhaver><pres><p3><sg>$ ^become<vblex><pp>$ ^the<det><def><sp>$ \
    # ^drive<vblex><subs>$ ^force<vblex><pres>$ ^of<pr>$ \
    # ^kazakhstan<np><top><sg>$ ^'s<gen>$ ^economy<n><sg>$^.<sent>$"]
# for line in test:

# Переменная для подсчета выводимых строк.
# Должна была называться count, но что-то пошло не так.
co = 0
# из stdin получеам слова с морфологическими анализами
for line in sys.stdin:
    # разбиваем строку по символу '^' (сам он при этом пропадает)
    splitted_input_str = line.split('^')

    source_words_with_tags = []
    # убираем из входной строки пустые слова, точки и пробелы
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
        # если тегов нет, не делать ничего
        else:
            continue

        source_words.append(item[:tag_idx])
        source_tags.append(item[tag_idx:])

    # определяем, границы групп тегов
    tag_borders = []
    current_tag = 0
    # последовательности тегов ищутся, начиная с самых длинных
    # поиск идет по введённому предложению слева направо
    # ближе к концу предложения длина последовательности тегов уменьшается
    while current_tag < len(source_tags):
        found = False
        # уменьшаем длину последовательности тегов ближе к концу предложения
        if len(source_tags) - current_tag >= 6:
            max_len = 6
        else:
            max_len = len(source_tags) - current_tag
        # ищем последовательности тегов, начиная с current_tag
        # если что-то найдено, current_tag смещается вправо
        for tags_len in range(max_len, 0, -1):
            if ' '.join(source_tags[current_tag:current_tag + tags_len]) in \
                                                                source_table:
                tag_borders.append(current_tag)
                current_tag += tags_len
                found = True
                break
        # если ничего не найдено, current_tag грустно вздыхает и смещается
        # вправо на 1
        if not found:
            tag_borders.append(current_tag)
            current_tag += 1
    # конец последовательности тегов тоже является границей
    tag_borders.append(len(source_tags))

    # группируем слова, исходные теги и целевые теги в одну структуру
    # namedtupple в python - аналог struct
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

        # если основ слов окажется меньше, чем тегов для целевого языка,
        # добавляем "экстра-слово"
        while len(tmp_words.split()) < len(tmp_target.split()):
            tmp_words += " extra_word"

        # объединяем сгруппированное в одну структуру и добавляем её в массив
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
        # если количество основ слов и тегов целевого языка одинаково,
        # то ничего делать не надо.
        # а вот если слов больше - то надо делать то, что написано ниже
        # ситуация, если слов меньше, решается выше добавлением "экстра-слова"
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

            # кортежи в питоне немутабельны, поэтому просто изменить одно
            # поле невозможно. надо переписывать/пересоздавать и заменять
            # всю структуру/кортеж
            w_s_t_list[i] = \
                w_s_t_list[i]._replace(words=' '.join(tmp_new_words_list))

    # переводим слова
    for i in range(len(w_s_t_list)):
        tmp_words_list = w_s_t_list[i].words.split()
        tmp_translations = []
        for word in tmp_words_list:
            tmp_tran = table_translate(direction=cur_direction,
                                       source_word=word)
            tmp_translations.append(tmp_tran)

        w_s_t_list[i] = \
            w_s_t_list[i]._replace(words=' '.join(tmp_translations))

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

    # Это та самая переменная для подсчета выводимых строк, которая
    # должна была называться count, но что-то пошло не так.
    co += 1
    sys.stdout.write(str(co) + ": " + output)
