import os
import pickle

import data_reading
from nltk.tree import Tree
from nltk import word_tokenize
from nltk.tag.stanford import CoreNLPNERTagger
from nltk.tag.stanford import CoreNLPPOSTagger


def create_parse_trees(sentences):
    """ Create Parse tree for each sentence in sentences list and return all trees in a list.
    Takes a sentence as a string; before parsing, it will be automatically tokenized and tagged by the CoreNLP Parser.

    :param sentences: Input sentences for parsing.
    :type sentences: list(str)
    :return: list(Tree)
    """

    # Create Stanford Parser.
    stanford_parser = CoreNLPPOSTagger()

    # Create a list to store all sentences parsed trees.
    parsed_sentences_trees = []

    # Create parsed trees ans store to list.
    for sentence in sentences:
        for line in stanford_parser.raw_parse(sentence):
            temp_tree = Tree.fromstring(str(line))
            parsed_sentences_trees.append(temp_tree)

    return parsed_sentences_trees


def write_parse_data(dataset, article_title, context_parsed_trees, questions_parsed_trees, context_sentences_ners):
    """ Write parse data to files used pickle library.

    The pickle module implements binary protocols for serializing and de-serializing a Python object structure.
    :param dataset: Dataset's Code
    :type dataset: str
    :param article_title: Article's title.
    :type article_title: str
    :param context_parsed_trees: List with context parsed trees.
    :type context_parsed_trees: list(list(Tree))
    :param questions_parsed_trees: List with questions parsed trees.
    :type questions_parsed_trees: list(list(Tree))
    :param context_sentences_ners: List with context sentences ners.
    :type context_sentences_ners: list(list(Tree))
    :return: Nothing
    """

    # Create a directory in Output file with name = article_title
    article_dir = data_reading.OUTPUT_DIR + dataset + '/' + article_title
    if not os.path.exists(article_dir):
        os.makedirs(article_dir)

    # Write serializing Python objects to files.

    file = open(article_dir+'\context_parsed_trees.txt', 'wb')
    pickle.dump(context_parsed_trees, file)
    file.close()

    file = open(article_dir+'\questions_parsed_trees.txt', 'wb')
    pickle.dump(questions_parsed_trees,file)
    file.close()

    file = open(article_dir+'\context_sentences_ners.txt', 'wb')
    pickle.dump(context_sentences_ners,file)
    file.close()


def read_parse_data(dataset, article_title):
    """ Read parse data from  files used pickle library.

    The pickle module implements binary protocols for serializing and de-serializing a Python object structure.

    :return: A triplet with article's context parsed trees, questions parsed trees & context sentences ners
    :rtype list(list(Tree)), list(list(Tree)), list(tuple(word,ner_tag))
    """
    article_dir = data_reading.OUTPUT_DIR + dataset + '/'  + article_title

    # Read and de-serializing Python objects from files.

    file = open(article_dir + '/context_parsed_trees.txt', 'rb')
    context_parsed_trees = pickle.load(file)
    file.close()

    file = open(article_dir + '/questions_parsed_trees.txt','rb')
    questions_parsed_trees = pickle.load(file)
    file.close()

    file = open(article_dir + '/context_sentences_ners.txt', 'rb')
    context_sentences_ners = pickle.load(file)
    file.close()

    return context_parsed_trees, questions_parsed_trees, context_sentences_ners


def find_all_ner(sentences):
    """NER Parse for each sentence in sentences list and store them to a list.

    :param sentences: Input sentences for NER parsing.
    :type sentences: list(str)
    :return: list(list(tuples))
    """

    # Create Stanford NER Tagger.
    stanford_ner_tagger = CoreNLPNERTagger()

    # Create a list to store all sentences parsed trees.
    ner_parsed_sentences = []

    """ NER LABELS(23): (job) TITLE, PERSON, 
                        LOCATION, CITY, STATE_OR_PROVINCE, COUNTRY, NATIONALITY
                        MONEY,NUMBER, ORDINAL, PERCENT, DATE, TIME, DURATION, 
                        ORGANIZATION, MISC, SET, EMAIL, URL,  RELIGION, , IDEOLOGY, CRIMINAL_CHARGE, CAUSE_OF_DEATH """

    # Find NERs for each sentence and store them to a list.
    for sentence in sentences:
        ner_parsed_sentences.append(stanford_ner_tagger.tag((word_tokenize(sentence))))

    return ner_parsed_sentences

