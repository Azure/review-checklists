import pandas as pd
import json
import streamlit as st

with open('./checklists/aks_checklist.en.json') as json_data:
    data = json.load(json_data)

checklistitems = pd.DataFrame(
    data['items'],
    columns=['category', 'subcategory', 'severity', 'text', 'link']
)
categorylist = pd.DataFrame(data['categories'])
severitylist = pd.DataFrame(data['severities'])
statuslist = pd.DataFrame(data['status'])

# TODO: need to convert from json object vs array and set the title dinamically
metadatalist = pd.DataFrame(data=['metadata'])

st.set_page_config(layout="wide")
st.title('FastTrack for Azure - AKS Review')

st.sidebar.title('Review configuration')
st.sidebar.write('')
categoryselector = st.sidebar.multiselect(
    'Select your review categories:', categorylist)

severityselector = st.sidebar.multiselect(
    'Select your review priority target:', severitylist)

sortselector = st.sidebar.selectbox('sort:', checklistitems.columns)

st.metric('Review completed', '92%')

checklistitems.sort_values(by=sortselector, inplace=True)

st.table(checklistitems.loc[(checklistitems['category'].isin(
    categoryselector)) & (checklistitems['severity'].isin(severityselector))])
