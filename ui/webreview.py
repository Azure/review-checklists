import pandas as pd
import json
import streamlit as st
import streamlit.components.v1 as components
import uuid

from streamlit.state.session_state import SessionState

# TODO: move to code provided by index json


def review_select(review):
    switcher = {
        'Landing Zone': 'lz',
        'Azure Kubernetes Service': 'aks',
        'Azure Virtual Desktop': 'avd',
        'Security': 'security'
    }
    return switcher.get(review, 'lz')


def language_select(lang):
    switcher = {
        'English': 'en',
        'Spanish': 'es',
        'Japanese': 'ja',
        'Korean': 'ko',
        'Portuguese': 'pt'
    }
    return switcher.get(lang, 'en')


def review_reset():
    if st.session_state.reviewconfigured == False:
        # TODO: reset the completereviewitems if category changes
        if 'checklist' in st.session_state:
            del st.session_state['checklist']


def review_append():
    st.session_state.completedreviewlist = st.session_state.completedreviewlist.append(
        {'guid': '{}'.format(uuid.uuid4()), 'Status': 'Fulfilled', 'Comments': 'This is a review comment'}, ignore_index=True)


st.set_page_config(
    layout="wide", page_title='FastTrack for Azure - Review', page_icon=":eyeglasses:")

# Setup the sidebar
st.sidebar.title('FastTrack for Azure')
st.sidebar.header('Review configuration')

# Load available checklists
if ('reviewindex' not in st.session_state) or ('reviewlanguages' not in st.session_state):
    with open('./checklists/index.json') as json_data:
        reviewindex = json.load(json_data)
    st.session_state.reviewindex = pd.DataFrame(
        reviewindex['checklists']
    )
    st.session_state.reviewlanguages = pd.DataFrame(
        reviewindex['languages']
    )

if 'reviewconfigured' not in st.session_state:
    st.session_state.reviewconfigured = False

if st.session_state.reviewconfigured == False:
    st.session_state.review = [st.sidebar.selectbox('Please select the review type:',
                                                    st.session_state.reviewindex['Name'], key='reviewselector')]

# if (('languageselector' not in st.session_state) and (st.session_state.reviewconfigured == False)):
if st.session_state.reviewconfigured == False:
    st.session_state.language = st.sidebar.selectbox('Please select the review language:',
                                                     st.session_state.reviewlanguages['Name'], key='languageselector')

st.sidebar.checkbox(
    'Review configured', on_change=review_reset(), key='reviewconfigured')

# Load the review
if ('checklist' not in st.session_state) and (st.session_state.reviewconfigured == True):
    with open('./checklists/' + review_select(st.session_state.review[0]) + '_checklist.' + language_select(st.session_state.language) + '.json') as json_data:
        data = json.load(json_data)

    st.session_state.checklist = pd.DataFrame(data['items'])
    st.session_state.categorylist = pd.DataFrame(data['categories'])
    st.session_state.severitylist = pd.DataFrame(data['severities'])
    st.session_state.statuslist = pd.DataFrame(data['status'])
    st.session_state.metadata = data['metadata']

    if 'completedreviewlist' not in st.session_state:
        st.session_state.completedreviewlist = pd.DataFrame(
            columns=['guid', 'Status', 'Comments'])

st.sidebar.header('Filters')

if st.session_state.reviewconfigured == True:
    st.session_state.category = st.sidebar.multiselect(
        'Included categories:', st.session_state.categorylist, default=st.session_state.categorylist['name'])

    st.session_state.severity = st.sidebar.multiselect(
        'Included severities:', st.session_state.severitylist, default=st.session_state.severitylist['name'])

    st.session_state.sortselector = st.sidebar.multiselect(
        'Sort by:', st.session_state.checklist.columns)
    if st.session_state.sortselector:
        st.session_state.checklist.sort_values(
            by=st.session_state.sortselector, inplace=True)

st.sidebar.title("Contribute")
st.sidebar.info(
    "This an open source project and you are very welcome to **contribute** with "
    "comments, questions and resources as "
    "[issues](https://github.com/Azure/review-checklists/issues) or "
    "[pull requests](https://github.com/Azure/review-checklists/pulls) "
    "to the [source code](https://github.com/Azure/review-checklists). "
)

# Setup the main pagest
if 'metadata' in st.session_state:
    st.title(st.session_state.metadata['name'])
# else:
#     st.title('FastTrack for Azure - Review')

# Setup the review

if st.session_state.reviewconfigured == False:
    st.warning(
        'Please select the required review and language from the sidebar, then check "Review Configured" to begin your review.')
else:
    # update target review based on filters
    reviewitems = st.session_state.checklist.loc[(st.session_state.checklist['category'].isin(
        st.session_state.category)) & (st.session_state.checklist['severity'].isin(st.session_state.severity))]

    # review progress
    reviewcount = len(reviewitems.index)
    completedcount = len(st.session_state.completedreviewlist.index)

    colpercent, colprogress, colcompleted = st.columns(3)

    with colpercent:
        str(completedcount) + \
            '/' + str(reviewcount)
    with colprogress:
        if (completedcount == 0):
            reviewprogress = 0
        else:
            reviewprogress = st.progress(
                (round(completedcount / reviewcount * 100)))
    with colcompleted:
        reviewcompleted = st.checkbox('Review completed')

    increment = st.button('Increment', on_click=review_append)

    st.table(st.session_state.completedreviewlist)
    st.table(
        reviewitems[['category', 'subcategory', 'severity', 'text', 'link']])
    # st.dataframe(reviewitems)

    # with st.expander('Documentation'):
    #     components.iframe(
    #         'https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles', height=600, scrolling=True)

    # if reviewcompleted:
    #     st.balloons()

    with st.expander('Debug session state'):
        st.session_state
