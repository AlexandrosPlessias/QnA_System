import os
import tkinter as tk

import server_stuff
import data_reading
import data_parsing
import question_answering

from textblob import TextBlob
from nltk import word_tokenize

# Global variables for file management.
DATASET_OPTIONS = ['S08', 'S09', 'S10']
SELECTED_DATASET = DATASET_OPTIONS[2]
INPUT_FILE = data_reading.INPUT_DIR + 'Question_Answer_Dataset_v1.2/'+SELECTED_DATASET+'/question_answer_pairs.txt'
DATA_FILE = data_reading.INPUT_DIR + 'Question_Answer_Dataset_v1.2/'+SELECTED_DATASET+'/'

# Global variables for data read and management.
DATA = data_reading.read_data(INPUT_FILE)  # Load data: ArticleTitle, Question, Answer & Article.
WIKI_ARTICLES_TITLES_SET = []

# Global variables for GUI.
WINDOW = tk.Tk()


def main():
    """ Create a set with all available articles & start Graphical User Interface(GUI).

    :return: None
    :rtype: None
    """
    create_wiki_titles()
    gui_start()


def create_wiki_titles():
    """ Read global variable DATA and get all available articles titles.
    After update global variable wiki_articles_titles with them.

    :return: None
    :rtype: None
    """
    wiki_articles_titles = []

    for article_title, question, answer, article in DATA:
        wiki_articles_titles.append(article_title)

    global WIKI_ARTICLES_TITLES_SET
    WIKI_ARTICLES_TITLES_SET = sorted(set(wiki_articles_titles))


def run_qna_system(target_article):
    """ Get all article's questions and real answers and call qna_system method for answering.

    :param target_article: The articles name we want to examine.
    :type target_article: str
    :return: None
    :rtype: None
    """

    questions = []
    real_answers = []
    question_buffer = ''  # For remove duplicates.

    for article_title, question, answer, article in DATA:
        if article_title == target_article:
            article_location = DATA_FILE + article + '.txt.clean'
            if question_buffer != question:  # Remove duplicates.
                questions.append(question.lower())
                real_answers.append(answer)
            question_buffer = question
    qna_system(target_article, article_location, questions, real_answers)


