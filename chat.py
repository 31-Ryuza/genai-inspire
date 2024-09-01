import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from http import HTTPStatus
import dashscope
from dashscope import Application

# Set the base URL for the DashScope API
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

# Function to call the DashScope Agent App
def call_agent_app(prompt):
    response = Application.call(
        app_id='fc813719d2d442959a4571dd74d112f3',
        prompt=prompt,
        api_key='sk-e9176e5a9ab0480b95e9c208da09088a',  # Replace with your valid API key
    )

    if response.status_code != HTTPStatus.OK:
        error_message = f"Request ID: {response.request_id}, Status Code: {response.status_code}, Error Code: {response.code}, Error Message: {response.message}"
        return None, error_message
    else:
        output_text = response.output.get("text", "")
        cleaned_text = output_text.replace("\n", " ")
        return cleaned_text, None

# Load and process Excel data
def load_data():
    df_fasilitas = pd.read_excel('data/fasilitas_pembuangan.xlsx')
    df_sungai = pd.read_excel('data/sungai_tercemar.xlsx')

    return df_fasilitas, df_sungai

 #Plotting functions with data labels
def plot_fasilitas(df_fasilitas, selected_year):
    # Filter data untuk tahun yang dipilih
    filtered_data = df_fasilitas[df_fasilitas['tahun'] == selected_year]
    
    # Urutkan data berdasarkan jumlah desa dari terbesar ke terkecil
    data_sort = filtered_data.sort_values('jumlah_desa', ascending=False)
    
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    
    # Remove confidence intervals by setting ci to None
    ax = sns.barplot(x="nama_kabupaten", y="jumlah_desa", data=data_sort, palette="Blues_d", ci=None)
    
    plt.title(f'Number of Village Waste Disposal Facilities per District in the Year {selected_year}')
    plt.xlabel('District Name')
    plt.ylabel('Number of Villages')
    plt.xticks(rotation=45, ha='right')
    
    # Add data labels (int values)
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 10), textcoords='offset points')
    
    st.pyplot(plt)



def plot_sungai(df_sungai, selected_year):
    # Filter data untuk tahun yang dipilih dan sungai tercemar
    filtered_data = df_sungai[(df_sungai['tahun'] == selected_year) & (df_sungai['sungai_tercemar'] == 'ADA')]
    
    # Urutkan data berdasarkan jumlah sungai tercemar dari terbesar ke terkecil
    filtered_data = filtered_data.sort_values('jumlah', ascending=False)
    
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    
    ax = sns.barplot(x="nama_kabupaten", y="jumlah", data=filtered_data, palette="Reds_d")
    
    plt.title(f'Number of Polluted Rivers per District in {selected_year}')
    plt.xlabel('District Name')
    plt.ylabel('Number of Polluted Rivers')
    plt.xticks(rotation=45, ha='right')
    
    # Add data labels (int values)
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 10), textcoords='offset points')
    
    st.pyplot(plt)


# Streamlit UI
st.title("Dashboard Assistant Smart Goverment")

# Load data
df_fasilitas, df_sungai = load_data()

# Filter for year selection
years = sorted(df_fasilitas['tahun'].unique())
selected_year = st.selectbox("Select Year:", years)

# Dropdown menu to select which data to visualize
data_selection = st.selectbox("Select the data you want to visualize:", 
                              ["Village Waste Disposal Facilities", "Polluted River"])

# Display the selected chart
if data_selection == "Village Waste Disposal Facilities":
    st.subheader(f'Number of Village Waste Disposal Facilities per Regency in the Year {selected_year}')
    plot_fasilitas(df_fasilitas, selected_year)
elif data_selection == "Polluted River":
    st.subheader(f'Number of Polluted Rivers per District in {selected_year}')
    plot_sungai(df_sungai, selected_year)

# Chatbot Section
user_input = st.text_input("Enter your prompt:", value="Waste water data recap")

if st.button("Send"):
    with st.spinner('Processing...'):
        response, error = call_agent_app(user_input)
        if error:
            st.error(error)
        else:
            st.success("Response received!")
            st.text_area("Chatbot Response:", value=response, height=200)

if __name__ == '__main__':
    st.write("Enter a prompt above to interact with the agent app!")
