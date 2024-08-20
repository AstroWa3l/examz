import streamlit as st
import re
import time
import matplotlib.pyplot as plt

def load_questions():
    try:
        with open("questions_2.md", "r") as file:
            content = file.read()
        
        # Split content into lines
        lines = content.split('\n')

        parsed_questions = []
        current_question = None
        current_options = []

        for line in lines:
            line = line.strip()
            if line.startswith("# Question"):
                # If it's a question, create a new question object
                if current_question:
                    parsed_questions.append({
                        'number': current_question['number'],
                        'question': current_question['question'],
                        'options': current_options
                    })
                current_options = []
                current_question = {'number': int(line.split()[2]), 'question': ''}
            elif line.startswith("- "):
                # If it's an option, add it to the current options list
                current_options.append(line[2:])
            elif line:  # If it's not an empty line
                # Append to the current question's text
                current_question['question'] += line + '\n'

        # Add the last question
        if current_question:
            parsed_questions.append({
                'number': current_question['number'],
                'question': current_question['question'],
                'options': current_options
            })

        return parsed_questions
    except Exception as e:
        st.error(f"Error loading questions: {e}")
        return []

def load_answers():
    try:
        with open("answers_2.md", "r") as file:
            content = file.read()
        answers = re.findall(r"(\d+): (.*)", content)
        return {int(num): [ans.strip() for ans in ans_str.split(",")] for num, ans_str in answers}
    except Exception as e:
        st.error(f"Error loading answers: {e}")
        return {}

def main():

    st.title("CompTIA A+ Practice Exam")

    questions = load_questions()
    answers = load_answers()

    # Get the session state
    session_state = st.session_state

     # Initialize session state
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}

    # Initialize the session state for incorrect questions if it doesn't exist
    if "incorrect_questions" not in st.session_state:
        st.session_state.incorrect_questions = []
                
    # Extract answer choice from user answers dictionary
    user_answers_choices = {}
    for key, value in st.session_state.user_answers.items():
        if isinstance(value, list):
            user_answers_choices[key] = [item.split('. ')[0].strip() for item in value]
        else:
            user_answers_choices[key] = value.split('. ')[0].strip()
    
    # Display the questions
    for q in questions:
        if q['number'] in st.session_state.incorrect_questions:
            st.subheader(f"Question {q['number']}: {q['question']}")
            for choice in q['options']:
                if q['number'] in st.session_state.incorrect_questions and choice.split('. ')[0].strip() in user_answers_choices[q['number']]:
                    st.markdown(f'<p style="color:red;">{choice}</p>', unsafe_allow_html=True)
                else:
                    st.markdown(choice)
        else:
            st.subheader(f"Question {q['number']}: {q['question']}")
            if "TWO" in q['question']:
                st.session_state.user_answers[q['number']] = st.multiselect(
                    f"Select your answer(s) for Question {q['number']}", q['options'], key=f"q{q['number']}")
            else:
                st.session_state.user_answers[q['number']] = st.radio(
                    f"Select your answer for Question {q['number']}", q['options'], key=f"q{q['number']}")
                
    # Initialize the session state for the buttons if they don't exist
    if "submit_clicked" not in st.session_state:
        st.session_state.submit_clicked = False
    if "review_clicked" not in st.session_state:
        st.session_state.review_clicked = False

    # Create a placeholder for the "Review Answers" button
    review_button_placeholder = st.empty()

    # Retake test button
    retake_button_placeholder = st.empty()

    # Submit button placeholder
    submit_button_placeholder = st.empty()

    # Calculate and display score
    if st.button("Submit") or st.session_state.submit_clicked:
        st.session_state.submit_clicked = True
        st.balloons()
        if len(user_answers_choices) == len(questions):
            score = 0
            incorrect_questions = []
            # Convert to set if value is list (multiple options selected)
            for k, v in user_answers_choices.items():
                # Sanitize the user's answers by trimming whitespace
                user_answer_set = set([ans.strip() for ans in v]) if isinstance(v, list) else {v.strip()}
                correct_answer_set = set([ans.strip() for ans in answers.get(k, [])])

                if user_answer_set == correct_answer_set:
                    score += 1
                else:
                    incorrect_questions.append(k)

            percentage = (score / len(questions)) * 100
            st.success(f"You scored {score}/{len(questions)} or ({percentage:.2f}%)")

            # Update the session state with the incorrect questions
            session_state.incorrect_questions = incorrect_questions

            # Update the review button placeholder after the user submits
            # this will show the "Review Answers" button and reveal the incorrect choices
            # and we wanty to still display the score even during review state
            if st.session_state.submit_clicked:
                if st.button("Review Answers") or st.session_state.review_clicked:
                    st.session_state.review_clicked = True

                    # Display the pie chart
                    correct_answers = score
                    incorrect_answers = len(questions) - score
                    labels = 'Correct', 'Incorrect'
                    sizes = [correct_answers, incorrect_answers]
                    colors = ['#4CAF50', '#FF5733']
                    explode = (0.1, 0)  # explode the 1st slice (Correct)

                    fig1, ax1 = plt.subplots()
                    ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                            shadow=True, startangle=90)
                    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

                    st.pyplot(fig1)

                    # Add Retake Test button
                    if st.button("Retake Test"):
                        # Clear session state
                        st.session_state.clear()
                        # Refresh the page
                        st.rerun()

if __name__ == "__main__":
    main()