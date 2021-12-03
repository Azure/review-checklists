import pandas as pd
import json
import streamlit as st
# import streamlit.components.v1 as components
# import uuid
import time

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


def review_append(id, status, comments):
    if comments:
        payload = {
            'guid': id,
            'Status': status,
            'Comments': comments
        }

        if currentitem[['guid']].isin(st.session_state.completedreviewlist['guid'])[0]:
            st.session_state.completedreviewlist.loc[st.session_state.completedreviewlist['guid'] == currentitem['guid'], [
                'Comments']] = comments
            st.session_state.completedreviewlist.loc[st.session_state.completedreviewlist['guid'] == currentitem['guid'], [
                'Status']] = status
        else:
            st.session_state.completedreviewlist = st.session_state.completedreviewlist.append(
                payload, ignore_index=True, verify_integrity=False)


def review_complete():
    time.sleep(0)


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
        st.session_state.currentitem = 0

if st.session_state.reviewconfigured == True:
    st.sidebar.header('Filters')
    st.session_state.category = st.sidebar.multiselect(
        'Included categories:', st.session_state.categorylist, default=st.session_state.categorylist['name'])

    st.session_state.severity = st.sidebar.multiselect(
        'Included severities:', st.session_state.severitylist, default=st.session_state.severitylist['name'])


# TODO: this needs rework
    st.session_state.sortselector = st.sidebar.multiselect(
        'Sort by:', st.session_state.checklist.columns)
    if st.session_state.sortselector:
        st.session_state.checklist.sort_values(
            by=st.session_state.sortselector, inplace=True)

    st.sidebar.button('Finish Review', on_click=review_complete())

st.sidebar.title("Contribute")
st.sidebar.info(
    "This an open source project and you are very welcome to **contribute** with "
    "comments, questions and review content as "
    "[issues](https://github.com/Azure/review-checklists/issues) or "
    "[pull requests](https://github.com/Azure/review-checklists/pulls) "
    "to the [source code](https://github.com/Azure/review-checklists). "
)

# Setup the main pages
if 'metadata' in st.session_state:
    st.title(st.session_state.metadata['name'])
# else:
#     st.error('Failed to load json.')
#     st.stop()

# Setup the review
if st.session_state.reviewconfigured == False:
    st.warning(
        'Please select the required review and language from the sidebar, then check "Review Configured" to begin your review.')
else:
    if len(st.session_state.category) == 0 or len(st.session_state.severity) == 0:
        st.warning(
            'Please select at least one Category and Severity.')
    else:
        # update target review based on filters
        reviewitems = st.session_state.checklist.loc[(st.session_state.checklist['category'].isin(
            st.session_state.category)) & (st.session_state.checklist['severity'].isin(st.session_state.severity))]

        # set the cursor
        currentitem = reviewitems.iloc[st.session_state.currentitem]

        progresscontainer = st.container()
        with progresscontainer:
            completereviewprogress = st.progress(0)
            filterreviewprogress = st.progress(0)

        # TODO: https://github.com/ikatyang/emoji-cheat-sheet/blob/master/README.md
        # TODO: Implement cursor updates
        currentitemcontainer = st.container()
        with currentitemcontainer:
            ccol1, ccol2, ccol3 = st.columns([12, 1, 1])
            with ccol1:
                st.header('Category: ' + currentitem['category'] +
                          ' - ' + currentitem['subcategory'])
                st.subheader('Severity: ' + currentitem['severity'])
                st.write(currentitem['text'])
                st.write('Learn more: ' + currentitem['link'])
                st.caption(currentitem['guid'])
            with ccol2:
                st.button('< Previous',
                          help='Move to the previous item in the review.')
            with ccol3:
                st.button(
                    'Next>', help='Move to the Next item in the review.')

        # TODO: load existing info and set on screen
        # https://stackoverflow.com/questions/20692122/edit-pandas-dataframe-row-by-row
        with st.form(key='review_form', clear_on_submit=False):
            fcol1, fcol2 = st.columns([9, 1])
            with fcol1:
                reviewcomments = st.text_input(label='Comments')
            with fcol2:
                reviewstatus = st.selectbox(
                    'Status:', st.session_state.statuslist)

            submit_button = st.form_submit_button(
                label='Submit')
            if submit_button:
                review_append(str(currentitem['guid']),
                              reviewstatus, reviewcomments)

        # TODO: style row for current cursor
        reviewitemscontainer = st.container()
        with reviewitemscontainer:
            # filter completed list based on filters, existing review comments are not lost
            with st.expander('Completed review items', True):
                filteredcompletedreviewitems = st.session_state.completedreviewlist.loc[
                    st.session_state.completedreviewlist['guid'].isin(reviewitems['guid'])]
                st.table(filteredcompletedreviewitems)

            with st.expander('Current review items:'):
                st.table(
                    reviewitems[['guid', 'category', 'subcategory', 'severity', 'text']])

        with st.expander('Debug session state'):
            st.session_state

        if len(filteredcompletedreviewitems.index) != 0 and len(st.session_state.completedreviewlist.index) != 0:
            with progresscontainer:
                completereviewprogress.progress(
                    (round(len(st.session_state.completedreviewlist.index) / len(st.session_state.checklist.index) * 100)))
                filterreviewprogress.progress(
                    (round(len(filteredcompletedreviewitems.index) / len(reviewitems.index) * 100)))
        elif len(filteredcompletedreviewitems.index) == 0 and len(st.session_state.completedreviewlist.index) != 0:
            completereviewprogress.progress(
                (round(len(st.session_state.completedreviewlist.index) / len(st.session_state.checklist.index) * 100)))
            filterreviewprogress.progress(0)
        else:
            with progresscontainer:
                completereviewprogress.progress(0)
                filterreviewprogress.progress(0)

# https://gist.github.com/IanCal/6435c2d7b314e491c62568998b31eb40
# https://gist.github.com/treuille/2ce0acb6697f205e44e3e0f576e810b7
# https://towardsdatascience.com/pagination-in-streamlit-82b62de9f62b
# https://discuss.streamlit.io/t/styling-a-row-in-a-dataframe/2245/2
# https://discuss.streamlit.io/t/change-background-color-based-on-value/2614
