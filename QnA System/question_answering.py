import re
import math
import nltk

import data_reading

from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from collections import Counter

WORD = re.compile(r'\w+')
VERB_TAGS = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']


def yes_no(question, question_tree, sentences):
    """ Here manage questions with Yes or No as answer.
    First check if i have binary or negative question and then call the proper function to get the answer.

    :param question: Question's text.
    :type question: str
    :param question_tree: The parse tree of question.
    :type question_tree: Tree
    :param sentences: A list with all sentences.
    :type sentences: list(str)
    :return A tuple with Yes/No word and the answer text.
    :rtype (str,str) or None
    """

    question_tokens = word_tokenize(question)
    is_binary = False
    is_negative = False

    if tree_search(question_tree, 'SQ') is not None:
        is_binary = True

    # Second check for binary question if needed.
    if not is_binary:

        # Second check look for yes_no_words.
        yes_no_words = data_reading.read_util_file('Yes No Words (18).txt')
        neg_yes_no_words = data_reading.read_util_file('Negative Yes No Words (15).txt')

        # If the first word is a Verb belong to yes_no_words, i have binary question.
        if question_tokens[0] in yes_no_words:
            is_binary = True
        elif question_tokens[0] in neg_yes_no_words:
            is_negative = True
        else:
            is_binary = False

    # Check for Negative Question.
    negative_words = data_reading.read_util_file('Negative Yes No Words (15).txt')
    if question_tokens[0] in negative_words:
        is_negative = True

    # Start Question answering & return the result Yes / No or None can't find answer.
    if is_binary:
        return binary_question_answering(question_tokens, sentences, False)
    elif is_negative:
        return binary_question_answering(question_tokens, sentences, True)
    else:
        return None


def binary_question_answering(question_tokens, sentences, negative_flag):
    """ Answer binary questions by transform Question to statements and then, find if exist as a part of sentences.
    If exist the Answer is Yes else No. Also create a positive or negative answer text.

    If negative_flag == True we have a Negative binary Question so invert the answer.

    :param question_tokens:
    :type question_tokens: list(str)
    :param sentences:
    :type sentences: list(str)
    :param negative_flag:
    :type negative_flag: Boolean
    :return A tuple with Yes/No word and the answer text.
    :rtype (str,str) or None
    """
    # The answer in NO.
    answer = False

    neg_words = data_reading.read_util_file('Negative Yes No Words (15).txt')
    snow = SnowballStemmer('english')

    # Transform Question to Simple sentence, keep from second to last word - except last word/symbol '?' .
    question_statement = ' '.join(question_tokens[1:-1])

    # Clean stopwords from question_to_sentence.
    clean_question_tokens = [word for word in word_tokenize(question_statement) if word not in stopwords.words('english')]
    stemmed_question_tokens = []

    # Do stemming
    for token in clean_question_tokens:
        stemmed_question_tokens.append(snow.stem(token))

    # Look all sentences for match.
    for sentence in sentences:
        # Clean stopwords from sentence.
        clean_sentence_tokens1 = [word for word in word_tokenize(sentence)]
        clean_sentence_tokens = []

        for token in clean_sentence_tokens1:
            clean_sentence_tokens.append(snow.stem(token))

        # Here check if clean_sentence_tokens list contains all elements in clean_question_tokens list.
        if all(elem in clean_sentence_tokens for elem in stemmed_question_tokens):
            # Update Flag.
            answer = True

            # If answer contain negative word then the answer is false.
            if any(value in clean_sentence_tokens for value in neg_words):
                # Update Flag.
                answer = False

    # If question in Negative invert answer.
    if negative_flag:
        answer = not answer

    # If answer is True then the answer is Yes.
    if answer:
        answer_text = question_statement[0].upper() + question_statement[1:] + '.'
        return 'Yes', answer_text
    else:
        # Create Answer text.
        answer_text = 'Not ' + question_statement[:] + '.'
        return 'No', answer_text


