import streamlit as st
import pandas as pd
import datetime
import os

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="My Goal Diary",
    page_icon="📖",
    layout="wide"
)

FILE_NAME = "my_diary.csv"

# ============================================================
# PASSWORD PROTECTION
# ============================================================

PASSWORD = "1234"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("🔐 My Goal Diary")

    st.write("Please enter your password to access your diary.")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        if password == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()

        else:
            st.error("Incorrect password.")

    st.stop()


# ============================================================
# LOAD EXISTING DIARY
# ============================================================

if os.path.exists(FILE_NAME):

    df = pd.read_csv(FILE_NAME)

else:

    df = pd.DataFrame(
        columns=[
            "Date",
            "Task or Goal",
            "Achieved",
            "Failed",
            "Reason"
        ]
    )


# Make sure the required columns exist
required_columns = [
    "Date",
    "Task or Goal",
    "Achieved",
    "Failed",
    "Reason"
]

for column in required_columns:

    if column not in df.columns:
        df[column] = ""


# Keep columns in correct order
df = df[required_columns]


# Convert dates safely
if not df.empty:

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    ).dt.date


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📖 My Goal Diary")

st.sidebar.write("Welcome to your personal goal tracker!")

if st.sidebar.button("🔒 Logout"):

    st.session_state.logged_in = False
    st.rerun()


# Daily goal setting
st.sidebar.header("🎯 Daily Goal")

daily_goal = st.sidebar.number_input(
    "Tasks to achieve per day",
    min_value=1,
    max_value=100,
    value=3,
    step=1
)


# ============================================================
# TABS
# ============================================================

diary_tab, dashboard_tab = st.tabs(
    ["📖 Diary", "📊 Dashboard"]
)


# ============================================================
# DIARY TAB
# ============================================================

with diary_tab:

    st.title("📖 My Daily Goal Diary")

    st.write(
        "Track what you did today. Be honest with yourself."
    )

    # --------------------------------------------------------
    # ADD TASK
    # --------------------------------------------------------

    st.header("➕ Add Today's Task")

    with st.form(
        "task_form",
        clear_on_submit=True
    ):

        date = st.date_input(
            "Date",
            datetime.date.today()
        )

        task = st.text_input(
            "Task or Goal"
        )

        col1, col2 = st.columns(2)

        with col1:

            achieved = st.checkbox(
                "✅ Achieved"
            )

        with col2:

            failed = st.checkbox(
                "❌ Failed"
            )

        reason = st.text_input(
            "Reason if Failed"
        )

        submitted = st.form_submit_button(
            "💾 Save Entry"
        )

        if submitted:

            if task.strip() == "":

                st.error(
                    "Please enter a task or goal."
                )

            elif achieved and failed:

                st.error(
                    "You can't tick both Achieved and Failed."
                )

            elif not achieved and not failed:

                st.error(
                    "Please select either Achieved or Failed."
                )

            elif failed and reason.strip() == "":

                st.error(
                    "Please state a reason why it failed."
                )

            else:

                new_row = {
                    "Date": date,
                    "Task or Goal": task,
                    "Achieved": "✓" if achieved else "",
                    "Failed": "✓" if failed else "",
                    "Reason": reason
                }

                df = pd.concat(
                    [
                        df,
                        pd.DataFrame([new_row])
                    ],
                    ignore_index=True
                )

                df.to_csv(
                    FILE_NAME,
                    index=False
                )

                st.success(
                    "✅ Entry saved successfully!"
                )

                st.rerun()


    # --------------------------------------------------------
    # DIARY LOG
    # --------------------------------------------------------

    st.header("📋 Your Diary Log")

    if not df.empty:

        display_df = df.copy()

        display_df.index = display_df.index + 1

        st.dataframe(
            display_df,
            use_container_width=True
        )

    else:

        st.info(
            "No entries yet. Add your first task above!"
        )


    # ========================================================
    # EDIT ENTRY
    # ========================================================

    if not df.empty:

        st.header("✏️ Edit Entry")

        selected_index = st.selectbox(
            "Select an entry to edit",
            options=list(df.index),
            format_func=lambda x:
                f"{x + 1}. {df.loc[x, 'Date']} - "
                f"{df.loc[x, 'Task or Goal']}"
        )

        selected_row = df.loc[selected_index]

        with st.form("edit_form"):

            edit_date = st.date_input(
                "Date",
                value=selected_row["Date"]
            )

            edit_task = st.text_input(
                "Task or Goal",
                value=str(
                    selected_row["Task or Goal"]
                )
            )

            edit_status = st.radio(
                "Status",
                ["Achieved", "Failed"],
                index=(
                    0
                    if selected_row["Achieved"] == "✓"
                    else 1
                )
            )

            edit_reason = st.text_input(
                "Reason if Failed",
                value=str(
                    selected_row["Reason"]
                )
            )

            edit_button = st.form_submit_button(
                "💾 Update Entry"
            )

            if edit_button:

                if edit_task.strip() == "":

                    st.error(
                        "Task or goal cannot be empty."
                    )

                elif (
                    edit_status == "Failed"
                    and edit_reason.strip() == ""
                ):

                    st.error(
                        "Please provide a reason for failure."
                    )

                else:

                    df.loc[
                        selected_index,
                        "Date"
                    ] = edit_date

                    df.loc[
                        selected_index,
                        "Task or Goal"
                    ] = edit_task

                    df.loc[
                        selected_index,
                        "Achieved"
                    ] = (
                        "✓"
                        if edit_status == "Achieved"
                        else ""
                    )

                    df.loc[
                        selected_index,
                        "Failed"
                    ] = (
                        "✓"
                        if edit_status == "Failed"
                        else ""
                    )

                    df.loc[
                        selected_index,
                        "Reason"
                    ] = (
                        edit_reason
                        if edit_status == "Failed"
                        else ""
                    )

                    df.to_csv(
                        FILE_NAME,
                        index=False
                    )

                    st.success(
                        "✅ Entry updated!"
                    )

                    st.rerun()


    # ========================================================
    # DELETE ENTRY
    # ========================================================

    if not df.empty:

        st.header("🗑️ Delete Entry")

        delete_index = st.selectbox(
            "Select an entry to delete",
            options=list(df.index),
            format_func=lambda x:
                f"{x + 1}. {df.loc[x, 'Date']} - "
                f"{df.loc[x, 'Task or Goal']}",
            key="delete_select"
        )

        if st.button(
            "🗑️ Delete Selected Entry"
        ):

            df = df.drop(
                index=delete_index
            ).reset_index(drop=True)

            df.to_csv(
                FILE_NAME,
                index=False
            )

            st.success(
                "Entry deleted successfully."
            )

            st.rerun()


    # ========================================================
    # DOWNLOAD CSV
    # ========================================================

    st.header("💾 Export Diary")

    csv = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Download Diary as CSV",
        csv,
        "my_diary.csv",
        "text/csv"
    )


