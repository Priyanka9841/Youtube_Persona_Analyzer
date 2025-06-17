import pandas as pd
import zipfile
import tempfile
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from bs4 import BeautifulSoup
import json

def extract_watch_history_html(zip_file):
    """Extract watch-history.html from the uploaded Takeout ZIP."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Expected path inside ZIP
        possible_paths = [
            os.path.join(temp_dir, "Takeout", "YouTube and YouTube Music", "history", "watch-history.html"),
            os.path.join(temp_dir, "Takeout", "YouTube", "history", "watch-history.html"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()

        return None  # File not found

def parse_watch_history_html(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    entries = soup.select('div.content-cell.mdl-cell.mdl-cell--6-col.mdl-typography--body-1')

    data = []
    for entry in entries:
        parts = entry.get_text(separator="|").split('|')
        if len(parts) >= 3:
            title = parts[1].strip()
            timestamp = parts[-1].strip()
            data.append({"Title": title, "Timestamp": timestamp})

    df = pd.DataFrame(data)
    if not df.empty:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')
        df = df.dropna(subset=["Timestamp"])
    return df

def cluster_titles(titles, num_clusters=5):
    vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
    X = vectorizer.fit_transform(titles)

    k = min(num_clusters, len(titles)) if len(titles) > 1 else 1
    if k == 1:
        return None, None, None

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X)
    return clusters, kmeans, vectorizer

def get_top_keywords(kmeans, vectorizer, top_n=5):
    terms = vectorizer.get_feature_names_out()
    keywords_per_cluster = []

    for i in range(kmeans.n_clusters):
        center = kmeans.cluster_centers_[i]
        top_indices = center.argsort()[::-1][:top_n]
        keywords = [terms[ind] for ind in top_indices]
        keywords_per_cluster.append(keywords)

    return keywords_per_cluster

def infer_label(keywords):
    if 'shorts' in keywords and 'comedy' in keywords:
        return "Comedy Shorts"
    elif 'shorts' in keywords:
        return "Trending Shorts"
    elif any(k in keywords for k in ['tamil', 'love', 'song']):
        return "Tamil Entertainment"
    elif all(k in keywords for k in ['youtube', 'watch']):
        return "External Links"
    elif 'comedy' in keywords:
        return "Comedy"
    elif any(k in keywords for k in ['gaming', 'stream']):
        return "Gaming"
    elif any(k in keywords for k in ['tutorial', 'how', 'learn']):
        return "Educational"
    return "Mixed/Other"

def generate_structured_profile(df, clusters, keywords_per_cluster):
    if clusters is None:
        return pd.DataFrame([{
            "Cluster ID": 0,
            "Cluster Label": "Single Topic",
            "Top Keywords": df['Title'].iloc[0],
            "Video Count": len(df),
            "Sample Titles": df['Title'].iloc[0]
        }])

    df['Cluster'] = clusters
    structured_data = []

    for i in range(len(keywords_per_cluster)):
        cluster_df = df[df['Cluster'] == i]
        keywords = keywords_per_cluster[i]
        label = infer_label(keywords)
        sample_titles = cluster_df['Title'].sample(min(5, len(cluster_df)), random_state=42).tolist()

        structured_data.append({
            "Cluster ID": i,
            "Cluster Label": label,
            "Top Keywords": ", ".join(keywords),
            "Video Count": len(cluster_df),
            "Sample Titles": " | ".join(sample_titles)
        })

    return pd.DataFrame(structured_data)

def summarize_persona(df):
    if df.empty:
        return "Not enough data to generate a persona."
    top_cluster = df.sort_values("Video Count", ascending=False).iloc[0]
    summary = f"🎯 You mostly watch content related to **{top_cluster['Cluster Label']}**. "
    summary += f"Your favorite topics include: *{top_cluster['Top Keywords']}*."
    return summary

def analyze_youtube_zip(uploaded_zip_file):
    try:
        html_content = extract_watch_history_html(uploaded_zip_file)

        if not html_content:
            return {
                'persona_summary': "❌ Could not find 'watch-history.html' in the uploaded ZIP.",
                'interests_chart_data': pd.DataFrame(),
                'full_report': "{}"
            }

        df = parse_watch_history_html(html_content)
        if df.empty or 'Title' not in df.columns:
            return {
                'persona_summary': "❌ No valid data found in watch-history.html.",
                'interests_chart_data': pd.DataFrame(),
                'full_report': "{}"
            }

        df['Title'] = df['Title'].str.lower()
        titles = df['Title']

        clusters, kmeans, vectorizer = cluster_titles(titles)
        if clusters is None:
            structured_df = generate_structured_profile(df, None, None)
        else:
            keywords_per_cluster = get_top_keywords(kmeans, vectorizer)
            structured_df = generate_structured_profile(df, clusters, keywords_per_cluster)

        persona_summary = summarize_persona(structured_df)
        chart_df = structured_df[["Cluster Label", "Video Count"]].set_index("Cluster Label")

        full_report_json = pd.Series({
            "persona_summary": persona_summary,
            "profile_clusters": structured_df.to_dict(orient="records")
        }).to_json(indent=4)

        return {
            'persona_summary': persona_summary,
            'interests_chart_data': chart_df,
            'full_report': full_report_json
        }

    except Exception as e:
        return {
            'persona_summary': f"❌ Error during processing: {str(e)}",
            'interests_chart_data': pd.DataFrame(),
            'full_report': "{}"
        }