def wh_familiar(question, context_parsed_trees, context_sentences_ners, target_ner_tags):
    """ Answer wh-questions with  those words:
    "when, how long, how many, how much, how old, who, whom, whose, where"

    First i search for matches at context_sentences_ners (list with NERs of each sentence) with the given target_ner_tags
    (ie. LOCATION for where questions etc) and store them at a list with sentence number & NERs at candidate_answers list.

    If the answer is only one I return it. Else remove from question the stopwords and questions words and tokenizing,
    stemming to create a statement from initial question. Search at candidate_answers, every sentence's sub-sentences
    (clauses) and at each clause i perform tokenizing, stop word removal and stemming and look for perfect match, if exist
    this i found the answer.

    If answer exist return a tuple with ners and clause else None (when None is returned at main i call other function).

    :param question: The question's text.
    :type question: str
    :param context_parsed_trees: A list with parsed tree of every sentence.
    :type context_parsed_trees: list(Trees)
    :param context_sentences_ners: A list with NERs of every sentence.
    :type context_sentences_ners: list(tuple(str,str))
    :param target_ner_tags: The NER/NERs tag/tags each question type need.
    :type target_ner_tags: list(str)
    :return: Answer or None
    :rtype: tuple(str,str) or None
    """

    answer_found = False
    answer = []

    '''' candidate_answers is a list for tuple for store the sentence number and 
    a list with location result if exist.
    
    ie. 0 ( 1, []) # Nothing in this sentence.
    ie.1 (29, ['united', 'states'])
    ie.2 (32, ['new', 'zealand', 'new', 'zealand'])
    ie.3 (34, ['germany', 'netherlands', 'denmark', 'sweden'])'''
    candidate_answers = []
    sentence_number = -1
    # Check each sentence's ners to find matches with target_tags.
    for sentence_ners in context_sentences_ners:
        sentence_number += 1
        ners = []
        current_sentence_ners = find_specific_ner_tags(sentence_ners, target_ner_tags)
        if current_sentence_ners is not None:  # If find NERs.
            ners.append(current_sentence_ners)
            pair = sentence_number, ners
            candidate_answers.append(pair)

    ''' ONLY ONE ANSWER '''
    # Check if exist only one answer.
    if len(candidate_answers) == 1:
        answer_found = True
        sentence_number, ners = candidate_answers[0]
        ners_text = ' '.join(ners[0])
        ners_text = ners_text.capitalize()
        answer = ners_text, 'Only one available Answer Found!!!'
        return answer

    ''' IF MORE THAN ONE ANSWERS. '''
    snow = SnowballStemmer('english')
    question_word = data_reading.read_util_file('Question words (9).txt')

    # Clean stopwords from question_statement.
    question_statement = [word for word in word_tokenize(question) if word not in stopwords.words('english')]
    # Clean questions words and '?' symbol  from question_statement.
    question_statement = [word for word in question_statement[:-1] if word not in question_word]

    # Do stemming.
    stemmed_question_statement = []
    for token in question_statement:
        stemmed_question_statement.append(snow.stem(token))

    # From sentences with NERs we try to match them with question.
    for sentence_number, ners in candidate_answers:

        # Get from parsed sentence all the S subtrees. A context sentence usually composed of other smaller sub-sentences (clauses).
        clauses = tree_search(context_parsed_trees[sentence_number], 'S')

        # If clauses exist.
        if clauses is not None:

            for clause in clauses:
                # Clean stopwords from sub-sentence(clause).
                clause_tokens = [word for word in word_tokenize(clause) if word not in stopwords.words('english')]

                # Do stemming
                stemmed_clause = []
                for token in clause_tokens:
                    stemmed_clause.append(snow.stem(token))

                # Here check if clause_tokens list contains all elements in questions_verbs list.
                if all(elem in stemmed_clause for elem in stemmed_question_statement):
                    answer_found = True  # Flag is Up.
                    ners_text = ' '.join(ners[0])
                    ners_text = ners_text.capitalize()
                    answer = ners_text, clause.capitalize()

    # If found_answer exist return the answer else None.
    if answer_found:
        return answer
    else:
        return None


def wh_questions(question, question_tree, sentences, context_parsed_trees):
    """ Answer all non-yes_no_questions & non-wh_familiar_questions or unanswered questions.

    First get question's verbs filter them and get all possible tenses. After search matches between question's verbs
    and sentences's tokens.

    If one answer found i return it if exist one than one or none call find_best_answer function.

    :param question: The question's text.
    :type question: str
    :param question_tree: The parse tree of question.
    :type question_tree: Tree
    :param sentences: The context sentences.
    :type sentences: list(str)
    :param context_parsed_trees: A list with parsed tree of every sentence.
    :type context_parsed_trees: list(Trees)
    :return answer
    :rtype Tuple(answer, comment on answer)
    """

    candidate_answers = []
    # Load all verbs used in questions.
    basic_verbs = data_reading.read_util_file('Yes No Words (18).txt')

    # Search at questions tree for all verb tags and get the question's verbs. Store ONLY verbs which don't exist at basic_verbs list.
    q_verbs = []
    for verb_tag in VERB_TAGS:
        verbs = tree_search(question_tree, verb_tag)
        if verbs is not None:
            for verb in verbs:
                if verb not in basic_verbs:
                    q_verbs.append(verb)

    # For every verb at question's verbs i search for all available tenses at verbs thesaurus and add them at verb list .
    q_verbs_all_tenses = []
    for verb in q_verbs:
        verb_tenses = find_all_tenses(verb)
        if verb_tenses is not None:
            for verb_tense in verb_tenses:
                q_verbs_all_tenses.append(verb_tense)

    # print(q_verbs_all_tenses)

    # Search for possible answers by find ANY match between clause tokens and verbs list.
    for tree in context_parsed_trees:
        clauses = tree_search(tree, 'S')
        if clauses is not None:
            for clause in clauses:
                clause_tokens = nltk.word_tokenize(clause)
                # Here check if clause_tokens list contains ANY elements in question's verbs list.
                if any(elem in clause_tokens for elem in q_verbs_all_tenses):
                    candidate_answers.append(clause)

    # Return answer
    if len(candidate_answers) == 0:
        answer = find_best_answer(question, sentences)
        return answer, 'Found in wh_questions -> Possible Wrong'
    elif len(candidate_answers) == 1:
        answer = candidate_answers[0]
        answer = answer.capitalize()
        return answer, 'Found in wh_questions'
    else:
        answer = find_best_answer(question, candidate_answers)
        return answer, 'Found in wh_questions -> Best possible'


