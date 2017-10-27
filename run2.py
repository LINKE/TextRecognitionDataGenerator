import argparse
import sys, os, errno
import random
# import re
# import requests
import cv2
import math
import numpy as np

# from bs4 import BeautifulSoup
from multiprocessing import Pool
from PIL import Image, ImageFont, ImageDraw, ImageFilter
from create_dataset import createDataset

# ----------------------------------------------------------------------------------------------------------------------
def create_and_save_sample(index, text, font, out_dir, height, extension, skewing_angle, random_skew, blur, random_blur,
                           background_type, file_name=None):
    image_font = ImageFont.truetype(font=os.path.join('fonts_zh', font), size=32)
    text_width, text_height = image_font.getsize(text)

    txt_img = Image.new('L', (text_width, text_height), 255)

    txt_draw = ImageDraw.Draw(txt_img)

    txt_draw.text((0, 0), text, fill=random.randint(1, 80), font=image_font)

    random_angle = random.randint(0 - skewing_angle, skewing_angle)

    rotated_img = txt_img.rotate(skewing_angle if not random_skew else random_angle, expand=1)

    new_text_width, new_text_height = rotated_img.size

    # We create our background a bit bigger than the text
    background = None

    if background_type == 0:
        background = create_gaussian_noise_background(new_text_height + 10, new_text_width + 10)
    elif background_type == 1:
        background = create_plain_white_background(new_text_height + 10, new_text_width + 10)
    else:
        background = create_quasicrystal_background(new_text_height + 10, new_text_width + 10)

    mask = rotated_img.point(lambda x: 0 if x == 255 or x == 0 else 255, '1')

    background.paste(rotated_img, (5, 5), mask=mask)

    # Create the name for our image
    image_name = file_name if file_name else '{}_{}.{}'.format(text, str(index), extension)

    # Resizing the image to desired format
    new_width = float(text_width + 10) * (float(height) / float(text_height + 10))
    image_on_background = background.resize((int(new_width), height), Image.ANTIALIAS)

    final_image = image_on_background.filter(
        ImageFilter.GaussianBlur(
            radius=(blur if not random_blur else random.randint(0, blur))
        )
    )

    # Save the image
    final_image.convert('RGB').save(os.path.join(out_dir, image_name))
    # print(os.path.join(out_dir, image_name))


def create_gaussian_noise_background(height, width):
    """
        Create a background with Gaussian noise (to mimic paper)
    """

    # We create an all white image
    image = np.ones((height, width)) * 255

    # We add gaussian noise
    cv2.randn(image, 235, 10)

    return Image.fromarray(image).convert('L')


def create_plain_white_background(height, width):
    """
        Create a plain white background
    """

    return Image.new("L", (width, height), 255)


def create_quasicrystal_background(height, width):
    """
        Create a background with quasicrystal (https://en.wikipedia.org/wiki/Quasicrystal)
    """

    image = Image.new("L", (width, height))
    pixels = image.load()

    frequency = random.random() * 30 + 20  # frequency
    phase = random.random() * 2 * math.pi  # phase
    rotation_count = random.randint(10, 20)  # of rotations

    for kw in range(width):
        y = float(kw) / (width - 1) * 4 * math.pi - 2 * math.pi
        for kh in range(height):
            x = float(kh) / (height - 1) * 4 * math.pi - 2 * math.pi
            z = 0.0
            for i in range(rotation_count):
                r = math.hypot(x, y)
                a = math.atan2(y, x) + i * math.pi * 2.0 / rotation_count
                z += math.cos(r * math.sin(a) * frequency + phase)
            c = int(255 - round(255 * z / rotation_count))
            pixels[kw, kh] = c  # grayscale
    return image


