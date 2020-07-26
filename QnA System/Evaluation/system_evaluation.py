import os
import re
import statistics

# Global variables for file management.
DATASET_OPTIONS = ['S08', 'S09', 'S10']
OUTPUT_FILE = '../Output/'


def get_stats():
    """Read each Dataset's article system_answers_eval.txt file and store the results.

    :rtype list
    :return: a list with quintet with #sentences, #questions, #questions_with_answers, #correct & #accuracy
    """

    all_statistics = []

    # For each Dataset
    for current_dataset in DATASET_OPTIONS:

        # Get files paths
        current_dataset_path = OUTPUT_FILE + current_dataset
        current_dataset_files = os.listdir(current_dataset_path)

        # Fore each file/article
        for file in current_dataset_files:

            # Open 'system_answers_eval.txt' in lines
            current_dataset_file_path = current_dataset_path + '/' + file + '/' + 'system_answers_eval.txt'
            current_dataset_file_lines = open(current_dataset_file_path).readlines()

            # Get statistics.
            try:
                article_sentences = re.findall(r'\d+', current_dataset_file_lines[0].strip())               # First Line - # sentences
                article_questions = re.findall(r'\d+', current_dataset_file_lines[1].strip())               # Second Line - # questions
                article_questions_with_answers = re.findall(r'\d+', current_dataset_file_lines[2].strip())  # Third Line - # questions with answers
                article_correct = re.findall(r'\d+', current_dataset_file_lines[3].strip())                 # Fourth Line - # correct answers
                article_accuracy = re.findall(r'\d+\.\d+', current_dataset_file_lines[4].strip())           # Fifth Line - # accuracy percent
            except 'Not_updated_file':
                print(current_dataset_file_path)

            # Store all statistics.
            quintet = int(article_sentences[0]), int(article_questions[0]),  int(article_questions_with_answers[0]), int(article_correct[0]), float(article_accuracy[0])
            all_statistics.append(quintet )

    return all_statistics


def counters(stats):
    """ Count all_sentences all_questions all_questions_with_ans & all_corrects

    :param stats: list(quintet)
    :rtype int, int, int, int
    :return: all_sentences, all_questions, all_questions_with_ans, all_corrects
    """

    # Initialization of counters.
    all_sentences = 0
    all_questions = 0
    all_questions_with_ans = 0
    all_corrects = 0

    # Parse stats and implement the addings.
    for sentences_num, questions_num, questions_with_ans, corrects, acc in stats:
        all_sentences += sentences_num
        all_questions += questions_num
        all_questions_with_ans += questions_with_ans
        all_corrects += corrects

    return all_sentences, all_questions, all_questions_with_ans, all_corrects


def calc(formula, stats):

    all_accuracies = []
    # Parse stats and implement the addings.
    for sentences_num, questions_num, questions_with_ans, corrects, acc in stats:
        all_accuracies.append(acc)

    if formula in 'mean':
        return statistics.mean(all_accuracies)
    else:
        return max(all_accuracies)


if __name__ == '__main__':

    stats_array = get_stats()
    sentences, questions, questions_with_answer, corrects_answers = counters(stats_array)
    mean = calc('mean', stats_array)
    max_accuracy = calc('max', stats_array)
    system_accuracy = float(corrects_answers/questions_with_answer) * 100

    print('Stats vector: ', stats_array)
    print('\nSentences number: ', sentences)
    print('Questions number: ', questions)
    print('Questions with answers number: ', questions_with_answer)
    print('Correct answers number: ', corrects_answers)

    print('\nSystem\'s accuracy(%):',system_accuracy)
    print('System\'s mean(%): ', mean)
    print('System\'s maximum accuracy(%): ', max_accuracy)
