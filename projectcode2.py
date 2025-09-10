import pandas as pd
import streamlit as st
import plotly.express as px
import folium
from streamlit_folium import st_folium

# ---------------------------
# Helper functions
# ---------------------------

def calculate_indices(df):
    """Calculate Heavy Metal Pollution Indices (HPI, HEI, Cd, PLI, CF)."""

    # Standard permissible limits (example values, can be updated as per WHO/ISI)
    standard_limits = {
        "Fe (ppm)": 0.3,
        "As (ppb)": 10,
        "U (ppb)": 30
    }

    results = []

    for idx, row in df.iterrows():
        Fe = row.get("Fe (ppm)", None)
        As = row.get("As (ppb)", None)
        U  = row.get("U (ppb)", None)

        if pd.isna(Fe) or pd.isna(As) or pd.isna(U):
            continue

        # Convert As, U from ppb to ppm for uniformity
        As_ppm = As / 1000
        U_ppm = U / 1000

        # --- Contamination Factor (CF) ---
        CF_Fe = Fe / standard_limits["Fe (ppm)"]
        CF_As = As / standard_limits["As (ppb)"]
        CF_U  = U / standard_limits["U (ppb)"]

        # --- Pollution Load Index (PLI) ---
        PLI = (CF_Fe * CF_As * CF_U) ** (1/3)

        # --- Heavy Metal Pollution Index (HPI) ---
        HPI = (CF_Fe + CF_As + CF_U) / 3 * 100

        # --- Heavy Metal Evaluation Index (HEI) ---
        HEI = CF_Fe + CF_As + CF_U

        # --- Degree of Contamination (Cd) ---
        Cd = HEI

        # Classification
        if HPI < 100:
            status = "Safe"
        elif HPI < 200:
            status = "Marginal"
        else:
            status = "Polluted"

        results.append({
            "Location": row.get("Location"),
            "Longitude": row.get("Longitude"),
            "Latitude": row.get("Latitude"),
            "Fe (ppm)": Fe,
            "As (ppb)": As,
            "U (ppb)": U,
            "HPI": HPI,
            "HEI": HEI,
            "Cd": Cd,
            "PLI": PLI,
            "Status": status
        })

    return pd.DataFrame(results)


# ---------------------------
# Streamlit App
# ---------------------------

st.set_page_config(page_title="Water Pollution Dashboard", layout="wide")
st.title("🌍 Heavy Metal Pollution Indices Dashboard")

uploaded_file = st.file_uploader("📂 Upload your cleaned water quality dataset (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File uploaded successfully!")

    with st.expander("📋 View Raw Dataset"):
        st.dataframe(df.head())

    # Calculate indices
    indices_df = calculate_indices(df)

    st.header("📊 Calculated Pollution Indices")
    st.dataframe(indices_df)

    # Download option
    csv = indices_df.to_csv(index=False).encode('utf-8')
    st.download_button("💾 Download Results as CSV", csv, "results.csv", "text/csv")

    # Status Distribution
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Status Distribution (Pie Chart)")
        fig = px.pie(indices_df, names="Status", title="Safe vs Unsafe Water Sources")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Status Distribution (Bar Chart)")
        fig_bar = px.bar(indices_df, x="Location", y="HPI", color="Status", title="HPI by Location")
        st.plotly_chart(fig_bar, use_container_width=True)

    # Plotly Map
    st.subheader("🗺️ Geographical Visualization (Plotly)")
    fig_map = px.scatter_mapbox(
        indices_df,
        lat="Latitude",
        lon="Longitude",
        color="Status",
        hover_name="Location",
        size_max=15,
        mapbox_style="carto-positron",
        zoom=4,
        title="Heavy Metal Pollution Map"
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Folium Map
    st.subheader("🌐 Interactive Map (Folium)")
    if not indices_df.empty:
        m = folium.Map(location=[indices_df["Latitude"].mean(), indices_df["Longitude"].mean()], zoom_start=5)

        # Color code markers
        for _, row in indices_df.iterrows():
            if row["Status"] == "Safe":
                color = "green"
            elif row["Status"] == "Marginal":
                color = "orange"
            else:
                color = "red"

            popup_text = f"""
            <b>{row['Location']}</b><br>
            HPI: {row['HPI']:.2f}<br>
            HEI: {row['HEI']:.2f}<br>
            Status: {row['Status']}
            """
            folium.CircleMarker(
                location=[row["Latitude"], row["Longitude"]],
                radius=7,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=popup_text
            ).add_to(m)

        st_folium(m, width=800, height=500)