# ----------------------------------------------------------------------------------------------------------------------
def parse_arguments():
    """
        Parse the command line arguments of the program.
    """

    parser = argparse.ArgumentParser(description='Generate synthetic text data for text recognition.')
    parser.add_argument(
        "output_dir",
        type=str,
        nargs="?",
        help="The output directory",
        default="out2/",
    )
    # parser.add_argument(
    #     "-i",
    #     "--input_file",
    #     type=str,
    #     nargs="?",
    #     help="When set, this argument uses a specified text file as source for the text",
    #     default=""
    # )
    # parser.add_argument(
    #     "-l",
    #     "--language",
    #     type=str,
    #     nargs="?",
    #     help="The language to use, should be fr (Français), en (English), es (Español), or de (Deutsch).",
    #     default="en"
    # )
    # parser.add_argument(
    #     "-c",
    #     "--count",
    #     type=int,
    #     nargs="?",
    #     help="The number of images to be created.",
    #     default=100  # 1000
    # )
    # parser.add_argument(
    #     "-n",
    #     "--include_numbers",
    #     action="store_true",
    #     help="Define if the text should contain numbers. (NOT IMPLEMENTED)",
    #     default=False
    # )
    # parser.add_argument(
    #     "-s",
    #     "--include_symbols",
    #     action="store_true",
    #     help="Define if the text should contain symbols. (NOT IMPLEMENTED)",
    #     default=False
    # )
    parser.add_argument(
        "-w",
        "--length",
        type=int,
        nargs="?",
        help="Define how many words should be included in each generated sample. If the text source is Wikipedia, this is the MINIMUM length",
        default=1  # 1
    )
    parser.add_argument(
        "-r",
        "--random",
        action="store_true",
        help="Define if the produced string will have variable word count (with --length being the maximum)",
        default=False
    )
    parser.add_argument(
        "-f",
        "--format",
        type=int,
        nargs="?",
        help="Define the height of the produced images",
        default=32,
    )
    parser.add_argument(
        "-t",
        "--thread_count",
        type=int,
        nargs="?",
        help="Define the number of thread to use for image generation",
        default=1,
    )
    parser.add_argument(
        "-e",
        "--extension",
        type=str,
        nargs="?",
        help="Define the extension to save the image with",
        default="jpg",
    )
    parser.add_argument(
        "-k",
        "--skew_angle",
        type=int,
        nargs="?",
        help="Define skewing angle of the generated text. In positive degrees",
        default=0,  # 0-12
    )
    parser.add_argument(
        "-rk",
        "--random_skew",
        action="store_true",
        help="When set, the skew angle will be randomized between the value set with -k and it's opposite",
        default=True,  # False
    )
    # parser.add_argument(
    #     "-wk",
    #     "--use_wikipedia",
    #     action="store_true",
    #     help="Use Wikipedia as the source text for the generation, using this paremeter ignores -r, -n, -s",
    #     default=False,
    # )
    parser.add_argument(
        "-bl",
        "--blur",
        type=int,
        nargs="?",
        help="Apply gaussian blur to the resulting sample. Should be an integer defining the blur radius",
        default=0,  # 0,1
    )
    parser.add_argument(
        "-rbl",
        "--random_blur",
        action="store_true",
        help="When set, the blur radius will be randomized between 0 and -bl.",
        default=False
    )

    parser.add_argument(
        "-b",
        "--background",
        type=int,
        nargs="?",
        help="Define what kind of background to use. 0: Gaussian Noise, 1: Plain white, 2: Quasicrystal",
        default=0,
    )

    return parser.parse_args()


def load_dict(name):
    """
        Read the dictionnary file and returns all words in it.
        http://www.cnblogs.com/zhangray/p/7118972.html
    """

    dict = []
    with open(os.path.join('lexicon', 'data', name + '.txt'), 'r') as d:
        dict = d.read().splitlines() #d.readlines()
    return dict


def load_fonts():
    """
        Load all fonts in the fonts directory
    """

    return [font for font in os.listdir('fonts_zh')]


# def create_strings_from_file(filename, count):
#     """
#         Create all strings by reading lines in specified files
#     """
#
#     strings = []
#
#     with open(filename, 'r') as f:
#         lines = [l.strip()[0:200] for l in f.readlines()]
#         if len(lines) == 0:
#             raise Exception("No lines could be read in file")
#         while len(strings) < count:
#             if len(lines) > count - len(strings):
#                 strings.extend(lines[0:count - len(strings)])
#             else:
#                 strings.extend(lines)
#
#     return strings

