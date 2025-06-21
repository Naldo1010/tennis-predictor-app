
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
import requests

import requests

# Function to fetch player stats from the API
def fetch_player_stats(player_name):
    api_key = 'YOUR_API_KEY'  # Replace with your actual API key
    url = f'https://api-sports.io/players?name={player_name}'
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': 'api-sports.io'
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    
    if data['results']:
        player_data = data['results'][0]
        return {
            "Ranking": player_data['ranking'],
            "Recent Win Rate": player_data['recent_win_rate'],
            "Surface Win Rate": player_data['surface_win_rate'],
            "Head-to-Head Wins": player_data['head_to_head_wins'],
            "First Serve Win %": player_data['first_serve_win_percentage'],
            "Break Point Conversion %": player_data['break_point_conversion_percentage']
        }
    else:
        return None

# Prompt user for player names
player_names = input("Enter the names of the tennis players, separated by commas: ").split(',')

# Initialize mock player statistics
mock_stats = {}

# Fetch and update stats for each player
for player_name in player_names:
    player_name = player_name.strip()
    mock_stats[player_name] = fetch_player_stats(player_name)

# Print updated stats
print(mock_stats)



# Logistic regression model coefficients (mock)
coefficients = {
    "Ranking": -0.01,
    "Recent Win Rate": 2.0,
    "Surface Win Rate": 1.5,
    "Head-to-Head Wins": 0.5,
    "First Serve Win %": 1.2,
    "Break Point Conversion %": 1.0
}
intercept = 0.2

# Streamlit UI
st.title("🎾 Tennis Match Predictor & Player Comparison")

players = list(mock_stats.keys())
player_a = st.selectbox("Select Player A", players, index=0)
player_b = st.selectbox("Select Player B", players, index=1)

if player_a == player_b:
    st.warning("Please select two different players.")
else:
    # Prepare comparison data
    stats = list(mock_stats[player_a].keys())
    data = {
        "Statistic": stats,
        player_a: [mock_stats[player_a][stat] for stat in stats],
        player_b: [mock_stats[player_b][stat] for stat in stats]
    }
    df = pd.DataFrame(data)

    # Display comparison table
    st.subheader("📊 Player Comparison Table")
    st.dataframe(df.set_index("Statistic"))

    # Bar chart with tooltips
    st.subheader("📈 Visual Comparison")
    df_melted = df.melt(id_vars="Statistic", var_name="Player", value_name="Value")
    fig = px.bar(df_melted, x="Statistic", y="Value", color="Player", barmode="group",
                 hover_data=["Player", "Value"], height=400)
    st.plotly_chart(fig)

    # Prediction
    st.subheader("🔮 Match Prediction")
    feature_diff = {
        stat: mock_stats[player_a][stat] - mock_stats[player_b][stat]
        for stat in stats
    }
    linear_sum = intercept + sum(feature_diff[stat] * coefficients[stat] for stat in stats)
    prob = 1 / (1 + np.exp(-linear_sum))
    predicted_winner = player_a if prob > 0.5 else player_b
    st.markdown(f"**Predicted Winner:** {predicted_winner}")
    st.markdown(f"**Win Probability for {player_a}:** {prob:.2%}")

    # Excel download
    st.subheader("📥 Download Comparison Data")
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    st.download_button(
        label="Download as Excel",
        data=excel_buffer.getvalue(),
        file_name="player_comparison.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