# ============================================================
# DASHBOARD TAB
# ============================================================

with dashboard_tab:

    st.title("📊 Goal Progress Dashboard")

    today = datetime.date.today()


    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    if df.empty:

        total_tasks = 0
        achieved_tasks = 0
        failed_tasks = 0

    else:

        total_tasks = len(df)

        achieved_tasks = (
            df["Achieved"] == "✓"
        ).sum()

        failed_tasks = (
            df["Failed"] == "✓"
        ).sum()


    if total_tasks > 0:

        success_rate = (
            achieved_tasks
            / total_tasks
            * 100
        )

    else:

        success_rate = 0


    # --------------------------------------------------------
    # TODAY'S PROGRESS
    # --------------------------------------------------------

    if not df.empty:

        today_df = df[
            df["Date"] == today
        ]

        today_achieved = (
            today_df["Achieved"] == "✓"
        ).sum()

        today_failed = (
            today_df["Failed"] == "✓"
        ).sum()

    else:

        today_achieved = 0
        today_failed = 0


    today_progress = min(
        today_achieved / daily_goal,
        1.0
    )


    # --------------------------------------------------------
    # TOP STATISTICS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "🎯 Today's Goal",
            daily_goal
        )

    with col2:

        st.metric(
            "✅ Achieved Today",
            today_achieved
        )

    with col3:

        st.metric(
            "❌ Failed Today",
            today_failed
        )

    with col4:

        st.metric(
            "📈 Success Rate",
            f"{success_rate:.1f}%"
        )


    # --------------------------------------------------------
    # TODAY'S PROGRESS BAR
    # --------------------------------------------------------

    st.subheader("🎯 Today's Progress")

    st.progress(
        today_progress
    )

    if today_achieved >= daily_goal:

        st.success(
            "🏆 Daily goal completed! Great work!"
        )

    else:

        remaining = (
            daily_goal
            - today_achieved
        )

        st.info(
            f"You need {remaining} more "
            f"achieved task(s) to reach today's goal."
        )


    # --------------------------------------------------------
    # STREAK CALCULATION
    # --------------------------------------------------------

    def calculate_streaks(data, goal):

        if data.empty:
            return 0, 0

        achieved_by_date = {}

        for current_date in sorted(
            data["Date"].dropna().unique()
        ):

            day_data = data[
                data["Date"] == current_date
            ]

            achieved_count = (
                day_data["Achieved"] == "✓"
            ).sum()

            achieved_by_date[current_date] = (
                achieved_count >= goal
            )

        # Current streak
        current_streak = 0

        check_date = today

        while achieved_by_date.get(
            check_date,
            False
        ):

            current_streak += 1

            check_date -= datetime.timedelta(
                days=1
            )


        # Best streak
        best_streak = 0
        running_streak = 0

        if achieved_by_date:

            all_dates = sorted(
                achieved_by_date.keys()
            )

            previous_date = None

            for current_date in all_dates:

                if (
                    achieved_by_date[current_date]
                    and previous_date is not None
                    and current_date
                    == previous_date
                    + datetime.timedelta(days=1)
                ):

                    running_streak += 1

                elif achieved_by_date[current_date]:

                    running_streak = 1

                else:

                    running_streak = 0

                best_streak = max(
                    best_streak,
                    running_streak
                )

                previous_date = current_date

        return current_streak, best_streak


    current_streak, best_streak = (
        calculate_streaks(
            df,
            daily_goal
        )
    )


    # --------------------------------------------------------
    # STREAK DISPLAY
    # --------------------------------------------------------

    st.subheader("🔥 Streaks")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "🔥 Current Streak",
            f"{current_streak} day(s)"
        )

    with col2:

        st.metric(
            "🏆 Best Streak",
            f"{best_streak} day(s)"
        )


    # --------------------------------------------------------
    # OVERALL STATISTICS
    # --------------------------------------------------------

    st.subheader("📊 Overall Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "📝 Total Tasks",
            total_tasks
        )

    with col2:

        st.metric(
            "✅ Total Achieved",
            achieved_tasks
        )

    with col3:

        st.metric(
            "❌ Total Failed",
            failed_tasks
        )


    # --------------------------------------------------------
    # DAILY PROGRESS CHART
    # --------------------------------------------------------

    st.subheader("📈 Daily Progress")

    if not df.empty:

        chart_data = (
            df.assign(
                Achieved_Count=(
                    df["Achieved"] == "✓"
                ).astype(int)
            )
            .groupby("Date")
            ["Achieved_Count"]
            .sum()
        )

        st.line_chart(
            chart_data
        )

    else:

        st.info(
            "Add some diary entries to see your progress chart."
        )


    # --------------------------------------------------------
    # DAILY SUMMARY
    # --------------------------------------------------------

    st.subheader("📅 Daily Activity")

    if not df.empty:

        daily_summary = (
            df.assign(
                Achieved_Count=(
                    df["Achieved"] == "✓"
                ).astype(int),

                Failed_Count=(
                    df["Failed"] == "✓"
                ).astype(int)
            )
            .groupby("Date")
            .agg(
                Tasks=(
                    "Task or Goal",
                    "count"
                ),
                Achieved=(
                    "Achieved_Count",
                    "sum"
                ),
                Failed=(
                    "Failed_Count",
                    "sum"
                )
            )
            .reset_index()
        )

        daily_summary["Goal Reached"] = (
            daily_summary["Achieved"]
            >= daily_goal
        ).map(
            {
                True: "🏆 Yes",
                False: "❌ No"
            }
        )

        st.dataframe(
            daily_summary.sort_values(
                "Date",
                ascending=False
            ),
            use_container_width=True
        )

    else:

        st.info(
            "No daily activity to display yet."
        )


    # --------------------------------------------------------
    # MOTIVATIONAL MESSAGE
    # --------------------------------------------------------

    st.subheader("💪 Keep Going")

    if current_streak >= 7:

        st.success(
            "🔥 Amazing! You've maintained a "
            "7+ day streak. Keep it going!"
        )

    elif current_streak >= 3:

        st.success(
            "🔥 You're building a strong streak!"
        )

    elif today_achieved >= daily_goal:

        st.success(
            "🎯 You completed today's goal!"
        )

    elif total_tasks == 0:

        st.info(
            "🌱 Start your first goal today."
        )

    else:

        st.info(
            "💪 Every completed task counts. "
            "Keep pushing!"
        )