# def create_strings_from_dict(length, allow_variable, count, lang_dict):
#     """
#         Create all strings by picking X random word in the dictionnary
#     """
#
#     dict_len = len(lang_dict)
#     strings = []
#     for _ in range(0, count):
#         current_string = ""
#         for _ in range(0, random.randint(1, length) if allow_variable else length):
#             current_string += lang_dict[random.randrange(dict_len)][:-1]
#             current_string += ' '
#         strings.append(current_string[:-1])
#     return strings


# def create_strings_from_wikipedia(minimum_length, count, lang):
#     """
#         Create all string by randomly picking Wikipedia articles and taking sentences from them.
#     """
#     sentences = []
#
#     while len(sentences) < count:
#         # We fetch a random page
#         page = requests.get('https://{}.wikipedia.org/wiki/Special:Random'.format(lang))
#
#         soup = BeautifulSoup(page.text, 'html.parser')
#
#         for script in soup(["script", "style"]):
#             script.extract()
#
#         # Only take a certain length
#         lines = list(filter(
#             lambda s:
#                 len(s.split(' ')) > minimum_length
#                 and not "Wikipedia" in s
#                 and not "wikipedia" in s,
#             [
#                 ' '.join(re.findall(r"[\w']+", s.strip()))[0:200] for s in soup.get_text().splitlines()
#             ]
#         ))
#
#         # Remove the last lines that talks about contributing
#         sentences.extend(lines[0:max([1, len(lines) - 5])])
#
#     return sentences[0:count]

