import streamlit as st
from openai import OpenAI
import os
import re

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_story_game_ui(client):
    st.set_page_config(page_title="Eco Story Adventure + Game", layout="centered")

    hero = st.text_input("🧒 Hero’s Name", placeholder="e.g., Andy")
    setting = st.selectbox("🌍 Choose a Story Setting", ["bathroom", "garden", "school", "beach", "forest"])
    habit = st.selectbox("💧 Water Habit Focus", ["brushing teeth", "watering plants", "taking showers", "fixing leaks"])

    with st.expander("⚙️ Game Settings"):
        theme = st.radio("🎨 Visual Theme", ["Blue Drop", "Nature Kids", "Clean City", "Water Warriors"])
        hint_mode = st.checkbox("💡 Show Helpful Hints", value=True)

    theme_styles = {
        "Blue Drop": {
            "background": "linear-gradient(to bottom right, #003d66, #006699)",
            "button": "#0099ff"
        },
        "Nature Kids": {
            "background": "linear-gradient(to bottom right, #1b5e20, #4caf50)",
            "button": "#66bb6a"
        },
        "Clean City": {
            "background": "linear-gradient(to bottom right, #212121, #616161)",
            "button": "#9e9e9e"
        },
        "Water Warriors": {
            "background": "linear-gradient(to bottom right, #6d1b00, #ff7043)",
            "button": "#ffab91"
        }
    }

    style = theme_styles.get(theme, theme_styles["Blue Drop"])
    bg_style = style["background"]
    btn_color = style["button"]

    st.markdown(
        f'''
        <style>
            .stApp {{
                background: {bg_style};
            }}
            .stButton>button {{
                background-color: {btn_color};
                color: white;
                border-radius: 10px;
                font-weight: bold;
            }}
            .stRadio>div>label, .stSelectbox>div>label {{
                color: {btn_color};
                font-weight: 600;
            }}
            .st-expander>summary {{
                color: {btn_color};
            }}
            h1 {{
                color: {btn_color};
            }}
        </style>
        ''',
        unsafe_allow_html=True
    )

    st.markdown(f"<h1>📖 Eco Story Adventure + Game</h1>", unsafe_allow_html=True)

    if st.button("✨ Generate My Eco Adventure"):
        with st.spinner("Creating your story and game..."):
            story_prompt = (
                f"Write a fun children's story about {hero}, a young eco-hero in the {setting}, "
                f"learning to save water by practicing {habit}. Include a friendly sidekick and end with a water-saving tip."
            )

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a creative children's storyteller focused on sustainability."},
                    {"role": "user", "content": story_prompt}
                ],
                max_tokens=800,
                temperature=0.8
            )

            story = response.choices[0].message.content.strip()

            rules = {
                "brushing teeth": {
                    "challenge": "🪥 Tap to turn off the faucet while brushing.",
                    "goal": "Save 10 gallons by acting quickly!",
                    "points": "+5 per correct tap, -2 for misses."
                },
                "watering plants": {
                    "challenge": "🌿 Water only dry plants. Skip the ones already wet.",
                    "goal": "Keep your garden healthy and hydrated!",
                    "points": "+10 correct, -5 for overwatering."
                },
                "taking showers": {
                    "challenge": "🚿 Finish your shower in under 2 minutes.",
                    "goal": "Use under 5 gallons total!",
                    "points": "+2 per second saved."
                },
                "fixing leaks": {
                    "challenge": "🔧 Tap leaks before the bucket fills.",
                    "goal": "Fix 10 leaks in time!",
                    "points": "+5 per fix, -3 for missed."
                }
            }

            game = rules.get(habit.lower(), {
                "challenge": "💧 Make a smart water-saving choice!",
                "goal": "Reduce waste and become an Eco Hero!",
                "points": "+5 per smart move."
            })

            st.subheader("📘 Your Personalized Story")
            st.markdown(f"**{hero}'s Adventure in the {setting.capitalize()}**")
            st.write(story)

            st.subheader("🎮 Your Water-Saving Game")
            st.markdown(f"**Challenge:** {game['challenge']}")
            st.markdown(f"**Goal:** {game['goal']}")
            st.markdown(f"**Scoring:** {game['points']}")

            if hint_mode:
                with st.expander("💡 Tips & Tricks"):
                    st.markdown("""
- Turn off taps while brushing your teeth.  
- Keep showers short and sweet.  
- Fix leaky faucets right away.  
- Water plants early or late to reduce evaporation.  
- Use buckets instead of hoses when cleaning.
                    """)

            st.markdown(f"🎨 **Theme Selected:** {theme}")
            if hint_mode:
                st.success("💡 Hint mode is on — you’ll get reminders during the game!")

            st.subheader("🎬 Your Eco Adventure Comic")

            scene_prompt = (
                f"You are a comic artist turning this children's story into a 4 to 6 panel comic. "
                f"For each panel, number them clearly (1. 2. 3...), and describe the scene visually in 1–2 sentences. "
                f"Make sure each panel has a new line and starts with a number. Incorporate this theme into the scene visuals: '{theme}'.\n\n"
                f"Story:\n{story}"
            )

            with st.spinner("Breaking the story into comic scenes..."):
                scene_response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": scene_prompt}]
                )
                scene_text = scene_response.choices[0].message.content.strip()

            panel_descriptions = re.findall(r'\d\.\s.*?(?=\n\d\.|\Z)', scene_text, re.DOTALL)
            panel_descriptions = panel_descriptions[:6]

            if panel_descriptions:
                for i, panel in enumerate(panel_descriptions, start=1):
                    panel_cleaned = re.sub(r"^\d+\.\s*", "", panel.strip())
                    st.markdown(f"**Panel {i}:** {panel_cleaned}")
                    with st.spinner(f"Generating image for Panel {i}..."):
                        try:
                            panel_img_response = client.images.generate(
                                prompt=f"Comic panel in theme of '{theme}': {panel_cleaned}",
                                n=1,
                                size="512x512"
                            )
                            image_url = panel_img_response.data[0].url
                            st.image(image_url, caption=f"Panel {i}")
                        except Exception:
                            st.warning(f"⚠️ Could not load image for Panel {i}.")
                            st.text(f"Panel description: {panel_cleaned}")
            else:
                st.warning("⚠️ GPT did not return clearly numbered scenes.")
                st.markdown("Here is the raw output from GPT:")
                st.code(scene_text)

generate_story_game_ui(client)
