import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Movie Ratings Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("data/movie_ratings.csv")
    return df

df = load_data()

st.title("🎬 Movie Ratings Dashboard")
st.markdown("""
This dashboard provides an interactive analysis of the movie dataset. Use the filters in the sidebar to explore the data and answer key analytical questions about movie ratings, genres, and viewer preferences.
""")


# Sidebar filters
st.sidebar.header("Filters")
unique_ages = sorted(df['age'].unique())
default_age_range = (int(min(unique_ages)), int(max(unique_ages)))
default_occupations = list(df['occupation'].unique())
default_genders = list(df['gender'].unique())

if 'age_range' not in st.session_state:
    st.session_state['age_range'] = default_age_range
if 'occupations' not in st.session_state:
    st.session_state['occupations'] = default_occupations
if 'genders' not in st.session_state:
    st.session_state['genders'] = default_genders

def clear_filters():
    st.session_state['age_range'] = default_age_range
    st.session_state['occupations'] = default_occupations
    st.session_state['genders'] = default_genders

st.sidebar.button("Clear All Filters", on_click=clear_filters)

age_range = st.sidebar.slider(
    "Select Age Range",
    min_value=int(min(unique_ages)),
    max_value=int(max(unique_ages)),
    value=st.session_state['age_range'],
    key='age_range'
)
occupations = st.sidebar.multiselect(
    "Select Occupations",
    options=sorted(df['occupation'].unique()),
    default=st.session_state['occupations'],
    key='occupations'
)
genders = st.sidebar.multiselect(
    "Select Genders",
    options=sorted(df['gender'].unique()),
    default=st.session_state['genders'],
    key='genders'
)

# Filter data
filtered_df = df[(df['age'] >= age_range[0]) & (df['age'] <= age_range[1])]
filtered_df = filtered_df[filtered_df['occupation'].isin(occupations)]
filtered_df = filtered_df[filtered_df['gender'].isin(genders)]

st.subheader("Dataset Preview")
st.dataframe(filtered_df.head(100))

st.markdown("---")

# visualizations summary
st.header("Visualizations")
st.markdown("Below, you will find charts answering the analytical questions. Use the sidebar to filter the data. Remember, a visualization is worth a thousand words!")


# (1) Genre breakdown
st.subheader("1. Breakdown of Genres for Rated Movies")
if filtered_df.empty:
    st.warning("No data available for the selected filters.")
else:
    genre_counts = filtered_df['genres'].str.split('|').explode().value_counts()
    if genre_counts.empty:
        st.warning("No genre data available for the selected filters.")
    else:
        fig1, ax1 = plt.subplots()
        genre_counts.plot(kind='bar', ax=ax1, color='skyblue')
        ax1.set_ylabel('Number of Ratings')
        ax1.set_xlabel('Genre')
        ax1.set_title('Number of Ratings per Genre')
        st.pyplot(fig1)
        st.caption("Each movie can belong to multiple genres. This chart shows the total number of ratings per genre.")

# (2) Highest viewer satisfaction by genre
st.subheader("2. Genres with Highest Viewer Satisfaction")
genre_ratings = filtered_df.copy()
genre_ratings = genre_ratings.assign(genre=genre_ratings['genres'].str.split('|')).explode('genre')
genre_grouped = genre_ratings.groupby('genre').agg(mean_rating=('rating', 'mean'), count=('rating', 'count')).reset_index()
genre_grouped = genre_grouped[genre_grouped['count'] >= 50]  # Minimum threshold
fig2, ax2 = plt.subplots()
sns.barplot(data=genre_grouped.sort_values('mean_rating', ascending=False), x='mean_rating', y='genre', ax=ax2, palette='viridis')
ax2.set_xlabel('Mean Rating')
ax2.set_ylabel('Genre')
ax2.set_title('Mean Rating by Genre (n ≥ 50)')
st.pyplot(fig2)
st.caption("Only genres with at least 50 ratings are shown.")

# (3) Mean rating by movie release year
st.subheader("3. Mean Rating Across Movie Release Years")
year_grouped = filtered_df.groupby('year').agg(mean_rating=('rating', 'mean'), count=('rating', 'count')).reset_index()
year_grouped = year_grouped[year_grouped['count'] >= 50]
fig3, ax3 = plt.subplots()
ax3.plot(year_grouped['year'], year_grouped['mean_rating'], marker='o')
ax3.set_xlabel('Release Year')
ax3.set_ylabel('Mean Rating')
ax3.set_title('Mean Rating by Movie Release Year (n ≥ 50)')
st.pyplot(fig3)
st.caption("How average ratings change with movie release year. Only years with at least 50 ratings are included. Note y-axis does not start at 0.")

# (4) Top 5 best-rated movies (≥50 and ≥150 ratings)
st.subheader("4. Top 5 Best-Rated Movies")
movie_grouped = filtered_df.groupby('title').agg(mean_rating=('rating', 'mean'), count=('rating', 'count')).reset_index()
top5_50 = movie_grouped[movie_grouped['count'] >= 50].sort_values('mean_rating', ascending=False).head(5)
top5_150 = movie_grouped[movie_grouped['count'] >= 150].sort_values('mean_rating', ascending=False).head(5)
st.markdown("**Top 5 Movies (≥ 50 ratings):**")
st.dataframe(top5_50)
st.markdown("**Top 5 Movies (≥ 150 ratings):**")
st.dataframe(top5_150)