def main():
    """
        Description: Main function
    """

    # Argument parsing
    args = parse_arguments()

    # Create the directory if it does not exist.
    try:
        os.makedirs(args.output_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # Creating word list
    # dict = load_dict('chinese_gb3755')

    # Create font (path) list
    fonts = load_fonts()

    # Creating synthetic sentences (or word)
    # strings = []

    '''
    image_list_[dict.abbr].txt
    [dict.abbr]/[dict.index]_[font.abbr]_[skew.value]_[blur.value]_[bg.value].jpg
    eg:
    image_list_word_pyu.txt
    - word_pyu/1_fsgb_0_1_0.jpg
    
    label_list_[dict.abbr].txt
    [dict.index.value]
    eg:
    label_list_word_pyu.txt
    - X
    
    [combine]
    image_list.txt
    > image_list_[dict.abbr].txt
    label_list.txt
    > label_list_[dict.abbr].txtprint
    '''
    dict_map = {
        'ascii': 'ascii',
        'chinese_gb3755': 'chi_gb',
        'chinese_name_sim': 'chi_name',
        'word_pinyin_upper': 'word_pyu',
        'word_date': 'word_dt',
        'word_sequence': 'word_seq',
        'word_document': 'word_doc'
    }
    font_map = {
        'FangSong_GB2312.ttf': 'fsgb',
        'FangZhengKaiTi_GBK.ttf': 'fzkt',
        'FangZhengXiHeiJianTi.ttf': 'fzxh',
        'KaiTi_GB2312.ttf': 'ktgb',
        'MS_Vista_HeiTi.ttf': 'msht',
        'XinSongTi_GB18030.ttc': 'stgb'
    }
    skews = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    blurs = [0, 1]
    bgs   = [0, 1, 2]
    tasks = [
        {   #94
            'dict': 'ascii',
            'choice': False,
            'font': 'All',
            'skew': [0, 4, 8],
            'blur': [0, 1],
            'bg':   [0, 1, 2]
        },
        {   #3755
            'dict': 'chinese_gb3755',
            'choice': False,
            'font': 'All',
            'skew': [0, 4, 8],
            'blur': [0, 1],
            'bg':   [0, 1, 2]
        },
        {   #2907
            'dict': 'chinese_name_sim',
            'choice': False,
            'font': 'All',
            'skew': [0, 4, 8],
            'blur': [0, 1],
            'bg': [0, 1, 2]
        },
        {   #3755
            'dict': 'word_pinyin_upper',
            'choice': False,
            'font': [], #random
            'skew': [], #random
            'blur': [], #random
            'bg':   []  #random
        },
        {   #108114
            'dict': 'word_date',
            'choice': 10000,
            'font': [], #random
            'skew': [], #random
            'blur': [], #random
            'bg':   []  #random
        },
        {   #11179
            'dict': 'word_sequence',
            'choice': False,
            'font': [], #random
            'skew': [], #random
            'blur': [], #random
            'bg':   []  #random
        },
        {   #12
            'dict': 'word_document',
            'choice': False,
            'font': 'All',
            'skew': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            'blur': [0, 1],
            'bg':   [0, 1, 2]
        }
    ][3:4]
    print(tasks)
    return

    base_dir = 'out2'
    log_file = open(os.path.join(base_dir, 'log.txt'), 'w')

    height = args.format
    extension = args.extension
    random_skew = args.random_skew
    random_blur = args.random_blur

    task_total = 0
    for task in tasks:
        # print(task)
        dict = task['dict']
        dict_abbr = dict_map[dict]
        dict_strs = load_dict(dict)
        dict_strs_len = len(dict_strs)
        dict_strs_len_bak = dict_strs_len
        if task['choice']:
            dict_strs = random.sample(dict_strs, task['choice'])
            dict_strs_len = len(dict_strs)
        font_sels = fonts if task['font'] == 'All' else []
        font_random = len(font_sels) == 0
        font_abbrs = [font_map[_] for _ in font_sels]
        skew_sels = task['skew']
        skew_random = len(skew_sels) == 0
        blur_sels = task['blur']
        blur_random = len(blur_sels) == 0
        bg_sels = task['bg']
        bg_random = len(bg_sels) == 0

        log_info = '---------->', dict, '(', dict_abbr, ')', '(len:', dict_strs_len_bak, '->', dict_strs_len, ')', \
                   '(font:', font_abbrs, ')', '(skew:', skew_sels, ')', '(blur:', blur_sels, ')', '(bg:', bg_sels, ')'
        print(*log_info)
        print(*log_info, file=log_file)
        # create directory
        out_dir = os.path.join(base_dir, dict_abbr)
        try:
            os.makedirs(out_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        # file log
        image_list_file = open(os.path.join(base_dir, 'image_list_' + dict_abbr + '.txt'), 'w')
        label_list_file = open(os.path.join(base_dir, 'label_list_' + dict_abbr + '.txt'), 'w')
        image_list = []
        label_list = []

        dict_total = 0
        for d_index in range(dict_strs_len):
            dict_str = dict_strs[d_index]
            if font_random: font_sels = [random.choice(fonts)]
            for font_name in font_sels:
                font_abbr = font_map[font_name]
                if skew_random: skew_sels = [random.choice(skews)]
                for skew_val in skew_sels:
                    if blur_random: blur_sels = [random.choice(blurs)]
                    for blur_val in blur_sels:
                        if bg_random: bg_sels = [random.choice(bgs)]
                        for bg_val in bg_sels:
                            file_name = str(d_index) + '_' + str(font_abbr) + '_' + str(skew_val) + '_' + str(blur_val) + '_' + str(bg_val) + '.' + extension

                            create_and_save_sample(d_index, dict_str, font_name, out_dir, height, extension,
                                                   skew_val, random_skew, blur_val, random_blur, bg_val, file_name)

                            # print(dict_abbr + '/' + file_name, file=image_list_file)
                            # print(dict_str, file=label_list_file)
                            image_list.append(dict_abbr + '/' + file_name)
                            label_list.append(dict_str)
                            dict_total += 1

        task_total += dict_total
        print('total:', dict_total)
        print('total:', dict_total, file=log_file)
        image_list_file.write('\n'.join(image_list))
        # image_list_file.flush()
        image_list_file.close()
        label_list_file.write('\n'.join(label_list))
        # label_list_file.flush()
        label_list_file.close()

    print('total-all:', task_total)
    print('total-all:', task_total, file=log_file)
    log_file.flush()
    log_file.close()


    # dict_len = len(dict)
    # for i in range(0, len(fonts)):
    #     font = fonts[i]
    #     print(font)
    #     out_dir = 'out2/image/' + font.split('.')[0] + '/'
    #     try:
    #         os.makedirs(out_dir)
    #     except OSError as e:
    #         if e.errno != errno.EEXIST:
    #             raise
    #     for j in range(0, dict_len):
    #         index = i * dict_len + j
    #         text = dict[j]
    #         print(index)
    #         # font = fonts[0]
    #         # out_dir = 'out2/image/'  # args.output_dir
    #         height = args.format
    #         extension = args.extension
    #         skewing_angle = 0  # args.skew_angle
    #         random_skew = args.random_skew
    #         blur = 0  # args.blur
    #         random_blur = args.random_blur
    #         background_type = 0  # args.background
    #         create_and_save_sample(index, text, font, out_dir, height, extension, skewing_angle, random_skew, blur,
    #                                random_blur, background_type)

    # if args.use_wikipedia:
    #     strings = create_strings_from_wikipedia(args.length, args.count, args.language)
    # elif args.input_file != '':
    #     strings = create_strings_from_file(args.input_file, args.count)
    # else:
    #     strings = create_strings_from_dict(args.length, args.random, args.count, lang_dict)
    # strings = create_strings_from_dict(args.length, args.random, args.count, dict)

    # string_count = len(strings)
    #
    # p = Pool(args.thread_count)
    # p.starmap(
    #     create_and_save_sample,
    #     zip(
    #         [i for i in range(0, string_count)],
    #         strings,
    #         [fonts[random.randrange(0, len(fonts))] for _ in range(0, string_count)],
    #         [args.output_dir] * string_count,
    #         [args.format] * string_count,
    #         [args.extension] * string_count,
    #         [args.skew_angle] * string_count,
    #         [args.random_skew] * string_count,
    #         [args.blur] * string_count,
    #         [args.random_blur] * string_count,
    #         [args.background] * string_count,
    #     )
    # )
    # p.terminate()

def combine():
    dict_list = [
        'ascii',
        # 'chi_gb',
        'word_pyu',
        'word_dt',
        'word_seq',
        'word_doc'
    ]
    image_list = []
    label_list = []
    base_dir = 'out2'
    total = 0
    for dict in dict_list:
        with open(os.path.join(base_dir, 'image_list_' + dict + '.txt'), 'r') as d:
            image_list.extend(d.read().splitlines())
        with open(os.path.join(base_dir, 'label_list_' + dict + '.txt'), 'r') as d:
            label_list.extend(d.read().splitlines())
        print('+', dict, len(image_list) - total)
        total = len(image_list)
    # print(image_list)
    with open(os.path.join(base_dir, 'image_list.txt'), 'w') as f:
        f.write('\n'.join(image_list))
    with open(os.path.join(base_dir, 'label_list.txt'), 'w') as f:
        f.write('\n'.join(label_list))
    print('match:', len(image_list) == len(label_list))
    print('total:', len(image_list))


def create_ds():
    base_dir = 'out2'
    image_list = []
    label_list = []
    with open(os.path.join(base_dir, 'image_list.txt'), 'r') as d:
        image_list = d.read().splitlines()
    with open(os.path.join(base_dir, 'label_list.txt'), 'r') as d:
        label_list = d.read().splitlines()
    dir = base_dir + '/'
    image_list = [dir + im for im in image_list]
    # print(image_list[0])
    # print(label_list[0])
    ds_file = os.path.join(base_dir, 'image_train')
    createDataset(ds_file, image_list, label_list)


if __name__ == '__main__':
    sel = input("1.main(default) 2.combine 3.create_ds: ")
    if sel == '1':
        print('mian')
        main()
    elif sel == '2':
        print('combine')
        combine()
    elif sel == '3':
        print('create_ds')
        create_ds()