def qna_system(article_title, article_location, questions, real_answers):
    """ Here get the article's name, location, questions and real answer and do the answering.

    :param article_title: The article's name we want to examine.
    :type article_title: str
    :param article_location: The location of file with article's context text.
    :type article_location: str
    :param questions: A list with all possible questions.
    :type questions:list(str)
    :param real_answers: A list with all real answers of questions.
    :type real_answers: list(str)
    :return: Nothing
    :rtype:Nothing
    """
    # Read Article.
    article_text = data_reading.read_article(article_location)

    # Trim lines.
    article_text = article_text.lower()
    article_text = article_text.replace('\n', ' ')

    # Article to sentences.
    blob = TextBlob(article_text)  # https://textblob.readthedocs.io/en/dev/
    sentences = blob.sentences  # Create list with sentences.
    sentences = [str(sentence) for sentence in sentences]

    update_display('Article name: ' + article_title, True)  # print('Article name: ', article_title)
    update_display('Article\'s sentences : ' + str(len(sentences)), True)  # print('Article\'s sentences : ', len(sentences))
    update_display('Questions number : ' + str(len(questions)), True)  # print('Questions number : ', len(questions))
    update_display('', False)  # print()

    # Read a file with 8567 different verbs and for every verb all tenses. ???
    data_reading.read_verbs('verbs (8567).txt')

    # Here check if parsed data already exist from past implementation
    # else create new data and store them.
    if os.path.isdir(data_reading.OUTPUT_DIR + '/' + SELECTED_DATASET + '/' + article_title):
        context_parsed_trees, questions_parsed_trees, context_sentences_ners = data_parsing.read_parse_data(SELECTED_DATASET, article_title)
    else:

        # Run CoreNLP Server.
        server_stuff.start_server()

        # Create parse trees for context and questions.
        context_parsed_trees = data_parsing.create_parse_trees(sentences)
        questions_parsed_trees = data_parsing.create_parse_trees(questions)

        # Parse sentences for NERs -Named Entity Recognition- in context.
        context_sentences_ners = data_parsing.find_all_ner(sentences)

        # Stop CoreNLP Server.
        server_stuff.stop_server()

        data_parsing.write_parse_data(SELECTED_DATASET, article_title, context_parsed_trees, questions_parsed_trees, context_sentences_ners)

    system_answers = []

    # Examine every question one by one.
    # https://docs.python.org/2/library/functions.html#zip
    for question, question_tree in zip(questions, questions_parsed_trees):

        update_display(question.capitalize(), True)  # print(question.capitalize())

        if ('when' in question) or ('how long' in question) or ('how many' in question) or ('how much' in question) or ('how old' in question):
            # The NER tags i need for When questions.
            target_ner_tags = ['DATE', 'TIME', 'NUMBER', 'ORDINAL']
            answer = question_answering.wh_familiar(question, context_parsed_trees, context_sentences_ners, target_ner_tags)

        elif ('who' in question) or ('whom' in question) or ('whose' in question):
            # The NER tags i need for Who questions.
            target_ner_tags = ['PERSON']  # 'TITLE'
            answer = question_answering.wh_familiar(question, context_parsed_trees, context_sentences_ners, target_ner_tags)

        elif 'where' in question:
            # The NER tags i need for Where questions.
            target_ner_tags = ['LOCATION', 'CITY', 'STATE_OR_PROVINCE', 'COUNTRY']
            answer = question_answering.wh_familiar(question, context_parsed_trees, context_sentences_ners, target_ner_tags)

        elif ('what' in question) or ('how' in question) or ('why' in question) or ('which' in question):
            answer = question_answering.wh_questions(question, question_tree, sentences, context_parsed_trees)

        else:
            answer = question_answering.yes_no(question, question_tree, sentences)

        # Other systems failed or haven't question
        if answer is None:
            answer = question_answering.wh_questions(question, question_tree, sentences, context_parsed_trees)

        # Store answer.
        record = question, answer
        system_answers.append(record)

        # answer_comment is used for Debugging propuses
        answer_text, answer_comment = answer
        update_display(answer_text, False)  # print(answer_text)
        update_display('', False)  # print()

    # Write answer to File.
    save_answers(article_title, system_answers)

    # Here add evaluation check correct answers with programme's answers.
    score = system_evaluation(sentences, questions, article_title, real_answers, system_answers)

    # print('For this article ' + article_title + ' the score (correct/all_number) is: ' + '{:.2%}'.format(score))
    update_display('For this article ' + article_title + ' the score (correct/all_number) is: ' + '{:.2%}'.format(score), True)


def save_answers(article_title, system_answers):
    """ Create a file at output folder with article's name with name system_answers.txt in this form:

        ArticleTitle    Question        Answer              AnswersComment
    ie. Zebra           question name   question's answer   answer's comment

    :param article_title: The articles test.
    :type article_title: str
    :param system_answers: System's question, answer_text & answer_comment.
    :type system_answers: list(tuple(question, tuple(answer_text,answer_comment) ) )
    """

    file = open(data_reading.OUTPUT_DIR + SELECTED_DATASET + '/' + article_title + '/system_answers.txt', 'w', encoding='utf-8')

    # Write data to file.
    file.write('ArticleTitle    Question    Answer    Answer\'sComment    \n')
    for system_answer in system_answers:

        # Unwrap answer text.
        question, answer = system_answer
        answer_text, answer_comment = answer

        line = article_title + '   ' + question + '   ' + answer_text + '    ' + answer_comment
        file.write(line)
        file.write('\n')

    file.close()


