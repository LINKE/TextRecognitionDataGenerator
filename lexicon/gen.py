import os
import datetime
import random
from pypinyin import pinyin, lazy_pinyin, Style  # pip install pypinyin


# ----------------------------------------------------------------------------------------------------------------------
def get_number():
    '''
    0-9 -> 48-57
    :return:
    '''
    return [chr(c) for c in range(48, 57 + 1)]


def get_alphabet(uppercase=True, lowercase=True):
    '''
    A-Z -> 65-90
    a-z -> 97-122
    :param uppercase:
    :param lowercase:
    :return:
    '''
    # if not(uppercase or lowercase): return []
    return [chr(c) for c in range(65, 90 + 1) if uppercase] + [chr(c) for c in range(97, 122 + 1) if lowercase]


def get_special():
    '''
    32(space) 33! 34" 35# 36$ 37% 38& 39' 40( 41) 42* 43+ 44, 45- 46. 47/
    58: 59; 60< 61= 62> 63? 64@
    91[ 92\ 93] 94^ 95_ 96`
    123{ 124| 125} 126~
    :return:
    '''
    return [chr(c) for c in range(33, 47 + 1)] + [chr(c) for c in range(58, 64 + 1)] + \
           [chr(c) for c in range(91, 96 + 1)] + [chr(c) for c in range(123, 126 + 1)]


def get_chinese_simplified():
    '''
    http://www.qingpingshan.com/jb/python/340910.html
    unicode: (0x4E00, 9FBF)=(19968, 40895), total: 20928
    :return:
    '''
    return [chr(c) for c in range(0x4e00, 0x9fbf + 1 - 26)]


def get_chinese_traditional():
    pass


def get_chinese_pinyin(str=None, uppercase=False):
    '''
    https://github.com/mozillazg/python-pinyin
    pip install pypinyin
    :param str:
    :param uppercase:
    :return:
    '''
    if str == None: str = ''.join(get_chinese_simplified())
    pys = lazy_pinyin(str)
    return [ch.upper() for ch in pys] if uppercase else pys


def get_unicode_special():
    '''
    :return:
    '''
    # x = ''.split()
    # y = sorted([hex(ord(c)) for c in x])
    cs = [0x2014, 0x2016, 0x2018, 0x2019, 0x201c, 0x201d, 0x2026, 0x2236, 0x2c9, 0x3001, 0x3002, 0x3003, 0x3005, 0x3008,
          0x3009, 0x300a, 0x300b, 0x300c, 0x300d, 0x300e, 0x300f, 0x3010, 0x3011, 0x3014, 0x3015, 0x3016, 0x3017, 0xa8,
          0xb7, 0xff01, 0xff02, 0xff07, 0xff08, 0xff09, 0xff0c, 0xff0e, 0xff1a, 0xff1b, 0xff1f, 0xff3b, 0xff3d, 0xff40,
          0xff5b, 0xff5c, 0xff5d, 0xff5e]
    return [chr(c) for c in cs]


# def get_date_range(beginDate, endDate):
#     dates = []
#     dt = datetime.datetime.strptime(beginDate, "%Y-%m-%d")
#     date = beginDate[:]
#     while date <= endDate:
#         dates.append(date)
#         dt = dt + datetime.timedelta(1)
#         date = dt.strftime("%Y-%m-%d")
#     return dates

def get_date_range(start, end, format='%Y-%m-%d'):
    '''
    https://www.zhihu.com/question/35455996
    :param start:
    :param end:
    :param format:
    :return:
    '''
    start_date = datetime.date(*start)
    end_date = datetime.date(*end)
    # print(start_date, '-', end_date)
    result = []
    curr_date = start_date
    # while curr_date != end_date:
    #     result.append("%04d%02d%02d" % (curr_date.year, curr_date.month, curr_date.day))
    #     curr_date += datetime.timedelta(1)
    # result.append("%04d%02d%02d" % (curr_date.year, curr_date.month, curr_date.day))
    while curr_date <= end_date:
        result.append(curr_date.strftime(format))
        curr_date += datetime.timedelta(1)
    return result


# ----------------------------------------------------------------------------------------------------------------------
def save_file(text, file='default', base='data'):
    with open(os.path.join(base, file), 'w') as f:
        f.write(text)


def gen_ascii(file='ascii.txt'):
    ascii_str = '\n'.join(get_number() + get_alphabet() + get_special())
    # print(ascii_str)
    save_file(ascii_str, file)


def gen_chinese_simplified(file='chinese_simplified.txt'):
    chi_sim = '\n'.join(get_chinese_simplified())
    # print(chi_sim)
    save_file(chi_sim, file)


def gen_word_pinyin_lower(file='word_pinyin_lower.txt'):
    chi_pinyin = '\n'.join(get_chinese_pinyin())
    # print(chi_pinyin)
    save_file(chi_pinyin, file)


def gen_word_pinyin_upper(file='word_pinyin_upper.txt'):
    chi_pinyin = '\n'.join(get_chinese_pinyin(uppercase=True))
    # print(chi_pinyin)
    save_file(chi_pinyin, file)


def gen_word_document(file='word_document.txt'):
    words = [
        '性别', '出生日期',
        '港澳证件号码', '证件号码',
        '签发日期', '更换日期',
        '本证有效期', '本证有效期至', '有效期限', '换证次数',
        '签发机关', '公安部出入境管理局'
    ]
    words_str = '\n'.join(words)
    # print(words_str)
    save_file(words_str, file)


def gen_word_sequence(file='word_sequence.txt'):
    years = [str(i).zfill(2) for i in range(1902, 2049 + 1)]
    dates = [str(i).zfill(2) for i in range(1, 31 + 1)]
    alphabet = get_alphabet(lowercase=False)
    alphabet_hot = ['H', 'O', 'P']
    # print(random.choice(alphabet), random.sample(alphabet, 5))
    ids = [random.choice(alphabet) + str(random.randint(1000000000, 9999999999)) for i in range(0, 1000)]
    hot_ids = [random.choice(alphabet_hot) + str(random.randint(1000000000, 9999999999)) for i in range(0, 10000)]
    words_str = '\n'.join(years + dates + ids + hot_ids)
    # print(words_str)
    save_file(words_str, file)


def gen_word_date(file='word_date.txt'):
    # date_str = '\n'.join(get_date_range((1900, 1, 1), (2099, 12, 31)))
    start = (1902, 1, 1)
    end = (2049, 12, 31)
    date_str = '\n'.join(get_date_range(start, end) + get_date_range(start, end, '%Y.%m.%d'))
    save_file(date_str, file)


def main():
    # gen_ascii('ascii.txt')
    # gen_chinese_simplified('chinese_simplified.txt')
    # gen_word_pinyin_lower('word_pinyin_lower.txt')
    # gen_word_pinyin_upper('word_pinyin_upper.txt')

    # gen_word_document('word_document.txt')
    gen_word_sequence('word_sequence.txt')
    # gen_word_date('word_date.txt')

    #
    # chi_sim = get_chinese_simplified()
    # print(len(chi_sim), ''.join(chi_sim))
    #
    # uni_sp = get_unicode_special()
    # print(len(uni_sp), ''.join(uni_sp))
    #
    # print(get_chinese_pinyin(chi_sim[0:2], uppercase=True))
    pass


if __name__ == '__main__':
    main()
