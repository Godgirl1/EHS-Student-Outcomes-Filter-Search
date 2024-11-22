import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import clear_output

st.set_page_config(page_title="EHS Alumnae Outcomes Dashboard")
st.title('EHS Student Outcomes Dashboard', anchor=False)
st.link_button("By Christian Johnson", "https://linktr.ee/godgirl1?utm_source=linktree_profile_share&ltsid=4ed1c8e4-ed21-4aed-a83b-7f9aed0d584a")
st.header('To start, upload the needed file :envelope_with_arrow: below!', divider='blue')
st.subheader('Please make sure that all the data you would like to filter is in the "All Students" sheet of the workbook.', divider='gray')

#Load Data
uploaded_file = st.file_uploader("Upload 'EHS DataStatistics Phase II (Student Outcomes).xlsx' file", type=['xlsx'])
if uploaded_file:
    Outcomes = pd.read_excel(uploaded_file, sheet_name='All Students', index_col=None, usecols='A:R', dtype={
        'SCHOLARS': 'string',
        'LAST NAME': 'string',
        'FIRST NAME': 'string',
        '900#': float,
        'MAJOR': 'category',
        'SUPPORT': 'category',
        'YEAR': int,
        'CLASSIFICATION': 'category',
        'CATEGORY': 'string',
        'DEGREE': 'category',
        'CUMMULATIVE GPA': float,
        'OVERALL GPA': float,
        'CELL PHONE NUMBER': 'string',
        'GRADUATE SCHOOL?': 'category',
        'WHAT GRADUATE SCHOOL?': 'string',
        'MAJOR IN GRADUATE SCHOOL?': 'string',
        'HIGHEST DEGREE FROM GRADUATE SCHOOL': 'category',
        'DECIDED TO WORK/TYPE OF GRADUATE SCHOOL': 'category'
    }, na_values=['N/A', 'NaN', ""])

    # # Initialize `filtered_data_for_download` as an empty DataFrame to avoid NameError
    # filtered_data_for_download = pd.DataFrame()

    #Additional Information
    st.subheader("Additional Information")
    st.write(
        """
        This Outcome Dashboard includes a degree pie chart, a GPA bar chart, and the table of filtered alumnae for download.
        - The degree pie chart will show the percentage of degrees existing in your filtered data.
        - The GPA bar chart has multiple configurations:
          - If you only choose one year, the GPA bar chart will show the average GPA per filtered degree type and degree in that year. 
          - Otherwise, if you choose multiple years, the GPA bar chart will take the average GPA of all filtered students in that year. 
        """
    )


    # Sidebar Filters
    st.sidebar.header("Filter Options")

    # Function to get Degree options filtered by selected years and work type
    def get_degree_options(selected_years, selected_work_type):
        # Filter data based on selected years
        if selected_years and 'All Years' in selected_years:
            filtered_data = Outcomes.copy()  # Include all data
        else:
            filtered_data = Outcomes[Outcomes['YEAR'].isin(selected_years)]
       
        # Apply work type filter only if "All" is not selected
        if selected_work_type and 'All' not in selected_work_type:
            filtered_data = filtered_data[filtered_data['DECIDED TO WORK/TYPE OF GRADUATE SCHOOL'].isin(selected_work_type)]

        # Extract unique degrees
        degrees = list(filtered_data['HIGHEST DEGREE FROM GRADUATE SCHOOL'].dropna().unique())
        degrees.sort()

        # Insert 'All Degrees' at the top of the list if not already present
        if 'All Degrees' not in degrees:
            degrees.insert(0, 'All Degrees')
        
        # Remove 'No Degree' from the options if present
        if 'No Degree' in degrees:
            degrees.remove('No Degree')
        return degrees

    # Function to get Work Type options filtered by selected years
    def get_work_type_options(selected_years):
    # Filter data based on selected years
        if selected_years and 'All Years' in selected_years:
            filtered_data = Outcomes.copy()  # Include all data
        else:
            filtered_data = Outcomes[Outcomes['YEAR'].isin(selected_years)]
            
        work_types = list(filtered_data['DECIDED TO WORK/TYPE OF GRADUATE SCHOOL'].dropna().unique())
        work_types.sort()

        if 'All' not in work_types:
            work_types.insert(0, 'All')
        if 'Unknown' in work_types:
            work_types.remove('Unknown')
        if 'Work' in work_types:
            work_types.remove('Work')
        return work_types

    #Filter Widgets
    # Year Selector
    years = ["All Years"] + sorted(Outcomes['YEAR'].dropna().unique())
    selected_years = st.sidebar.multiselect("Select Graduation Year(s):", years, default=["All Years"], label_visibility="visible", key="year_multiselect", help="Select one or more years to filter data by student graduation year.")

    #Graduate School Selector
    grad_school = st.sidebar.selectbox("Graduate School?", ["Yes", "No"], help="Choose if student attended graduate school")
    
    # Conditionally render Degree and Work Type selectors based on grad_school_selection
    if grad_school == "Yes":
        # Degree/Work Type Selector (depends on selected years)
        work_types = get_work_type_options(selected_years)
        selected_work_type = st.sidebar.multiselect("Degree Type:", work_types, default=["All"], label_visibility="visible", key="work_multiselect", help="Select the type of degree the student recieved, or choose 'All' to include all degree types")

        # Degree Selector (depends on selected years and work type)
        degree_options = get_degree_options(selected_years, selected_work_type)
        selected_degrees = st.sidebar.multiselect("Degree(s):", degree_options, label_visibility="visible", default=["All Degrees"],  key="degree_multiselect", help="Select one or more degrees, or choose 'All Degrees' to include all available degrees, under the corrsponding degree type")
    else:
        selected_work_type = None  # Set to None when grad_school = "No"
        selected_degrees = None  # Set to None when grad_school = "No"


    # Main Filtering Function
    def filter_Outcomes(years=None, grad_school=None, degrees=None, work_type=None):
        filtered = Outcomes.copy()

        if years and "All Years" not in years:
            print(f"Filtering for years: {years}")
            filtered = filtered[filtered['YEAR'].isin(years)]
        
        if grad_school:
            print(f"Filtering for graduate school: {grad_school}")
            filtered = filtered[filtered['GRADUATE SCHOOL?'] == grad_school]
        
        if degrees and "All Degrees" not in degrees:
            print(f"Filtering for degrees: {degrees}")
            filtered = filtered[filtered['HIGHEST DEGREE FROM GRADUATE SCHOOL'].isin(degrees)]
        
        if work_type and "All" not in work_type:
            print(f"Filtering for work type: {work_type}")
            filtered = filtered[filtered['DECIDED TO WORK/TYPE OF GRADUATE SCHOOL'].isin(work_type)]

        print(f"Filtered data size: {filtered.shape}")
        return filtered
    
    def plot_pie_chart(ax, filtered_data, degrees, years=None, work_type=None, degree_col='HIGHEST DEGREE FROM GRADUATE SCHOOL'):
        # Only consider degrees that are part of the filter
        if 'All Degrees' not in degrees:
            filtered_data = filtered_data[filtered_data[degree_col].isin(degrees)]

        # Count occurrences of each degree in the filtered data
        degree_counts = filtered_data[degree_col].value_counts()
        degree_counts = degree_counts[degree_counts > 0] # Filter out degrees with zero occurrences
        
        # Calculate explode values based on slice size
        total_count = degree_counts.sum()
        explode = [(count / total_count) * 0.1 for count in degree_counts]  # Adjust 0.1 for desired explosion
        explode = np.clip(explode, 0.005, 0.04)  # Set max and min values for explode so spacing won't be too big or small

        # Plot pie chart only if there are multiple degrees or 'All Degrees' is selected and data exists
        if (len(degree_counts) > 1 or 'All Degrees' in degrees) and not degree_counts.empty:
            patches, labels, pct_texts = ax.pie(
                degree_counts,
                labels=degree_counts.index,
                autopct='%1.1f%%',
                startangle=90,
                colors=plt.cm.Paired.colors, #plt.get_cmap('cool')(np.linspace(0.25, 1.0, len(degree_counts))),
                explode=explode,
                pctdistance=0.85,
                labeldistance=1.17,
                rotatelabels=False,
                textprops={'fontsize': 16}
            )

            # Rotate labels and percentages based on angle for readability
            for i, (label, pct_text) in enumerate(zip(labels, pct_texts)):
                percentage_value = float(pct_text.get_text().strip('%'))
                if percentage_value < 5:
                    angle = (patches[i].theta2 + patches[i].theta1) / 2  # Mid-angle of slice
                    rotation = angle if 90 < angle < 270 else angle  # Adjust rotation for readability
                    label.set_rotation(rotation)
                    label.set_horizontalalignment("center")
                    pct_text.set_rotation(rotation)

            # Set a dynamic title based on selected years and work type
            years_str = ', '.join(map(str, years)) if years else "Filtered Data"
            work_str = ', '.join(work_type) if work_type else "Filtered Data"
            ax.set_title(f"{work_str} Degree Type Distribution in {years_str}", pad=42, size=18)
            ax.axis('equal')  # Ensures pie chart is circular
        else:
            # Clear any previous output if conditions for pie chart are not met
            clear_output()
            st.write("Pie chart is not displayed for a single degree selection or if no data is available.")

    #Plotting GPA Chart (calculate and plot the bar chart for average GPA per year)
    def plot_bar_chart(ax, filtered_data, years, degrees, work, graduate):
        # Clear the axis to prevent overplotting
        ax.clear()

        if filtered_data.empty:
            st.write("No data available for the selected filters. Cannot generate plot.")
            return  # Exit the function to prevent the error
        
        else:
            if len(years) == 1 and 'All Years' not in years:
                # If only one year is selected, calculate GPA by degree for that year
                year = years[0]
                avg_gpa_data_per_degree = filtered_data[filtered_data['YEAR'] == year].groupby('HIGHEST DEGREE FROM GRADUATE SCHOOL', observed=False)['CUMMULATIVE GPA'].mean()

                # Filter out degrees with zero occurrences
                avg_gpa_per_degree = avg_gpa_data_per_degree[avg_gpa_data_per_degree > 0]

                # Plot bar chart for GPA by degree
                bars = avg_gpa_per_degree.plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')

                # Set the labels
                ax.tick_params(axis='both', which='major', labelsize=15)
                ax.set_xlabel("Year", fontsize = 15)
                ax.set_ylabel("Average GPA", fontsize = 15)

                # Set Dynamic Title
                if graduate == 'No':
                    ax.set_title(f"Average GPA of Working Alumnae in {year}", fontsize=16)
                else:
                    if work == 'All':
                        ax.set_title(f"Average GPA by Degree in {year}", fontsize=16)
                    else:
                        ax.set_title(f"Average GPA of {', '.join(work)} Degrees by Degree in {year}", fontsize=16)

                # Add numeric labels on top of each bar
                for bar in bars.patches:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height(),
                        f'{bar.get_height():.2f}',  # Format to 2 decimal places
                        ha='center',
                        va='bottom',
                        fontsize = 14
                    )

            else:
                # If multiple years are selected, calculate average GPA per year
                avg_gpa_per_year = filtered_data.groupby('YEAR')['CUMMULATIVE GPA'].mean()

                # Plot bar chart for average GPA per year
                bars = avg_gpa_per_year.plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')

                # Set the labels
                ax.tick_params(axis='both', which='major', labelsize=15)
                ax.set_xlabel("Year", fontsize = 15)
                ax.set_ylabel("Average GPA", fontsize = 15)

                # Set Dynamic Title
                if graduate == 'No':
                    ax.set_title(f"Average GPA of Working Alumnae per Year in {', '.join(map(str, years))}" if years else "Average GPA per Year", fontsize=16)
                else:
                    # Check if work type is 'All'
                    if "All" in work:
                        # Handle title for all work types and degrees
                        if len(degrees) <= 4 and "All Degrees" not in degrees:
                            title = f"Average GPA of {', '.join(degrees)} Degrees per Year in {', '.join(map(str, years))}" if years else "Average GPA per Year"
                        else:
                            title = f"Average GPA of Multiple Degrees per Year in {', '.join(map(str, years))}" if years else "Average GPA per Year"
                    else:
                        # Handle title when specific work type is selected
                        if len(degrees) <= 4 and "All Degrees" not in degrees:
                            title = f"Average GPA of {', '.join(work)} ({', '.join(degrees)}) Degrees per Year in {', '.join(map(str, years))}"
                        else:
                            title = f"Average GPA of {', '.join(work)} Degrees per Year in {', '.join(map(str, years))}"

                    # Set the title on the plot
                    ax.set_title(title, fontsize=16)

                # Add numeric labels on top of each bar
                for bar in bars.patches:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height(),
                        f'{bar.get_height():.2f}',  # Format to 2 decimal places
                        ha='center',
                        va='bottom',
                        fontsize = 14
                    )

            # Add grid for readability
            ax.grid(axis='y', linestyle='--', alpha=0.7)

            # Rotate x-axis labels for readability
            ax.tick_params(axis='x', rotation=0)

    # Modified main function to display both filtered data and charts
    def show_filtered_Outcomes(years, grad_school, work_type, degrees):

        result = filter_Outcomes(years=years, grad_school=grad_school, degrees=degrees, work_type=work_type)
        print(f"Result data size: {result.shape}")
        # filtered_data_for_download = result  # Store the result DataFrame

        total_filtered = len(result)
        total_students = len(Outcomes)

        if 'All Years' in selected_years:
            total_students_in_years = total_students
        else:
            total_students_in_years = len(Outcomes[Outcomes['YEAR'].isin(selected_years)])
        
        # Count occurrences of each degree in the filtered data
        degree_counts = result['HIGHEST DEGREE FROM GRADUATE SCHOOL'].value_counts()
        degree_counts = degree_counts[degree_counts > 0] # Filter out degrees with zero occurrences

        # Clear previous output to prevent flashing
        clear_output(wait=True)

        # Display filtered Outcomes and statistics
        st.write("")
        st.write(f"Total entries in selected years: {total_students_in_years}")
        st.write(f"Total filtered entries: {total_filtered}")
        
        # Avoid division by zero
        if total_students_in_years == 0:
            st.warning("No students found for the selected filters.")
            st.write(f"Percentage of filtered entries in selected years: 0.00%")
        else:
            percentage_in_years = (total_filtered / total_students_in_years) * 100
            st.write(f"Percentage of filtered entries in selected years: {percentage_in_years:.2f}%")
        
        if total_students == 0:
            st.warning("No students found in the datasheet. Is there data in the 'All Students' sheet of the workbook?")
            st.write(f"Percentage of filtered entries in total Outcomes: 0.00%")
        else:
            percentage = (total_filtered / total_students) * 100
            st.write(f"Percentage of filtered entries in total Outcomes: {percentage:.2f}%")
      
        st.write("")

        if grad_school == 'No':
            st.write("Degree Type: Work (No Graduate School)")
            st.write("Degree(s): No Degree")
            st.write("")
            st.write("Graduate School is set to 'No'. No degree data to plot in the pie chart.")

            # Plot only the bar chart, occupying the entire plot area
            fig, ax = plt.subplots(figsize=(15, 7))
            plot_bar_chart(ax, result, years, degrees, work_type, grad_school)
            
            st.pyplot(fig)

        else:
            # Check if there is data for the pie chart (i.e., degree data)
            if ((total_filtered > 1 or 'All Degrees' in degrees) and len(degree_counts) > 1):
                # Create subplots for pie chart and bar chart side by side
                fig, axes = plt.subplots(2, 1, figsize=(20, 20))

                # Plot pie chart for degree distribution
                plot_pie_chart(axes[0], result, degrees, years=years, work_type=work_type)

                # Plot bar chart for average GPA per year
                plot_bar_chart(axes[1], result, years, degrees, work_type, grad_school)

                st.pyplot(fig)

            else:
                # If no data for pie chart, display only the bar chart
                st.write("Pie chart is not displayed for a single degree selection or if no data is available.")
                fig, ax = plt.subplots(figsize=(15, 7))
                plot_bar_chart(ax, result, years, degrees, work_type, grad_school)
                
                st.pyplot(fig)

        st.write("")
        # Return the DataFrame to ensure it’s displayed automatically
        return result
    
    #Define the function to run when downlaod button clicked
    def download_button_csv(dataframe, filename=None):
        csv = dataframe.to_csv(index=False)
        st.download_button(
            label="Download Filtered Data (CSV File)",
            data=csv,
            file_name=filename,
            mime='text/csv'
        )


    # Trigger display of filtered data and charts
    st.sidebar.text('')
    if st.sidebar.button('Show Outcomes'):      
        result = show_filtered_Outcomes(selected_years, grad_school, selected_work_type, selected_degrees)
        if not result.empty:
            st.write("### Filtered Data Table")
            st.text("Hover over the table to search by text or make the table full screen")
            download_button_csv(result, filename="filtered_data.csv")
            st.dataframe(result)  # Display table after graphs
        else:
            st.write("No data available for download.")  
