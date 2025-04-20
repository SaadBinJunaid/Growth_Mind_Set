import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Set page title and theme
st.set_page_config(page_title="Smart File Converter", layout="wide")

# Custom Styling
st.markdown(
    """
    <style>
        body {background-color: #f4f4f4;}
        .main {background-color: #ffffff; padding: 20px; border-radius: 10px;}
        h1, h2, h3 {color: #0078D7; font-family: 'Arial', sans-serif;}
        .stButton>button {background-color: #28a745; color: white; border-radius: 5px;}
        .stButton>button:hover {background-color: #218838;}
        .stDownloadButton>button {background-color: #0078D7; color: white; border-radius: 5px;}
        .stDownloadButton>button:hover {background-color: #005a9e;}
    </style>
    """,
    unsafe_allow_html=True
)

# App Title
st.title("🚀 Smart File Converter")
st.write("Easily upload, clean, visualize, and convert files!")

# Supported File Types
SUPPORTED_TYPES = {".csv", ".xlsx", ".json", ".txt"}

# File Upload Section
uploaded_files = st.file_uploader(
    "Upload your file (CSV, Excel, JSON, TXT):",
    type=["csv", "xlsx", "json", "txt"],
    accept_multiple_files=True
)

# Process uploaded files
if uploaded_files:
    file_processed = False  # Flag to track if any file was converted

    for file in uploaded_files:
        file_extension = os.path.splitext(file.name)[-1].lower()

        # Check for unsupported file types
        if file_extension not in SUPPORTED_TYPES:
            st.error(f"❌ Unsupported file type: {file_extension}. Please upload CSV, Excel, JSON, or TXT.")
            continue

        # Read the file based on format
        try:
            if file_extension == ".csv":
                df = pd.read_csv(file)
            elif file_extension == ".xlsx":
                df = pd.read_excel(file, engine="openpyxl")
            elif file_extension == ".json":
                df = pd.read_json(file)
            elif file_extension == ".txt":
                df = pd.read_csv(file, delimiter="\t", encoding="utf-8")
        except Exception as e:
            st.error(f"⚠️ Error reading {file.name}: {str(e)}")
            continue

        # Prevent processing empty files
        if df.empty:
            st.warning(f"⚠️ {file.name} is empty and cannot be processed.")
            continue

        # Display file details
        st.write(f"**📄 File Name:** {file.name}")
        st.write(f"**📏 File Size:** {file.size / 1024:.2f} KB")
        st.write("🔍 **Preview:**")
        st.dataframe(df.head())

        # Data Cleaning
        st.subheader("🛠️ Data Cleaning")
        if st.checkbox(f"Remove Duplicates from {file.name}"):
            duplicate_count = df.duplicated().sum()
            if duplicate_count > 0:
                df.drop_duplicates(inplace=True)
                st.write(f"✔️ {duplicate_count} Duplicates Removed!")
            else:
                st.write("✅ No duplicate values found.")

        if st.checkbox(f"Fill Missing Values for {file.name}"):
            missing_count = df.isnull().sum().sum()
            if missing_count > 0:
                df.fillna("Missing", inplace=True)
                st.write(f"✔️ {missing_count} Missing Values Filled!")
            else:
                st.write("✅ No missing values found.")

        # Data Visualization
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show Chart for {file.name}"):
            numeric_df = df.select_dtypes(include="number")
            if not numeric_df.empty:
                st.bar_chart(numeric_df)
            else:
                st.warning(f"✅ No numeric data found in {file.name} for chart visualization.")

        # Conversion Options
        st.subheader("🔄 Convert & Download")
        conversion_type = st.radio(
            f"Convert {file.name} to:", ["CSV", "Excel", "JSON", "TXT"], key=file.name
        )

        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            
            # Ensure correct file extension
            if conversion_type == "Excel":
                file_name = file.name.replace(file_extension, ".xlsx")  # Correct extension for Excel
            else:
                file_name = file.name.replace(file_extension, f".{conversion_type.lower()}")

            try:
                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    mime = "text/csv"
                elif conversion_type == "Excel":
                    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                        df.to_excel(writer, index=False)
                    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                elif conversion_type == "JSON":
                    buffer.write(df.to_json(orient="records", indent=4).encode("utf-8"))
                    mime = "application/json"
                elif conversion_type == "TXT":
                    df.to_csv(buffer, sep="\t", index=False)
                    mime = "text/plain"

                buffer.seek(0)
                st.download_button(
                    label=f"⬇️ Download {file_name}", data=buffer, file_name=file_name, mime=mime
                )

                file_processed = True  # Set flag to true
                st.success(f"🎉 {file.name} successfully converted to {conversion_type}!")

            except Exception as e:
                st.error(f"⚠️ Error converting {file.name}: {str(e)}")

    # ✅ Show success message ONLY if a file was converted
    if file_processed:
        st.success("🎉 File processing complete!")
    else:
        st.info("📝 No files were converted.")
