

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_float import *
st.set_page_config(page_title="Contract Review Interface", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)



def read_from_sheets(worksheet="Data"):
    df = conn.read(spreadsheet=st.secrets["spreadsheet"], worksheet=worksheet, ttl=1)
    return df

def update_or_append_to_sheets(values, worksheet="ReviewResults"):
    existing_data = read_from_sheets(worksheet)

    # Check if the guideline ID already exists
    guideline_id = values[0]  # Assuming the ID is the first element in values
    if existing_data.empty:
        # Initialize the data frame with the first row
        existing_data = pd.DataFrame(columns=["id", "guideline", "guideline_quality", "guideline_improvement", "status", "reason", "reason_quality", "reason_improvement_other", "comment", "comment_quality", "comment_improvement_other", "selected_sources", "update_clause_improvement_other"])
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
        guideline["status"],
        guideline["reason"],
        guideline["reason_quality"],
        guideline.get("reason_improvement_other", ""),
        guideline["comment"],
        guideline["comment_quality"],
        guideline.get("comment_improvement_other", ""),
        ",".join(guideline["selected_sources"]),
        guideline.get("update_clause_improvement_other", ""),
    ]
    update_or_append_to_sheets(data_to_write)


def display_contract(contract):
    st.header("Contract")

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
                is_selected = str(i) in st.session_state.get('selected_sources', set())
                if st.checkbox("", value=is_selected, key=f"source_{i}"):
                    if 'selected_sources' not in st.session_state:
                        st.session_state.selected_sources = set()
                    st.session_state.selected_sources.add(str(i))
                else:
                    if 'selected_sources' in st.session_state:
                        st.session_state.selected_sources.discard(str(i))
            with col2:
                st.write(paragraph)

    # Display selected sources (optional)
    if 'selected_sources' in st.session_state and st.session_state.selected_sources:
        st.write("Selected Sources:", ", ".join(sorted(st.session_state.selected_sources)))

def display_guidelines(guideline):
    st.header("Guidelines")

    st.subheader(f"Guideline {st.session_state.current_guideline + 1} of {len(st.session_state.guidelines)}")
    st.write(guideline["guideline"])

    guideline_quality = st.selectbox(
        "Guideline Quality", ("Pending", "Excellent", "Good", "Better", "Bad"),
        index=["Pending", "Excellent", "Good", "Better", "Bad"].index(guideline["guideline_quality"]) if "guideline_quality" in guideline else 0,
    )
    print(guideline_quality)
    print("GUIDELINE", guideline["guideline_quality"])
    guideline["guideline_quality"] = guideline_quality
    print("GUIDELINE", guideline["guideline_quality"])
    if guideline["guideline_quality"] in ["Better", "Bad"]:
        guideline["guideline_improvement"] = st.selectbox(
            "What can be improved in the guideline?",
            ["Clarity", "Specificity", "Relevance", "Other"],
            index=["Clarity", "Specificity", "Relevance", "Other"].index(guideline.get("guideline_improvement", "Clarity")),
        )

        if guideline["guideline_improvement"] == "Other":
            guideline["guideline_improvement"] = st.text_input(
                "Specify other guideline improvement:"
            )

    guideline["status"] = st.radio(
        "Guideline Status",
        ["FOLLOWED", "NOT_FOLLOWED", "NOT_APPLICABLE"],
        index=["FOLLOWED", "NOT_FOLLOWED", "NOT_APPLICABLE"].index(guideline["status"]) if "status" in guideline else 2,
    )

    st.write(
        "Selected Sources:",
        ", ".join([f"Paragraph {i}" for i in st.session_state.selected_sources]),
    )

    guideline["reason"] = st.text_area(
        "Reason", value=guideline["reason"], height=100
    )
    guideline["reason_quality"] = st.selectbox(
        "Reason Quality", ["Pending", "Excellent", "Good", "Better", "Bad"],
        index=["Pending", "Excellent", "Good", "Better", "Bad"].index(guideline["reason_quality"]) if "reason_quality" in guideline else 0,
    )
    if guideline["reason_quality"] in ["Better", "Bad"]:
        reason_improvement = st.selectbox(
            "What can be improved in the reason?",
            ["Clarity", "Specificity", "Relevance", "Other"],
            index=["Clarity", "Specificity", "Relevance", "Other"].index(guideline.get("reason_improvement", "Clarity")),
        )
        if reason_improvement == "Other":
            guideline["reason_improvement_other"] = st.text_input(
                "Specify other reason for improvement:"
            )
        else:
            guideline["reason_improvement_other"] = reason_improvement

    guideline["comment"] = st.text_area(
        "Comment", value=guideline["comment"], height=100
    )
    guideline["comment_quality"] = st.selectbox(
        "Comment Quality", ["Pending", "Excellent", "Good", "Better", "Bad"],
        index=["Pending", "Excellent", "Good", "Better", "Bad"].index(guideline["comment_quality"]) if "comment_quality" in guideline else 0,
    )
    if guideline["comment_quality"] in ["Better", "Bad"]:
        comment_improvement = st.selectbox(
            "What can be improved in the comment?",
            ["Clarity", "Detail", "Relevance", "Other"],
            index=["Clarity", "Detail", "Relevance", "Other"].index(guideline.get("comment_improvement", "Clarity")),
        )
        if comment_improvement == "Other":
            guideline["comment_improvement_other"] = st.text_input(
                "Specify other comment improvement:"
            )
        else:
            guideline["comment_improvement_other"] = comment_improvement
    guideline["update_clause_text"] = st.text_area(
        "Updated Clause Text", value=guideline["update_clause_text"], height=100
    )
    update_clause = st.radio("Update Clause Text", ["Correct", "Incorrect"])
    if update_clause == "Incorrect":
        update_clause_improvement = st.selectbox(
            "What can be improved in the updated clause text?",
            ["Changes too extensive", "Does not meet guideline", "Content inaccuracies", "Other"],
            index=["Changes too extensive", "Does not meet guideline", "Content inaccuracies", "Other"].index(guideline.get("update_clause_improvement", "Changes too extensive")),
        )
        if update_clause_improvement == "Other":
            guideline["update_clause_improvement_other"] = st.text_input(
                "Specify other update clause improvement:"
            )
        else:
            guideline["update_clause_improvement_other"] = update_clause_improvement

    guideline["selected_sources"] = list(st.session_state.selected_sources)


    st.session_state.guidelines[st.session_state.current_guideline] = guideline
    # print("GUIDELINE", guideline)
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
        st.session_state.guidelines = read_from_sheets().to_dict("records")

    # Create two columns
    # col1, col2 = st.columns(2)

    # with col1:
    contract = st.session_state.guidelines[st.session_state.current_guideline]["contract"]
    display_contract(contract)

    # col2.float()
    with st.sidebar:
        updated_guideline = display_guidelines(st.session_state.guidelines[st.session_state.current_guideline])

        # Save button
        if st.button("Save"):
            save_guideline(updated_guideline)
            st.rerun()

        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("Previous") and st.session_state.current_guideline > 0:
                # save_guideline(updated_guideline)
                st.session_state.current_guideline -= 1
                st.rerun()
        with col3:
            if st.button("Next") and st.session_state.current_guideline < len(st.session_state.guidelines) - 1:
                # save_guideline(updated_guideline)
                st.session_state.current_guideline += 1
                st.rerun()

        # Progress bar
        progress = (st.session_state.current_guideline + 1) / len(st.session_state.guidelines)
        st.progress(progress)


if __name__ == "__main__":
    main()