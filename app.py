
import pandas as pd
import streamlit as st
from io import BytesIO
from collections import defaultdict

st.set_page_config(page_title="Dealer Cleaner", layout="centered")
st.title("🧹 Dealer Data Cleaner")

uploaded_file = st.file_uploader("Upload your dealer CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    cleaned_data = []
    dealer_map = defaultdict(list)

    for _, row in df.iterrows():
        address_parts = [
            str(row.get('Dealer Adress 1 SOURCE', '')).strip(),
            str(row.get('Dealer Address 1', '')).strip(),
            str(row.get('Dealer Address 2', '')).strip(),
            str(row.get('Dealer City SOURCE', '')).strip(),
            str(row.get('Dealer State SOURCE', '')).strip(),
            str(row.get('Dealer ZIP Code SOURCE', '')).strip()
        ]
        raw_address = ' '.join([part for part in address_parts if part])

        dealer_id = str(row.get('Dealer Code SOURCE (Original)', '')).strip()
        dealer_name = str(row.get('Dealer Final', '')).strip()
        city = str(row.get('Dealer City SOURCE', '')).strip()
        source = str(row.get('Source', '')).strip()

        key = (dealer_id, raw_address)
        dealer_map[key].append(source)

        cleaned_data.append({
            'Dealer ID': dealer_id,
            'Dealer Name': f"{dealer_name} - {city}" if city else dealer_name,
            'Dealer Address': raw_address,
            'Dealer City': city,
            'Dealer State': str(row.get('Dealer State SOURCE', '')).strip(),
            'Dealer ZIP Code': str(row.get('Dealer ZIP Code SOURCE', '')).strip(),
            'Dealer Country': '',
            'Dealer Website': '',
            'Admin Group': source
        })

    final_data = []
    dealer_seen = {}

    for entry in cleaned_data:
        key = (entry['Dealer ID'], entry['Dealer Address'])
        if key not in dealer_seen:
            similar = [e for e in cleaned_data if e['Dealer ID'] == entry['Dealer ID']]
            if len(similar) > 1:
                entry['Dealer ID'] += "-001"
            sources = list(set([e['Admin Group'] for e in similar]))
            entry['Admin Group'] = ', '.join(sources)
            dealer_seen[key] = True
            final_data.append(entry)

    cleaned_df = pd.DataFrame(final_data)
    st.success("✅ File cleaned successfully!")
    st.dataframe(cleaned_df)

    def to_csv_download(df):
        buffer = BytesIO()
        df.to_csv(buffer, index=False)
        return buffer.getvalue()

    st.download_button(
        label="Download Cleaned CSV",
        data=to_csv_download(cleaned_df),
        file_name="cleaned_dealer_data.csv",
        mime="text/csv"
    )