def system_evaluation(sentences, questions, article_title, real_answers, system_answers):
    """ Here calculate the number of right answers and create a score.

    score = correct answers / total number of questions.

    :param article_title: The articles test.
    :type article_title: str
    :param real_answers: A list with right answers to questions.
    :type real_answers: list(str)
    :param system_answers: System's question, answer_text & answer_comment.
    :type system_answers: list(tuple(question, tuple(answer_text,answer_comment) ) )
    :return: The correct answers percent.
    :rtype: float
    """

    total_num = len(real_answers)
    correct = 0
    no_answer_exist = 0

    for real_answer, system_answer in zip(real_answers, system_answers):

        # Unwrap answer text.
        question, answer = system_answer
        answer_text, answer_comment = answer

        # print("Q: "+question, "RA: "+real_answer, "MA: "+answer_text)  # Used for debugging.

        # If answer exist.
        if 'NULL' in real_answer:
            no_answer_exist += 1
        elif not real_answer:
            no_answer_exist += 1
        else:
            if is_similar(real_answer, answer_text):
                correct += 1
        # print(correct)  # Used for debugging

    score = float(correct/(total_num - no_answer_exist))

    file = open(data_reading.OUTPUT_DIR + '/' + SELECTED_DATASET + '/' + article_title + '/system_answers_eval.txt', 'w', encoding='utf-8')
    file.write(article_title + '\'s article sentences: ' + str(len(sentences)) + '\n')
    file.write(article_title + '\'s article questions: ' + str(len(questions)) + '\n')
    file.write(article_title + '\'s article questions with answer: ' + str(total_num - no_answer_exist) + '\n')
    file.write(article_title + '\'s correct answers: ' + str(correct) + '\n')
    file.write('For this article ' + article_title + ' the score (correct/all_number) is: ' + '{:.2%}'.format(score))
    file.close()

    return score


def is_similar(real_answer, answer_text):
    """  Check if the answer text is similar to real answer.

    :param real_answer: The text of real answer.
    :type real_answer: str
    :param answer_text: The text of system's answer.
    :type answer_text: str
    :return: True if is similar else False
    :rtype: Bool
    """

    from nltk.stem import SnowballStemmer

    snow_stemmer = SnowballStemmer(language='english')

    # Create real's answer's tokens.
    real_answer = real_answer.lower()
    real_tokens = word_tokenize(real_answer)
    real_tokens = [snow_stemmer.stem(token) for token in real_tokens]

    # Create system's answer's tokens.
    answer_text = answer_text.lower()
    answer_tokens = word_tokenize(answer_text)
    answer_tokens = [snow_stemmer.stem(token) for token in answer_tokens]

    # print(real_tokens, '-->', answer_tokens)

    # Here check if answer_tokens list contains all elements in real_tokens list.
    return all(elem in answer_tokens for elem in real_tokens)


"""GUI DESIGN & METHODS"""


def gui_start():
    """ Create a basic GUI screen for interaction with user and show the results.

    :return: None
    :rtype: None
    """

    # Set windows properties.
    WINDOW.title("Question answering System")
    WINDOW.minsize(width=900, height=600)
    WINDOW.maxsize(width=1300, height=600)

    # Create 3 frames (for article_list - run_button - text_area ) with border = 1 &  3-D effects = sunken.
    list_frame = tk.Frame(WINDOW,  bd=1, relief='sunken')
    button_frame = tk.Frame(WINDOW,  bd=1, relief='sunken')
    console_frame = tk.Frame(WINDOW, bd=1, relief='sunken')

    # Placement of 3 frames at grid.
    list_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
    button_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
    console_frame.grid(row=0, column=1, rowspan=2,  columnspan=2, sticky="nsew", padx=2, pady=2)

    # Configure grid geometry of rows.
    WINDOW.grid_rowconfigure(0, weight=3)
    WINDOW.grid_rowconfigure(1, weight=1)

    # Configure grid geometry of column.
    WINDOW.grid_columnconfigure(0, weight=1)
    WINDOW.grid_columnconfigure(1, weight=5)

    """ Create list_frame's scrollbar & listbox """
    # Create a label to Show the text "Select Dataset:"
    text_label = tk.Label(list_frame, text="Select Dataset:")
    text_label.pack()

    # Create a drop down menu to choose the preferred Dataset to choose from.
    dataset_var = tk.StringVar()
    dataset_var.set(SELECTED_DATASET)
    option_menu = tk.OptionMenu(list_frame, dataset_var, *DATASET_OPTIONS, command=get_drop_down_menu_val)
    option_menu.pack()

    # Create listbox with dataset's options.
    list_scrollbar = tk.Scrollbar(list_frame, orient="vertical")
    list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox = tk.Listbox(list_frame, yscrollcommand=list_scrollbar.set, selectmode=tk.SINGLE, font=("Helvetica", 13))
    listbox.pack(expand=True, fill=tk.BOTH)

    # Fill the listbox and set default select the 0.
    fill_list(listbox)
    listbox.select_set(0)

    """ Create button_frame's button """
    # Make my event handler a lambda function, which calls run_button() when called.
    button_run = tk.Button(button_frame, command=lambda: run_button(button_run, listbox), state=tk.NORMAL, text='Run QnA')
    button_run.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    """ Create console_frame's scrollbar & text """
    text_scrollbar = tk.Scrollbar(console_frame, orient="vertical")
    text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # The variable DISPLAY_TEXT is global for show console messages to GUI.
    global DISPLAY_TEXT
    DISPLAY_TEXT = tk.Text(console_frame, wrap=tk.WORD, yscrollcommand=text_scrollbar.set, font=("Helvetica", 12))
    DISPLAY_TEXT.pack(expand=True, fill=tk.BOTH)

    # Create 2 tags witch used for important text(use Bold) & for simple text(use italic).
    DISPLAY_TEXT.tag_config('important_text', font="Helvetica 12 bold")
    DISPLAY_TEXT.tag_config('simple_text', font="Helvetica 12 italic")

    # Show info message when frame is created.
    tk.messagebox.showinfo("PROGRAM INFO", "For properly run of Program  you will need:\n\n"
                                           "Python ver. 3.5 or newer installed with NLTK, re, math, csv,collections, platform, subprocess & pickle packages installed (better use pip command).\n\n\n"
                                           "Additional information:\n\n"
                                           "If the needed program's data don't exist, from an earlier run the command line (cmd) will open for a few seconds for starting Stanford CoreNLP server."
                                           "So, don't close it. Also ignore 'Don't respond message', if showed and wait for a few seconds. \n\n\n"
                                           "Program's output:\n\n"
                                           "Finally, all data from the program's runs will be stored in the Output folder!!!")

    WINDOW.mainloop()


