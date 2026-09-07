
import os
import streamlit as st
from google import genai

from workflow import run_workflow


st.set_page_config(
    page_title="AI Study Pack Generator",
    page_icon="📚",
    layout="wide"
)

DEFAULT_MODEL = "gemini-2.5-flash"

SECTIONS = [
    "Simple Explanation",
    "Detailed Notes",
    "Key Points",
    "Important Definitions",
    "Worked Examples",
    "Flashcards",
    "MCQs with Answers",
    "Short Questions with Answers",
    "Revision Summary",
]

DEFAULT_SECTIONS = [
    "Simple Explanation",
    "Key Points",
    "Important Definitions",
    "Flashcards",
    "MCQs with Answers",
    "Revision Summary",
]

if "workflow_result" not in st.session_state:
    st.session_state.workflow_result = None

if "workflow_errors" not in st.session_state:
    st.session_state.workflow_errors = []


def get_api_key(typed_key=""):
    if typed_key and typed_key.strip():
        return typed_key.strip()

    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    return os.getenv("GEMINI_API_KEY", "")


st.title("📚 AI Study Pack Generator")
st.caption("Planning → Content Generation → Assessment → Review → Refinement")

with st.sidebar:
    st.header("⚙️ AI Settings")

    model = st.text_input("Gemini Model", value=DEFAULT_MODEL)

    st.info("One study pack can use up to five AI calls, plus retries.")

left, right = st.columns([2, 1])

with left:
    topic = st.text_area(
        "📖 Topic / Study Instructions",
        height=130,
        placeholder="Example: Explain climate change and water availability."
    )

    goal = st.text_area(
        "🎯 Learning Goal",
        height=80,
        placeholder="Example: Prepare for my university exam and viva."
    )

    preferences = st.text_area(
        "📝 Personalization Preferences",
        height=80,
        placeholder="Example: Simple explanations and practical examples."
    )

with right: 
    level = st.selectbox(
        "Student Level",
        ["Beginner", "Intermediate", "Advanced"]
    )

    learning_duration = st.selectbox(
        "⏱️ Learning Duration",
        [
            "15 Minutes",
            "30 Minutes",
            "45 Minutes",
            "1 Hour",
            "2 Hours",
            "3+ Hours"
        ]
    )

    language = st.selectbox(
        "Language",
        ["English", "Urdu", "Roman Urdu"]
    )

    include_quiz = st.checkbox(
        "📝 Include Quiz",
        value=True
    )

    quiz_questions = 5

    if include_quiz:
        quiz_questions = st.selectbox(
            "Number of Quiz Questions",
            [5, 10, 15, 20]
        )

    selected_sections = st.multiselect(
        "Study Pack Sections",
        SECTIONS,
        default=DEFAULT_SECTIONS
    )

    selected_sections = st.multiselect(
        "Study Pack Sections",
        SECTIONS,
        default=DEFAULT_SECTIONS
    )

if st.button("🚀 Generate Study Pack", type="primary", use_container_width=True):
    api_key = get_api_key()

    if not api_key:
        st.error(
            "Gemini API key is missing. Enter it in the sidebar "
            "or add GEMINI_API_KEY in Streamlit Secrets."
        )
    elif not topic.strip():
        st.error("Please enter a study topic.")
    elif not selected_sections:
        st.error("Please select at least one study-pack section.")
    else:
        context = {
            "topic": topic.strip(),
            "level": level,
            "language": language,
            "learning_duration": learning_duration,
            "include_quiz": include_quiz,
            "quiz_questions": quiz_questions if include_quiz else 0,
            "goal": goal.strip() or "General learning and exam revision",
            "preferences": (
                preferences.strip()
                or "Clear, accurate, concise and student-friendly"
            ),
            "sections": selected_sections,
        }

        try:
            client = genai.Client(api_key=api_key)

            with st.status(
                "Running multi-stage AI workflow...",
                expanded=True
            ) as status:

                def show_progress(message):
                    st.write(message)

                outputs, errors, final_pack = run_workflow(
                    client=client,
                    model=model.strip() or DEFAULT_MODEL,
                    context=context,
                    progress_callback=show_progress
                )

                if final_pack:
                    status.update(
                        label="AI workflow completed.",
                        state="complete",
                        expanded=False
                    )
                else:
                    status.update(
                        label="Workflow stopped because content generation failed.",
                        state="error"
                    )

            st.session_state.workflow_result = outputs
            st.session_state.workflow_errors = errors

            if final_pack is None:
                st.error("No final study pack could be created.")

        except Exception as exc:
            st.error(f"Application error: {exc}")

result = st.session_state.workflow_result

if result and result.get("final"):
    st.divider()
    st.header("✅ Final Personalized Study Pack")
    st.markdown(result["final"])

    st.download_button(
        "⬇️ Download Final Study Pack",
        data=result["final"],
        file_name="personalized_study_pack.md",
        mime="text/markdown",
        use_container_width=True
    )

    st.subheader("🔬 Workflow Stages")

    with st.expander("1. 🧭 Planning Stage"):
        st.markdown(result.get("plan", "Not available."))

    with st.expander("2. ✍️ Content Generation Stage"):
        st.markdown(result.get("draft", "Not available."))

    with st.expander("3. 🧪 Assessment Stage"):
        st.markdown(result.get("assessment", "Not available."))

    with st.expander("4. 🔎 Review Stage"):
        st.markdown(result.get("review", "Not available."))

    with st.expander("5. ✨ Refinement Stage"):
        st.markdown(result.get("final", "Not available."))

if st.session_state.workflow_errors:
    with st.expander("⚠️ Error / Recovery Log"):
        for item in st.session_state.workflow_errors:
            st.warning(item)