def find_best_answer(question, candidate_answers):
    """ Calculate all cosine similarities between question & each candidate answer.

    Return the Best candidate answer.

    :param question: The question text.
    :type question: str
    :param candidate_answers: A list with all candidate answers.
    :type candidate_answers: list(str)
    :return: The most similar
    :rtype: str
    """
    answer = ''

    # Create question's vector.
    question_vector = create_vector(question)

    # Pair of score & answer's text.
    pairs = []
    # For sentence in sentences.
    for candidate_answer in candidate_answers:
        # Create sentence's vector.
        candidate_answer_vector = create_vector(candidate_answer)

        # Get cosine score between question & sentence vectors.
        cosine = get_cosine(question_vector, candidate_answer_vector)

        # Create pair and store it.
        pair = cosine, candidate_answer
        pairs.append(pair)

    # Find maximum cosine similarity and save best answer.
    max_score = -1
    for pair in pairs:
        score, candidate_answer = pair
        if score >= max_score:
            max_score = score
            answer = candidate_answer

    # Capitalize answer.
    answer = answer.capitalize()
    return answer


""" UTILITIES OF QUESTION ANSWERING """


def tree_search(tree, label):
    """ Search Parse's tree to get subtrees with specific label and return a list with subtrees leaves text.

    :param tree: Sentence parse tree.
    :type tree: list(Tree)
    :param label: Label we want to search.
    :type label: str
    :rtype: list(str)
    """

    tree_leaves = []

    # Search for subtrees with
    for sub_tree in tree.subtrees(lambda t: t.label() == label):
        tree_leaves.append(sub_tree.leaves())

    if len(tree_leaves) == 0:
        return None

    subtree_text = []
    for line in tree_leaves:
        temp_string = (' '.join(line))
        subtree_text.append(temp_string)

    return subtree_text


def find_specific_ner_tags(ner_parsed_sentence, target_tags):
    """ Search for target tags in a ner-ed sentence and return them.

    :param ner_parsed_sentence: A list each sentence NER's.
    :type ner_parsed_sentence: list(str)
    :param target_tags: A list with NER tags i want to find.
    :type target_tags: list(str)
    :return: list(str)
    """

    candidate_answers = []  # A list of words, which match target tags.

    # Search each pair (word, ner tag) and tag of target tags and keep only the mathces if exist.
    for word, ner_tag in ner_parsed_sentence:
        for target_tag in target_tags:
            if ner_tag == target_tag:
                candidate_answers.append(word)

    if len(candidate_answers) == 0:
        return None
    else:
        return candidate_answers


def find_all_tenses(verb):
    """ Look at verbs_list line by line until find the line with given verb.
    Return all verbs exist at given's verb line.

    :param verb: A verb
    :type verb: str
    :return: A set with verb's tenses.
    :rtype set(str) or None
    """
    for verb_list in data_reading.VERBS_LIST:
        if verb in verb_list:
            verb_set = set(verb_list)
            return verb_set

    return None


""" COSINE SIMILARITY """


def create_vector(text):
    """ Create text's frequency vector.

    :param text: The text of question/sentence.
    :type  text: str
    :return: The question/sentence's word frequency vector.
    :rtype: collections.Counter (A dictionary with key = word and value = counter of word)
    """

    words = WORD.findall(text)
    return Counter(words)


def get_cosine(question_vector, sentence_vector):
    """ Implementation of  Cosine Similarity (https://en.wikipedia.org/wiki/Cosine_similarity).

    Formula = [SUM(1,n) of Ai * Bi] / {[Square root of (SUM(1,n) Ai^2)] * [Square root of (SUM(1,n) Bi^2)]}

    :param question_vector: The question's vector.
    :type question_vector: collections.Counter
    :param sentence_vector: The sentence's vector.
    :type sentence_vector: collections.Counter
    :return: The similarity score of question & sentence vectors(from -1 to 1)
    :rtype: float
    """

    # Create intersection ('tomi').
    intersection = set(question_vector.keys()) & set(sentence_vector.keys())

    # Create numerator ('arithmitis').
    # [SUM(1,n) of Ai * Bi]
    numerator = sum([question_vector[x] * sentence_vector[x] for x in intersection])

    # Create denominator ('paronomastis').
    question_vector_sum = sum([question_vector[x]**2 for x in question_vector.keys()])  # (SUM(1,n) of  Ai^2)
    sentence_vector_sum = sum([sentence_vector[x]**2 for x in sentence_vector.keys()])  # (SUM(1,n) of Bi^2)
    denominator = math.sqrt(question_vector_sum) * math.sqrt(sentence_vector_sum)  # [Square root of (question_vector_sum)] * [Square root of (sentence_vector_sum)]

    # Calculate similarity score.
    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator





