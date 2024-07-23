

import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection
from streamlit_float import *
st.set_page_config(page_title="Contract Review Interface", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)


def initialize_guideline(guideline):
    default_values = {
        "id": "",
        "guideline": "",
        "guideline_quality": "Pending",
        "guideline_improvement": "NA",
        "guideline_improvement_other": "",
        "status": "NOT_APPLICABLE",
        "reason": "",
        "reason_quality": "Pending",
        "reason_improvement": "NA",
        "reason_improvement_other": "",
        "comment": "",
        "comment_quality": "Pending",
        "comment_improvement": "NA",
        "comment_improvement_other": "",
        "update_clause_text": "",
        "update_clause_improvement": "NA",
        "update_clause_improvement_other": "",
        "selected_sources": [],
    }

    for key, default_value in default_values.items():
        if key not in guideline:
            guideline[key] = default_value

    return guideline

def read_from_sheets(worksheet="Data"):
    df = conn.read(spreadsheet=st.secrets["spreadsheet"], worksheet=worksheet, ttl=1)
    return df

def update_or_append_to_sheets(values, worksheet="ReviewResults"):
    worksheet = f"ReviewResults_{st.session_state.reviewer_name}"
    existing_data = read_from_sheets(worksheet)

    # Check if the guideline ID already exists
    guideline_id = values[0]  # Assuming the ID is the first element in values
    if existing_data.empty:
        # Initialize the data frame with the first row
        existing_data = pd.DataFrame(columns=["id", "guideline", "guideline_quality", "guideline_improvement", "guideline_improvement_other", "status", "reason", "reason_quality", "reason_improvement_other", "comment", "comment_quality", "comment_improvement_other", "selected_sources", "update_clause_text", "update_clause_improvement", "update_clause_improvement_other"])
    existing_row = existing_data[existing_data['id'] == guideline_id]
    if len(existing_row) > 0:
        # Update existing row
        existing_data.loc[existing_data['id'] == guideline_id] = values
    else:
        # Append new row
        existing_data = existing_data.append(pd.Series(values, index=existing_data.columns), ignore_index=True)

    # Write updated data back to the sheet
    conn.update(spreadsheet=st.secrets["spreadsheet"], data=existing_data, worksheet=worksheet)


def save_guideline(guideline):
    data_to_write = [
        guideline["id"],  # Unique ID for the guideline
        guideline["guideline"],
        guideline["guideline_quality"],
        guideline["guideline_improvement"],
        guideline.get("guideline_improvement_other", ""),
        guideline["status"],
        guideline["reason"],
        guideline["reason_quality"],
        guideline.get("reason_improvement_other", ""),
        guideline["comment"],
        guideline["comment_quality"],
        guideline.get("comment_improvement_other", ""),
        ",".join(guideline["selected_sources"]),
        guideline["update_clause_text"],
        guideline["update_clause_improvement"],
        guideline.get("update_clause_improvement_other", ""),
    ]
    update_or_append_to_sheets(data_to_write)

@st.cache
def get_file_content(file_url):
    return requests.get(file_url).text

def display_contract():
    st.header("Contract")

    contract_link = st.session_state.guidelines[st.session_state.current_guideline]["contract"]
    # Fetch the contract from the URL link
    contract = get_file_content(contract_link)

    selected_sources = st.session_state.guidelines[st.session_state.current_guideline]["selected_sources"]

    def update_selected_sources(key):
        # Only if the checkbox is checked, if unchecked, remove from selected_sources,
        if st.session_state[key]:
            st.session_state.guidelines[st.session_state.current_guideline]["selected_sources"].append(key.split("_")[-1])
        else:
            st.session_state.guidelines[st.session_state.current_guideline]["selected_sources"].remove(key.split("_")[-1])


    # Custom CSS for scrollable container
    st.markdown("""
        <style>
        .streamlit-expanderHeader {
            font-size: 1em;
        }
        .stExpander {
            border: none;
        }
        </style>
    """, unsafe_allow_html=True)
    # Create a scrollable container using st.expander
    with st.expander("Contract Text", expanded=True):
        contract_paragraphs = contract.split("\n")

        for i, paragraph in enumerate(contract_paragraphs):
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                is_selected = str(i) in selected_sources
                st.checkbox(
                    "",
                    value=is_selected,
                    key=f"selected_source_{i}",
                    on_change=update_selected_sources,
                args=(f'selected_source_{i}',))

            with col2:
                st.write(paragraph)

    # Display selected sources (optional)
    if 'selected_sources' in st.session_state and st.session_state.selected_sources:
        st.write("Selected Sources:", ", ".join(sorted(st.session_state.selected_sources)))

