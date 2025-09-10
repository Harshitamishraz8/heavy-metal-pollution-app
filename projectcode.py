import pandas as pd
import streamlit as st
import plotly.express as px

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
        # Simple avg method (for demo), formula can be refined
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

st.title("🌍 Heavy Metal Pollution Indices Calculator")

uploaded_file = st.file_uploader("Upload your cleaned water quality dataset (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("Raw Dataset")
    st.dataframe(df.head())

    # Calculate indices
    indices_df = calculate_indices(df)
    st.subheader("Calculated Pollution Indices")
    st.dataframe(indices_df)

    # Download option
    csv = indices_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Results as CSV", csv, "results.csv", "text/csv")

    # Visualization: Status distribution
    st.subheader("Water Quality Classification")
    fig = px.pie(indices_df, names="Status", title="Safe vs Unsafe Water Sources")
    st.plotly_chart(fig)

    # Map visualization
    st.subheader("Geographical Visualization")
    fig_map = px.scatter_mapbox(
        indices_df,
        lat="Latitude",
        lon="Longitude",
        color="Status",
        hover_name="Location",
        mapbox_style="carto-positron",
        zoom=4,
        title="Heavy Metal Pollution Map"
    )
    st.plotly_chart(fig_map)