def get_drop_down_menu_val(preferred_dataset):
    global SELECTED_DATASET, INPUT_FILE, DATA_FILE, DATA

    SELECTED_DATASET = preferred_dataset
    INPUT_FILE = data_reading.INPUT_DIR + 'Question_Answer_Dataset_v1.2/' + SELECTED_DATASET + '/question_answer_pairs.txt'
    DATA_FILE = data_reading.INPUT_DIR + 'Question_Answer_Dataset_v1.2/' + SELECTED_DATASET + '/'
    DATA = data_reading.read_data(INPUT_FILE)  # Load data: ArticleTitle, Question, Answer & Article.

    create_wiki_titles()
    main()


def fill_list(listbox):
    """ Fill listbox with global variables values from WIKI_ARTICLES_TITLES_SET.

    :param listbox: The empty Listbox.
    :type listbox: tk.Listbox
    :return: None
    :rtype: None
    """

    for wiki_article in WIKI_ARTICLES_TITLES_SET:
        listbox.insert("end", wiki_article)


def run_button(button_run, listbox):
    """Clean GUI's text after disable Run Button and get the article's name the user choose.
    Call run_qna_system with article's name chosen by user and enable Run Button for re-Run.

    :param button_run: The run Button.
    :type  button_run: tk.Button
    :param listbox: The Listbox with articles.
    :type listbox: tk.Listbox
    :return: None
    :rtype: None
    """

    # Clean GUI's text.
    DISPLAY_TEXT.delete('1.0', tk.END)

    # Disable Run Button.
    button_run.config(state=tk.DISABLED)
    button_run.update()

    # Call run_qna_system with article's name chosen by user.
    article_title = listbox.get(tk.ACTIVE)
    run_qna_system(article_title)

    # Enable Run Button for re-Run.
    button_run.config(state=tk.NORMAL)
    button_run.update()


def update_display(text, important):
    """ Update DISPLAY_TEXT variable with given text with proper tag.

    :param text: The text I want to show in GUI.
    :type text: str
    :param important: A flag to know if text is important or not.
    :type important: Bool
    :return:
    """

    text = text + '\n'

    # If text is important use important_text tag else simple_text tag.
    # And update GUI's text.
    if important:
        DISPLAY_TEXT.tag_config('RED', foreground='red')
        DISPLAY_TEXT.insert("end", text, 'important_text')
    else:
        DISPLAY_TEXT.insert("end", text, 'simple_text')


"""Call program's main."""
if __name__ == "__main__":
    main()