def display_guidelines():
    st.header("Guidelines")

    # Give option to select a guideline to review

    guideline = st.session_state.guidelines[st.session_state.current_guideline]
    st.subheader(f"Guideline {st.session_state.current_guideline + 1} of {len(st.session_state.guidelines)}")
    st.write(guideline["guideline"])

    def update_selectbox(key):
        st.session_state.guidelines[st.session_state.current_guideline][key] = st.session_state[f"{key}_{st.session_state.current_guideline}"]

    # Guideline Quality
    st.selectbox(
        f"Guideline Quality: {guideline['guideline_quality']}",
        ("Pending", "Excellent", "Good", "Better", "Bad"),
        key=f"guideline_quality_{st.session_state.current_guideline}",
        on_change=update_selectbox,
        args=('guideline_quality',),
        index=["Pending", "Excellent", "Good", "Better", "Bad"].index(guideline['guideline_quality']),
    )

    if guideline['guideline_quality'] in ["Better", "Bad"]:
        st.selectbox(
            "What can be improved in the guideline?",
            ["NA", "Clarity", "Specificity", "Relevance", "Other"],
            key=f"guideline_improvement_{st.session_state.current_guideline}",
            on_change=update_selectbox,
            args=('guideline_improvement',),
            index=["NA", "Clarity", "Specificity", "Relevance", "Other"].index(guideline['guideline_improvement']),
        )

        if guideline["guideline_improvement"] == "Other":
            guideline["guideline_improvement_other"] = st.text_input(
                "Specify other guideline improvement:",
                value=guideline["guideline_improvement_other"]
            )

    # Guideline Status
    st.radio(
        "Guideline Status",
        ["FOLLOWED", "NOT_FOLLOWED", "NOT_APPLICABLE"],
        key=f"status_{st.session_state.current_guideline}",
        on_change=update_selectbox,
        args=('status',),
        index=["FOLLOWED", "NOT_FOLLOWED", "NOT_APPLICABLE"].index(guideline['status']),
    )

    st.write(
        "Selected Sources:",
        ", ".join([f"Paragraph {i}" for i in guideline['selected_sources']]),
    )

    guideline["reason"] = st.text_area(
        "Reason", value=guideline["reason"], height=100
    )

    # Reason Quality
    st.selectbox(
        "Reason Quality",
        ["Pending", "Excellent", "Good", "Better", "Bad"],
        key=f"reason_quality_{st.session_state.current_guideline}",
        on_change=update_selectbox,
        args=('reason_quality',),
        index=["Pending", "Excellent", "Good", "Better", "Bad"].index(guideline['reason_quality']),
    )

    if guideline["reason_quality"] in ["Better", "Bad"]:
        st.selectbox(
            "What can be improved in the reason?",
            ["NA", "Clarity", "Specificity", "Relevance", "Other"],
            key=f"reason_improvement_{st.session_state.current_guideline}",
            on_change=update_selectbox,
            args=('reason_improvement',),
            index=["NA", "Clarity", "Specificity", "Relevance", "Other"].index(guideline['reason_improvement']),
        )
        if guideline["reason_improvement"] == "Other":
            guideline["reason_improvement_other"] = st.text_input(
                "Specify other reason for improvement:",
                value=guideline["reason_improvement_other"]
            )

    guideline["comment"] = st.text_area(
        "Comment", value=guideline["comment"], height=100
    )

    # Comment Quality
    st.selectbox(
        "Comment Quality",
        ["Pending", "Excellent", "Good", "Better", "Bad"],
        key=f"comment_quality_{st.session_state.current_guideline}",
        on_change=update_selectbox,
        args=('comment_quality',),
        index=["Pending", "Excellent", "Good", "Better", "Bad"].index(guideline['comment_quality']),
    )

    if guideline["comment_quality"] in ["Better", "Bad"]:
        st.selectbox(
            "What can be improved in the comment?",
            ["NA", "Clarity", "Detail", "Relevance", "Other"],
            key=f"comment_improvement_{st.session_state.current_guideline}",
            on_change=update_selectbox,
            args=('comment_improvement',),
            index=["NA", "Clarity", "Detail", "Relevance", "Other"].index(guideline['comment_improvement']),
        )
        if guideline["comment_improvement"] == "Other":
            guideline["comment_improvement_other"] = st.text_input(
                "Specify other comment improvement:",
                value=guideline["comment_improvement_other"]
            )

    guideline["update_clause_text"] = st.text_area(
        "Updated Clause Text", value=guideline["update_clause_text"], height=100
    )

    update_clause = st.radio("Update Clause Text", ["Correct", "Incorrect"])
    if update_clause == "Incorrect":
        st.selectbox(
            "What can be improved in the updated clause text?",
            ["NA", "Changes too extensive", "Does not meet guideline", "Content inaccuracies", "Other"],
            key=f"update_clause_improvement_{st.session_state.current_guideline}",
            on_change=update_selectbox,
            args=('update_clause_improvement',),
            index=["NA", "Changes too extensive", "Does not meet guideline", "Content inaccuracies", "Other"].index(guideline['update_clause_improvement']),
        )
        if guideline["update_clause_improvement"] == "Other":
            guideline["update_clause_improvement_other"] = st.text_input(
                "Specify other update clause improvement:",
                value=guideline["update_clause_improvement_other"]
            )

    st.session_state.guidelines[st.session_state.current_guideline] = guideline
    return guideline


