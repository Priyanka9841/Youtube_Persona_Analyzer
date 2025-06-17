import streamlit as st
import pandas as pd
import plotly.express as px
from backend.processing import analyze_youtube_zip
import time
import json

st.set_page_config(page_title="YouTube Digital Mirror", page_icon="🔮", layout="wide")

# Dark theme styling
st.markdown("""
<style>
body {
    background-color: #0f0f0f;
    color: white;
}
[data-testid="stAppViewContainer"] {
    background-color: #0f0f0f;
}
h1, h2, h3, h4 {
    color: #FFD700;
}
.step-box {
    padding: 15px;
    border-radius: 10px;
    background: #1e1e1e;
    margin-bottom: 20px;
    border-left: 4px solid #FF0000;
}
.recommendation-tag {
    background-color: #cc0000;
    color: white;
    border-radius: 10px;
    padding: 5px 10px;
    margin: 5px;
    display: inline-block;
}
.box {
    background-color: #1e1e1e;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

def show_step(step):
    steps = {
        1: ("Upload your YouTube ZIP file", "Next: Analyzing your watch history..."),
        2: ("Analyzing your history", "Next: Generating persona insights..."),
        3: ("Results Ready", "")
    }
    current, next_ = steps.get(step, ("", ""))
    st.markdown(f"""
    <div class='step-box'>
        <h3>🔄 {current}</h3>
        <p style='color:#aaa;'>{next_}</p>
    </div>
    """, unsafe_allow_html=True)

# Main app
def main():
    st.title("🧠 YouTube Digital Mirror")
    uploaded_file = st.file_uploader("📁 Upload your YouTube Takeout ZIP file", type=["zip"])

    if uploaded_file:
        show_step(1)
        time.sleep(1)
        show_step(2)

        results = analyze_youtube_zip(uploaded_file)
        time.sleep(1)
        show_step(3)

        st.subheader("🎯 Current Algorithm Profile")

        persona_summary = results.get('persona_summary', '❌ No summary')
        full_report_str = results.get('full_report', '{}')
        interests_df = results.get('interests_chart_data', pd.DataFrame())

        try:
            report_json = json.loads(full_report_str)
            cluster_data = report_json.get("profile_clusters", [])
        except:
            report_json = {}
            cluster_data = []

        top_interest = cluster_data[0]['Cluster Label'] if cluster_data else "Unknown"
        top_keywords = cluster_data[0]['Top Keywords'] if cluster_data else "N/A"

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("#### Top Interest")
            st.markdown(f"**{top_interest}**")
        with col2:
            st.markdown("#### Sample Keywords")
            st.markdown(f"`{top_keywords}`")

        # JSON-like output
        st.code(json.dumps(report_json, indent=4), language='json')

        st.markdown("---")
        st.subheader("🔁 Retrain Your Recommendations")

        # Tags from cluster labels
        for cluster in cluster_data:
            st.markdown(f"<span class='recommendation-tag'>{cluster['Cluster Label']}</span>", unsafe_allow_html=True)

        st.text_input("➕ Add new interest:")
        st.button("Generate YouTube Training Plan")

        st.markdown("---")
        st.subheader("🧪 Simulated Recommendations")
        st.markdown("- Based on your interests, YouTube might recommend:")
        for cluster in cluster_data[:2]:
            st.markdown(f"- 🎥 *More on* `{cluster['Cluster Label']}`")

        st.markdown("---")
        st.subheader("📊 Your Viewing Habits Analysis")

        if not interests_df.empty:
            interests_df = interests_df.reset_index()
            pie = px.pie(interests_df, names='Cluster Label', values='Video Count', hole=0.4)
            bar = px.bar(interests_df, x='Video Count', y='Cluster Label', orientation='h')
            pie.update_layout(paper_bgcolor='#0f0f0f', font_color='white')
            bar.update_layout(paper_bgcolor='#0f0f0f', font_color='white')
            st.plotly_chart(pie, use_container_width=True)
            st.plotly_chart(bar, use_container_width=True)
        else:
            st.info("No chart data available.")

    else:
        st.info("Upload your YouTube Takeout ZIP to begin.")
        with st.expander("ℹ️ How to get your YouTube data", expanded=True):
            st.markdown("""
            1. Go to [Google Takeout](https://takeout.google.com/)
            2. Select only **YouTube and YouTube Music**
            3. Choose **HTML format**
            4. Click **Create Export**, then upload the ZIP here.
            """)

if __name__ == "__main__":
    main()