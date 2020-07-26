import csv

INPUT_DIR = 'Input/'
OUTPUT_DIR = 'Output/'
UTILITIES_DIR = 'Utilities/'

VERBS_LIST = []


def read_data(filename):
    """" Read scv file : #0 ArticleTitle, #1 Question, #2 Answer, #3 DifficultyFromQuestioner, #4 DifficultyFromAnswerer, #5ArticleFile
    and store them.

    :param filename: Name of file.
    :type filename: str
    :rtype: list(list(str))
    """

    # Create quintuplet to store
    quadruple = []

    file = open(filename, 'r', encoding='ISO-8859-1')
    data = file.readlines()
    file.close()

    reader = list()

    # Clean data.
    # Skip first line = header, last \n & split them.
    for line in data[1:]:
        line = line.rstrip()
        line = line.split('|')
        reader.append(line)

    # Keep only ArticleTitle, Question, Answer & Article.
    for row in reader:
        temp_quintuplet = row[0], row[1], row[2], row[5]
        quadruple.append(temp_quintuplet)
    file.close()

    return quadruple


def read_article(article_location):
    """ Read article's filtered context.

    :param article_location: The article's file location.
    :type article_location: str
    :return: The context of file.
    :rtype: str
    """

    article_text = ''

    with open(article_location, 'r', encoding='utf-8') as file:
        for line in file:
            if not line.startswith('*'):
                if not line.startswith('#'):
                    article_text += line

    return article_text


def read_util_file(filename):
    """ Get filename read it and store it to a list. This function used for read files from Utilities Project's folder.
    This folder contain useful lists of words, i prefer to use files and NOT hardcoded word lists in program.

    :param filename: The filename in utilities_dir.
    :type filename: str
    :return: A list with the words are in file.
    :rtype: list(str)
    """

    # Load file location.
    file = open(UTILITIES_DIR + filename, "r")
    text = file.read()
    file.close()

    words = text.split(",")
    return words


def read_verbs(filename):
    """" Read a file with 8567 verbs. For every verb exist all the tenses.
    Return a list of list with each verb available tenses.

    :param filename: Name of file.
    :type filename: str
    :rtype: list(list(str))
    """

    file = UTILITIES_DIR + filename
    with open(file, 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            VERBS_LIST.append([x for x in line if x])
