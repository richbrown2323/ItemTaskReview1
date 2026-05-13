import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# -----------------------------
# File paths
# -----------------------------
APP_DIR = Path(__file__).parent

INPUT_FILE = APP_DIR / "item_task_review_input.csv"
OUTPUT_FILE = APP_DIR / "item_task_review_results.csv"

# -----------------------------
# Page setup
# -----------------------------
st.title("Item–Task Statement Review")

# -----------------------------
# Load input data
# -----------------------------
df = pd.read_csv(INPUT_FILE)

# Make sure IDs are treated consistently
df["item_id"] = df["item_id"].astype(str)
df["task_id"] = df["task_id"].astype(str)

rater_id = st.text_input("Enter your rater ID")

if not rater_id:
    st.warning("Please enter your rater ID to begin.")
    st.stop()

rater_id = rater_id.strip()

# Create a unique review ID
df["item_id"] = df["item_id"].astype(str)
df["task_id"] = df["task_id"].astype(str)

df["review_id"] = (
    rater_id + "_" +
    df["item_id"] + "_" +
    df["task_id"]
)

# -----------------------------
# Load existing reviews
# -----------------------------
if OUTPUT_FILE.exists():
    reviewed = pd.read_csv(OUTPUT_FILE)
    reviewed_ids = set(reviewed["review_id"].astype(str))
else:
    reviewed = pd.DataFrame()
    reviewed_ids = set()

# -----------------------------
# Download button
# -----------------------------
if OUTPUT_FILE.exists():
    results_df = pd.read_csv(OUTPUT_FILE)

    st.download_button(
        label="Download review results CSV",
        data=results_df.to_csv(index=False),
        file_name="item_task_review_results.csv",
        mime="text/csv",
        key="download_item_task_results"
    )

# -----------------------------
# Identify remaining rows
# -----------------------------
remaining = df[~df["review_id"].isin(reviewed_ids)].reset_index(drop=True)

st.write(f"Remaining items to review: {len(remaining)}")

if len(remaining) == 0:
    st.success("All items have been reviewed.")
    st.stop()

# -----------------------------
# Display next item-task pair
# -----------------------------
row = remaining.iloc[0]

st.subheader(f"Reviewing Item {row['item_id']} / Task {row['task_id']}")

st.markdown("### Task Statement")
st.write(row["task_statement"])

st.markdown("### Item Stem")
st.write(row["stem"])

st.markdown("### Response Options")

for option_col in ["option_a", "option_b", "option_c", "option_d"]:
    if option_col in df.columns and pd.notna(row[option_col]):
        st.write(f"**{option_col.replace('_', ' ').title()}:** {row[option_col]}")

if "correct_answer" in df.columns and pd.notna(row["correct_answer"]):
    st.markdown("### Keyed Correct Answer")
    st.write(row["correct_answer"])

# -----------------------------
# Reviewer questions
# -----------------------------
content_match = st.radio(
    "1. Does the item address the content of the task statement?",
    ["Yes", "No"],
    index=None,
    key="content_match"
)

item_quality = st.radio(
    "2. Is the question clear, understandable, and correct?",
    ["Yes", "No"],
    index=None,
    key="item_quality"
)

suggested_edits = st.text_area(
    "Suggested edits or comments",
    key="suggested_edits"
)

# -----------------------------
# Save review
# -----------------------------
if st.button("Submit review", key="submit_review"):

    if content_match is None or item_quality is None:
        st.warning("Please answer both Yes/No questions before submitting.")
        st.stop()

    new_row = pd.DataFrame([{
    "timestamp": datetime.now().isoformat(timespec="seconds"),
    "rater_id": rater_id,
    "review_id": row["review_id"],
    "item_id": row["item_id"],
    "task_id": row["task_id"],
    "content_match": content_match,
    "item_quality": item_quality,
    "suggested_edits": suggested_edits
}])

    if OUTPUT_FILE.exists():
        new_row.to_csv(OUTPUT_FILE, mode="a", header=False, index=False)
    else:
        new_row.to_csv(OUTPUT_FILE, index=False)

    st.success("Review saved. Loading next item...")
    st.rerun()