def main():
    st.title("Contract Review Interface")

    # Initialize session state
    if "current_guideline" not in st.session_state:
        st.session_state.current_guideline = 0
    if "selected_sources" not in st.session_state:
        st.session_state.selected_sources = set()
    if "guidelines" not in st.session_state:
        # Assume the guidelines data now includes a unique ID for each guideline
        guidelines = read_from_sheets().to_dict("records")
        st.session_state.guidelines = [initialize_guideline(g) for g in guidelines]

    # Ask for reviewer name

    name = st.text_input("Enter your name:")
    # Add reviewer name to session state
    st.session_state["reviewer_name"] = name

    # Create two columns
    # col1, col2 = st.columns(2)

    # with col1:
    contract = st.session_state.guidelines[st.session_state.current_guideline]["contract"]
    display_contract()

    # col2.float()
    with st.sidebar:
        def update_current_guideline():
            st.session_state.current_guideline = st.session_state.guideline_number - 1

        st.number_input(
            "Guideline Number",
            min_value=1,
            max_value=len(st.session_state.guidelines),
            value=st.session_state.current_guideline + 1,
            key="guideline_number",
            on_change=update_current_guideline,
        )

        updated_guideline = display_guidelines()

        # Save button
        if st.button("Save"):
            save_guideline(updated_guideline)
            st.rerun()

        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("Previous") and st.session_state.current_guideline > 0:
                save_guideline(updated_guideline)
                st.session_state.current_guideline -= 1
                st.rerun()
        with col3:
            if st.button("Next") and st.session_state.current_guideline < len(st.session_state.guidelines) - 1:
                save_guideline(updated_guideline)
                st.session_state.current_guideline += 1
                st.rerun()

        # Progress bar
        progress = (st.session_state.current_guideline + 1) / len(st.session_state.guidelines)
        st.progress(progress)


if __name__ == "__main__":
    main()