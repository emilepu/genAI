# api - single generation
import streamlit as st
import requests

##################################
# Helper Functions
##################################
def generate_text(prompt, temperature=0.9, top_p=0.8, max_length=400):
    # Replace with your actual Hugging Face token
    headers = {"Authorization": "Bearer hf_XXXXXXXXXX"}
    API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-1B"

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": max_length,
            "temperature": temperature,
            "top_p": top_p
        },
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
        # Single prompt to generate the entire story
        prompt = ((f"You are a writer. Write a {genre} story about {characters} with the main idea: {story_idea}. Start by describing the characters, the setting, and the journey they will go on. Then introduce a conflict or challenge they must face, and finally, resolve the conflict and conclude the story. Write the entire story:")

        # Generate the story in one go
        full_story = generate_text(prompt)
        full_story = trim_at_eos(full_story, eos_token='.')

        # Store in session state so we can display and potentially refine
        st.session_state.story_generated = True
        st.session_state.full_story = full_story

        # Hide refine input by default after a fresh generation
        st.session_state.show_refine_input = False

##################################
# 2. Display the generated story
##################################
if st.session_state.story_generated:
    st.subheader("Generated Story:")
    st.write(st.session_state.full_story)

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
        refine_prompt = (f"You are a writer. Here's the story so far:\n\n {st.session_state.full_story}\n\n Refine or rewrite the story based on the following feedback (without adding unrelated comments or questions): {feedback}\n\n Refined story:")

        # Generate the refined story
        refined_story = generate_text(refine_prompt)
        refined_story = trim_at_eos(refined_story, eos_token='.')

        st.subheader("Refined Story:")
        st.write(refined_story)
