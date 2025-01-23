from gtts import gTTS
import tempfile
from dotenv import load_dotenv
import os
import streamlit as st
from PIL import Image
import google.generativeai as genai

# Load environment variables
load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to generate a response from the Gemini model
def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([input, image[0], prompt])
    return response.text

# Function to process uploaded image and prepare for input
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data,
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Function to convert text to speech using gTTS
def start_speech(text):
    tts = gTTS(text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        st.audio(fp.name, format="audio/mp3")

# Streamlit app initialization
st.set_page_config(page_title="Tablet Info Summarizer", layout="centered", page_icon="💊")

# Add custom CSS for styling
st.markdown(
    """
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: #ffffff;
        }
        .header {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 20px;
            color: #ffd700;
        }
        .subheader {
            text-align: center;
            font-size: 1.5em;
            color: #00ffcc;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown("<div class='header'>Tablet Info Summarizer</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subheader'>Upload a tablet image and get detailed information</div>",
    unsafe_allow_html=True,
)

# Initialize session state for the response text
if "response_text" not in st.session_state:
    st.session_state.response_text = ""

# User inputs
input = st.text_input(
    "Enter Additional Details (Optional):",
    key="input",
    help="Add any specific details or context about the tablet.",
)
uploaded_file = st.file_uploader(
    "Upload Tablet Image (JPG, JPEG, PNG):", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
)

# Display uploaded image
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Tablet Image")

# Analyze tablet info button
if st.button("Analyze Tablet Info", use_container_width=True):
    if uploaded_file is not None:
        try:
            # Prepare the image data for input to the Gemini model
            image_data = input_image_setup(uploaded_file)

            # Custom prompt for the tablet information summary
            input_prompt = """
            You are an expert in understanding pharmaceutical information.
            You will receive input images of tablets with their labels.
            Based on the input image, you will:
            1. Identify the name of the tablet from the label.
            2. Search for its uses, side effects, precautions, dosage instructions, and interactions.
            3. Provide a concise and accurate summary of the findings.
            Ensure that the information is up-to-date and sourced from reliable medical websites.
            """

            # Combine the extracted text with the user's input prompt
            complete_prompt = f"{input_prompt}\n\nTablet Details: {input}\n\nSummary:"

            # Process the tablet image with the Gemini model
            st.session_state.response_text = get_gemini_response(complete_prompt, image_data, input)

        except Exception as e:
            st.error(f"Error processing the tablet info: {e}")
    else:
        st.warning("Please upload a tablet image to proceed.")

# Display the response text if available
if st.session_state.response_text:
    st.markdown("<h3 style='color:#ffd700;'>Tablet Information Summary</h3>", unsafe_allow_html=True)
    st.success(st.session_state.response_text)

    # Add "Voice" button
    if st.button("Voice"):
        start_speech(st.session_state.response_text)
