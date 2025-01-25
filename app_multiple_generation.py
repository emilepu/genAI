


## multiple part generation version

import streamlit as st
import requests

##################################
# Helper Functions
##################################
def generate_text(prompt, temperature=0.9, top_p=0.9, max_length=150):
    # Replace with your actual Hugging Face token
    headers = {"Authorization": "Bearer hf_XXXXXXXXXXXXXXXXXx"}
    API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-1B"

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": max_length,
            "return_full_text": False,
            "temperature": temperature,
            "top_p": top_p
        },
        "options": {
            "use_cache": True,
            "wait_for_model": True
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload, timeout=180)
    if response.status_code == 200:
        return response.json()[0]['generated_text']
    else:
        raise Exception(f"Failed to generate text: {response.text}")

def trim_at_eos(text, eos_token='.'):
    pos = text.find(eos_token)
    if pos != -1:
        return text[:pos + len(eos_token)]
    return text

##################################
# Streamlit App
##################################
st.title("Creative Story Generator")

# Make sure certain variables exist in session state
if 'story_generated' not in st.session_state:
    st.session_state.story_generated = False
if 'show_refine_input' not in st.session_state:
    st.session_state.show_refine_input = False

# User inputs for the story
genre = st.text_input("Enter the genre of the story (e.g., fantasy, sci-fi, mystery):")
characters = st.text_input("Enter the characters in the story (e.g., John and Sarah):")
story_idea = st.text_input("Enter the main idea or theme of the story (e.g., exploring a new planet):")

##################################
# 1. Generate the story
##################################
if st.button("Generate Story"):
    if genre and characters and story_idea:
        # Prompt for story start
        prompt = (
            f"You are a writer. Write a {genre} story about {characters} "
            f"with the main idea: {story_idea} without extra remarks or questions. "
            f"Start by describing the characters, the setting, and the journey they will go on. "
            f"The story starts here:"
        )
        story_start = generate_text(prompt)
        story_start = trim_at_eos(story_start, eos_token='.')

        # Prompt for story middle
        prompt2 = (
            f"You are a writer. Continue this story by introducing a conflict or challenge "
            f"that {characters} must face. "
            f"This is the beginning of the story: {story_start}. "
            f"Don't add any additional comments or questions. Develop the story further:"
        )
        story_middle = generate_text(prompt2)
        story_middle = trim_at_eos(story_middle, eos_token='.')

        # Prompt for story end
        prompt3 = (
            f"You are a writer. Continue this story by resolving the conflict and concluding "
            f"the journey of {characters}. "
            f"This is the beginning of the story: {story_start} {story_middle}. "
            f"Don't add any additional comments or questions. Write the resolution of this story from here:"
        )
        story_end = generate_text(prompt3)
        story_end = trim_at_eos(story_end, eos_token='.')

        # Store in session state so we can display and potentially refine
        st.session_state.story_generated = True
        st.session_state.story_start = story_start
        st.session_state.story_middle = story_middle
        st.session_state.story_end = story_end

        # Hide refine input by default after a fresh generation
        st.session_state.show_refine_input = False

##################################
# 2. Display the generated story
##################################
if st.session_state.story_generated:
    st.subheader("Generated Story:")
    st.write(st.session_state.story_start)
    st.write(st.session_state.story_middle)
    st.write(st.session_state.story_end)

    # Reveal the "Refine Story" button
    if st.button("Refine Story"):
        st.session_state.show_refine_input = True

##################################
# 3. Refinement section
##################################
if st.session_state.show_refine_input:
    st.subheader("Refine Your Story")
    feedback = st.text_area("What would you like to change or refine? (e.g., add more description, change the ending, etc.)")

    if st.button("Apply Feedback"):
        # Build a new prompt that includes user feedback
        refine_prompt = (
            "You are a writer. Here's the story so far:\n\n"
            f"{st.session_state.story_start} {st.session_state.story_middle} {st.session_state.story_end}\n\n"
            "Refine or rewrite the story based on the following feedback (without adding unrelated comments or questions): "
            f"{feedback}\n\n"
            "Refined story:"
        )

        # Generate the refined story
        refined_story = generate_text(refine_prompt)
        refined_story = trim_at_eos(refined_story, eos_token='.')

        st.subheader("Refined Story:")
        st.write(refined_story)
