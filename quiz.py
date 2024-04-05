from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import StrOutputParser
import streamlit as st
import os

def create_the_quiz_prompt_template():
    """Create the prompt template for the quiz app."""
    template = """
You are an expert quiz maker relating to content around AI, ML, Data Science, LLM's, NLP and Computer Vision. Let's think step by step and create a multiple choice quiz with {num_questions} questions about the following concept/content: {quiz_context}.

The format of the quiz is as follows:
Questions:
1. <Question1>
   a. <Answer 1>
   b. <Answer 2>
   c. <Answer 3>
   d. <Answer 4>
2. <Question2>
   a. <Answer 1>
   b. <Answer 2>
   c. <Answer 3>
   d. <Answer 4>
...

Answers:
1. <a|b|c|d>
2. <a|b|c|d>
...

Note: Allow the user to select any of the options (a, b, c, or d) as the answer to each question. Give hints if necessary. Make sure the questions are clear and concise.
"""
    prompt = ChatPromptTemplate.from_template(template)
    prompt.format(num_questions=2, quiz_context="AI and Machine Learning")
    return prompt

def create_quiz_chain(prompt_template, llm):
    """Creates the chain for the quiz app."""
    return prompt_template | llm | StrOutputParser()

def split_questions_answers(quiz_response):
    """Function that splits the questions and answers from the quiz response."""
    questions = quiz_response.split("Answers:")[0]
    answers = quiz_response.split("Answers:")[1]
    return questions, answers

def display_questions(questions):
    user_answers = {}
    question_lines = questions.split("\n")
    current_question = None
    options = []
    question_number = 1

    for line in question_lines:
        if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.")):
            if current_question:
                st.write(current_question)
                user_answer = st.radio("Select your answer:", options, key=f"question_{question_number}")
                user_answers[question_number] = user_answer.split(".", 1)[0].strip()
                question_number += 1
            current_question = line
            options = []
        elif line.strip().startswith(("a.", "b.", "c.", "d.")):
            options.append(line)

    if current_question:
        st.write(current_question)
        user_answer = st.radio("Select your answer:", options, key=f"question_{question_number}")
        user_answers[question_number] = user_answer.split(".", 1)[0].strip()

    return user_answers

def calculate_score(user_answers, correct_answers):
    # print both user_answers and correct_answers 
    print("USER ANSWER:", user_answers)
    # extract the first letter from the user answer and use update the variable to use that 
    print("CORRECT ANSWER:", correct_answers)
    score = 0
    correct_answers_list = correct_answers.strip().split("\n")
    for i, correct_answer in enumerate(correct_answers_list, start=1):
        if user_answers.get(i, "").strip().lower() == correct_answer.strip().lower().split(".")[0]:
            score += 1
    return score

def main():
    st.title("AI Quiz App")
    st.write("This app generates a quiz based on a given context.")
    os.environ["OPENAI_API_KEY"] = "PUT_YOUR_OPENAI_API_KEY_HERE"
    prompt_template = create_the_quiz_prompt_template()
    llm = ChatOpenAI(model="gpt-4", temperature=0.0)
    chain = create_quiz_chain(prompt_template, llm)
    
    if "questions" not in st.session_state:
        st.session_state.questions = None
    if "answers" not in st.session_state:
        st.session_state.answers = None
    
    context = st.text_area("Enter the concept/context for the quiz")
    num_questions = st.number_input("Enter the number of questions", min_value=1, max_value=5, value=2)
    
    if st.button("Generate Quiz"):
        quiz_response = chain.invoke({"num_questions": num_questions, "quiz_context": context})
        st.write("Quiz Generated!")
        questions, answers = split_questions_answers(quiz_response)
        st.session_state.questions = questions
        st.session_state.answers = answers
    
    if st.session_state.questions:
        user_answers = display_questions(st.session_state.questions)
        st.session_state.user_answers = user_answers
    
    if st.button("Show Answers"):
        if st.session_state.questions and st.session_state.answers:
            st.write("----")
            st.markdown(st.session_state.answers)
            # Score calculation buggy rn so commented it out but needs to compare the string. Output correctly below: 
            """
                USER ANSWER: {1: 'a', 2: 'd'}
                UPDATED USER ANSWER: {1: 'a', 2: 'd'}
                CORRECT ANSWER:
                1. a
                2. d
            """
            #score = calculate_score(st.session_state.user_answers, st.session_state.answers)
            #total_questions = len(st.session_state.answers.strip().split("\n"))
            #st.write(f"Your score: {score}/{total_questions}")
        else:
            st.write("Please generate the quiz first.")

if __name__ == "__main__":
    main()