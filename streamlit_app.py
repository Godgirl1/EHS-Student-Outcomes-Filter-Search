import streamlit as st
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from IPython.display import clear_output
#Version 5 - 'No Degree' to 'Workforce' & Blue Color Palet & Spaced Legend

st.set_page_config(page_title="EHS Alumnae Outcomes Dashboard")
st.title('EHS Student Outcomes Dashboard', anchor=False)
st.link_button("By Christian Johnson", "https://linktr.ee/godgirl1?utm_source=linktree_profile_share&ltsid=4ed1c8e4-ed21-4aed-a83b-7f9aed0d584a")
st.header('To start, upload the needed file :envelope_with_arrow: below!', divider='blue')
st.subheader('Please make sure that all the data you would like to filter is in the "All Students" sheet of the workbook.', divider='gray')

#Load Data
uploaded_file = st.file_uploader("Upload 'EHS DataStatistics Phase II (Student Outcomes).xlsx' file", type=['xlsx'])
if uploaded_file:
    Outcomes = pd.read_excel(uploaded_file, sheet_name='All Students', index_col=None, usecols='A:S', dtype={
        'SCHOLARS': 'string',
        'LAST NAME': 'string',
        'FIRST NAME': 'string',
        '900#': 'string',
        'MAJOR': 'category',
        'SUPPORT': 'category',
        'YEAR': 'string',
        'CLASSIFICATION': 'category',
        'CATEGORY': 'string',
        'DEGREE': 'category',
        'CUMMULATIVE GPA': float,
        'OVERALL GPA': float,
        'CELL PHONE NUMBER': 'string',
        'GRADUATE SCHOOL?': 'category',
        'WHAT GRADUATE SCHOOL?': 'string',
        'GRADUATE SCHOOL TYPE (IF ANY)': 'string',
        'MAJOR IN GRADUATE SCHOOL?': 'string',
        'HIGHEST DEGREE FROM GRADUATE SCHOOL': 'category',
        'DECIDED TO WORK/TYPE OF GRADUATE SCHOOL': 'category'
    }, na_values=['N/A', 'NaN', ""])


    #Additional Information
    st.subheader("Dashboard Information")
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
    print(Outcomes.columns)
    def get_degree_options(selected_years, selected_work_type, grad_school):
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

        if 'No Degree' in degrees:
            degrees.remove('No Degree')
            degrees.insert(len(degrees), 'No Degree')
        
        # Remove 'No Degree' from options when "Graduate School?" is "Yes"
        if grad_school == "Yes" and 'No Degree' in degrees:
            degrees.remove('No Degree')

        return degrees

    # Function to get Work Type options filtered by selected years
    def get_work_type_options(selected_years, grad_school):
        # Filter data based on selected years
        if selected_years and 'All Years' in selected_years:
            filtered_data = Outcomes.copy()  # Include all data
        else:
            filtered_data = Outcomes[Outcomes['YEAR'].isin(selected_years)]
            
        work_types = list(filtered_data['DECIDED TO WORK/TYPE OF GRADUATE SCHOOL'].dropna().unique())
        work_types.sort()

        #Sets All at the top of the list and removes unknown option
        if 'All' not in work_types:
            work_types.insert(0, 'All')

        if 'Unknown' in work_types:
            work_types.remove('Unknown')

        # Remove 'Work' from options when "Graduate School?" is "Yes"
        if grad_school == "Yes" and 'Work' in work_types:
            work_types.remove('Work')

        return work_types

    # Filter Widgets
    # Year Selector
    years = ["All Years"] + sorted(Outcomes['YEAR'].dropna().unique())
    selected_years = st.sidebar.multiselect("Select Graduation Year(s):", years, default=["All Years"], label_visibility="visible", key="year_multiselect", help="Select one or more years to filter data by student graduation year.")

    # Graduate School Selector (Added "All Students")
    grad_school = st.sidebar.selectbox("Graduate School?", ["All Students", "Yes", "No"], help="Filter by whether or not the student(s) attended graduate school.")

    # Degree and Work Type Selectors (Based on Graduate School Selection)
    if grad_school == "Yes" or grad_school == "All Students":
        # Work Type Selector (depends on selected years and graduate school status)
        work_types = get_work_type_options(selected_years, grad_school)
        selected_work_type = st.sidebar.multiselect("Post-Graduation Route:", work_types, default=["All"], label_visibility="visible", key="work_multiselect", help="Select the post-graduate route the student(s) pursued, or choose 'All' to include all routes.")

        # Degree Selector (depends on selected years, work type, and graduate school status)
        degree_options = get_degree_options(selected_years, selected_work_type, grad_school)
        selected_degrees = st.sidebar.multiselect("Degree(s):", degree_options, label_visibility="visible", default=["All Degrees"], key="degree_multiselect", help="Select one or more degrees, or choose 'All Degrees' to include all available degrees, under the corresponding post-graduation route.")
    else: #Disable work_type and degree filters, when grad_school == "No"
        selected_work_type = None 
        selected_degrees = None  

    # Main Filtering Function
    def filter_Outcomes(years=None, grad_school=None, degrees=None, work_type=None):
        filtered = Outcomes.copy()

        # Year Filter (only filter if not "All Years")
        if years and "All Years" not in years:
            print(f"Filtering for years: {years}")
            filtered = filtered[filtered['YEAR'].isin(years)]
        
        # Graduate School Filter (only filter if not "All Students")
        if grad_school and grad_school != "All Students":
            print(f"Filtering for graduate school: {grad_school}")
            filtered = filtered[filtered['GRADUATE SCHOOL?'] == grad_school]

        # If "All Students" is selected, only apply degree & work filters to grad students
        if grad_school == "All Students":
            grad_students = filtered[filtered['GRADUATE SCHOOL?'] == "Yes"]

            if degrees and "All Degrees" not in degrees:
                print(f"Filtering for degrees: {degrees}")
                grad_students = grad_students[grad_students['HIGHEST DEGREE FROM GRADUATE SCHOOL'].isin(degrees)]

            if work_type and "All" not in work_type:
                print(f"Filtering for work type: {work_type}")
                grad_students = grad_students[grad_students['DECIDED TO WORK/TYPE OF GRADUATE SCHOOL'].isin(work_type)]

            # Combine filtered grad students with non-grad students
            non_grad_students = filtered[filtered['GRADUATE SCHOOL?'] == "No"]
            filtered = pd.concat([grad_students, non_grad_students])

        else:
            # Apply filters normally if "Yes" or "No" is selected
            if degrees and "All Degrees" not in degrees:
                print(f"Filtering for degrees: {degrees}")
                filtered = filtered[filtered['HIGHEST DEGREE FROM GRADUATE SCHOOL'].isin(degrees)]

            if work_type and "All" not in work_type:
                print(f"Filtering for work type: {work_type}")
                filtered = filtered[filtered['DECIDED TO WORK/TYPE OF GRADUATE SCHOOL'].isin(work_type)]

        print(f"Filtered data size: {filtered.shape}")
        return filtered
    
    def plot_pie_chart(filtered_data, degrees, years=None, work_type=None, degree_col='HIGHEST DEGREE FROM GRADUATE SCHOOL'):
        # Only consider degrees that are part of the filter
        if 'All Degrees' not in degrees:
            filtered_data = filtered_data[filtered_data[degree_col].isin(degrees)]

        # Count occurrences of each degree in the filtered data
        degree_counts = filtered_data[degree_col].value_counts()
        degree_counts = degree_counts[degree_counts > 0] # Filter out degrees with zero occurrences

        # Replace "No Degree" with "Workforce"
        if "No Degree" in degree_counts:
            degree_counts.index = degree_counts.index.str.replace("No Degree", "Workforce")
        
        
        total_count = degree_counts.sum()
        sizes = degree_counts / total_count * 100

        # Calculate explode values based on slice size
        explode = [(count / total_count) * 0.1 for count in degree_counts]  # Adjust 0.1 for desired explosion
        explode = np.clip(explode, 0.005, 0.04)  # Set max and min values for explode so spacing won't be too big or small

        # Determine which labels to show based on a threshold (e.g., >= 5%)
        show_labels = [label if size >= 5 else '' for label, size in zip(degree_counts.index, sizes)]
        text_values = [f'{size:.1f}%' if size >= 5 else '' for size in sizes]
        
        # # Define a custom formatting function that doesn't show percentages 2% or less
        # def autopct_format(pct):
        #     return f'{pct:.1f}%' if pct >= 2 else ''  # Show percentages only if 2% or higher

        # # Define a custom label filter that doesn't show labels if percentage's are 2% or less
        # def filter_labels(labels, sizes):
        #     return [label if size > 2 else '' for label, size in zip(labels, sizes)]
        
        # filtered_labels = filter_labels(degree_counts.index, sizes)

        # Define a custom label filter that doesn't show labels if percentage's are 2% or less
        # def filter_labels(labels, sizes):
        #     return [label if size > 2 else '' for label, size in zip(labels, sizes)]
        
        # sizes = degree_counts / total_count * 100
        # filtered_labels = filter_labels(degree_counts.index, sizes)
        
        # text_template = []
        # for pct in sizes:
        #     if pct >= 2:
        #         text_template.append(f'{pct:.1f}%')
        #     else:
        #         text_template.append('')

        #filtered_labels = [degree if pct >= 2 else '' for degree, pct in zip(degree_counts.index, sizes)]

        # Plot pie chart only if there are multiple degrees or 'All Degrees' is selected and data exists
        if (len(degree_counts) > 1 or 'All Degrees' in degrees) and not degree_counts.empty:
            fig = go.Figure(go.Pie(
                values = degree_counts,
                labels=degree_counts.index,
                hole=0, #No donut pie chart
                text=text_values,
                textinfo='label+text',
                textposition='inside', # Initially set to inside
                insidetextorientation='radial',
                hoverinfo='label+percent',
                #marker=dict(colors=px.colors.qualitative.Set3),  # Use a predefined color set
                pull=explode,
                textfont_size=18
            ))

            # Set a dynamic title based on selected years and work type
            years.sort()
            if years == ['2019', '2021', '2022', '2023', '2024']:
                years = ['All Years'] 
            work_type.sort()
            if work_type == ['Doctorate Biomedical', 'Doctorate Professional', 'Masters Biomedical', 'Masters Professional', 'Ph.D.']:
                work_type = ['All']
            elif work_type == ['Doctorate Biomedical', 'Doctorate Professional']:
                work_type = ['All Doctorate']
            elif work_type == ['Masters Biomedical', 'Masters Professional']:
                work_type = ['All Masters']
            elif work_type == ['Doctorate Biomedical', 'Doctorate Professional', 'Masters Biomedical', 'Masters Professional']:
                work_type = ['All Doctorate & Masters']
            elif work_type == ['Doctorate Biomedical', 'Masters Biomedical']:
                work_type = ['All Biomedical']
            elif work_type == ['Doctorate Professional', 'Masters Professional']:
                work_type = ['All Professional']
            
            years_str = ', '.join(map(str, years)) if years else "Filtered Data"
            work_str = ', '.join(work_type) if work_type else "Filtered Data"

            fig.update_layout(
                title=f"{work_str} Filtered Graduate Degrees' Distribution in {years_str}",
                title_x=0.5,
                uniformtext={'mode': 'hide', 'minsize': 16},
                font_size=16,
                #showlegend=True
            )

            return fig
            # ax.set_title(f"{work_str} Filtered Graduate Degrees' Distribution in {years_str}", pad=20, size=20)
        else:
            # Clear any previous output if conditions for pie chart are not met
            clear_output()
            st.write("Pie chart is not displayed for a single degree selection or if no data is available.")

    #Plotting GPA Chart (calculate and plot the bar chart for average GPA per year)
    def plot_bar_chart(filtered_data, years, degrees, work, graduate):
        # Clear the axis to prevent overplotting
        #ax.clear()

        if filtered_data.empty:
            st.write("No data available for the selected filters. Cannot generate plot.")
            return  # Exit the function to prevent the error

        else:
            fig = go.Figure()

            if "No Degree" in work:
                work.index = work.index.str.replace("No Degree", "Workforce")

            if len(years) == 1 and 'All Years' not in years:
                # If only one year is selected, calculate GPA by degree for that year
                year = years[0]
                avg_gpa_data_per_degree = filtered_data[filtered_data['YEAR'] == year].groupby('HIGHEST DEGREE FROM GRADUATE SCHOOL', observed=False)['CUMMULATIVE GPA'].mean()

                # Filter out degrees with zero occurrences
                avg_gpa_per_degree = avg_gpa_data_per_degree[avg_gpa_data_per_degree > 0]

                # Replace "No Degree" with "Workforce"
                if "No Degree" in avg_gpa_per_degree:
                    avg_gpa_per_degree.index = avg_gpa_per_degree.index.str.replace("No Degree", "Workforce")

                # Generate bar colors using Pastel2 colormap
                colors = cm.Paired(mcolors.Normalize()(range(len(avg_gpa_per_degree))))
                
                # Plot bar chart for GPA by degree
                fig.add_trace(go.Bar(
                    x=avg_gpa_per_degree.index,
                    y=avg_gpa_per_degree.values,
                    text=[f"{val:.2f}" for val in avg_gpa_per_degree.values],
                    textposition='auto',
                    marker_color='rgb(158,202,225)',
                    marker_line_color='rgb(8,48,107)',
                    marker_line_width=1.5,
                ))
                #bars = avg_gpa_per_degree.plot(kind='bar', ax=ax, color=colors, edgecolor='black')

                # # Create dynamic legend
                # handles = [
                #     mpatches.Patch(color=colors[i], label=f"{degree} - {avg_gpa_per_degree[degree]:.2f}")
                #     for i, degree in enumerate(avg_gpa_per_degree.index)
                # ]
                # ax.legend(handles=handles, title="Degrees and Avg GPA", bbox_to_anchor=(1.20, 0.5), loc='center right', fontsize=15, title_fontsize=15)

                # # Set the labels
                # ax.tick_params(axis='both', which='major', labelsize=18)
                # ax.set_xlabel("Degree", fontsize = 18)
                # ax.set_ylabel("Average GPA", fontsize = 18)
                
                if graduate == 'No':
                    title = f"Average GPA of Working Alumnae in {year}"
                    # ax.legend(handles=handles, title="Degrees and Avg GPA", bbox_to_anchor=(1.25, 0.5), loc='center right', fontsize=15, title_fontsize=15)
                else:
                    # Set Dynamic Title
                    work.sort()
                    if work == ['Doctorate Biomedical', 'Doctorate Professional', 'Masters Biomedical', 'Masters Professional', 'Ph.D.']:
                        work= ['All']
                    elif work == ['Doctorate Biomedical', 'Doctorate Professional']:
                        work = ['All Doctorate']
                    elif work == ['Masters Biomedical', 'Masters Professional']:
                        work = ['All Masters']
                    elif work == ['Doctorate Biomedical', 'Doctorate Professional', 'Masters Biomedical', 'Masters Professional']:
                        work = ['All Doctorate & Masters']
                    elif work == ['Doctorate Biomedical', 'Masters Biomedical']:
                        work = ['All Biomedical']
                    elif work == ['Doctorate Professional', 'Masters Professional']:
                        work = ['All Professional']
                    
                    if "All" in work:
                        title = f"Average GPA by Filtered Graduate Degrees in {year}"
                    else:
                        title = f"Average GPA of {', '.join(work)} Filtered Graduate Degrees by Degree in {year}"

                fig.update_layout(
                    title=title,
                    xaxis_title="Degree",
                    yaxis_title="Average GPA",
                    font_size=16,
                    bargap=0.2,
                    plot_bgcolor='rgba(0,0,0,0)',
                )

                # # Set the title on the plot
                # ax.set_title(title, fontsize=20)

                # # Add numeric labels on top of each bar
                # for bar in bars.patches:
                #     ax.text(
                #         bar.get_x() + bar.get_width() / 2,
                #         bar.get_height(),
                #         f'{bar.get_height():.2f}',  # Format to 2 decimal places
                #         ha='center',
                #         va='bottom',
                #         fontsize = 18
                #     )

            else:
                # If multiple years are selected, calculate average GPA per year
                avg_gpa_per_year = filtered_data.groupby('YEAR')['CUMMULATIVE GPA'].mean()

                # Replace "No Degree" with "Workforce"
                if "No Degree" in avg_gpa_per_year :
                    avg_gpa_per_year.index = avg_gpa_per_year.index.str.replace("No Degree", "Workforce")

                # Generate bar colors using Pastel2 colormap
                #colors = cm.Paired(mcolors.Normalize()(range(len(avg_gpa_per_year))))
                
                # Plot bar chart for average GPA per year
                #bars = avg_gpa_per_year.plot(kind='bar', ax=ax, color=colors, edgecolor='black')
                fig.add_trace(go.Bar(
                    x=avg_gpa_per_year.index.astype(str),
                    y=avg_gpa_per_year.values,
                    text=[f"{val:.2f}" for val in avg_gpa_per_year.values],
                    textposition='auto',
                    marker_color='rgb(158,202,225)',
                    marker_line_color='rgb(8,48,107)',
                    marker_line_width=1.5,
                ))

                # # Create dynamic legend
                # handles = [
                #     mpatches.Patch(color=colors[i], label=f"{year} - {avg_gpa_per_year[year]:.2f}")
                #     for i, year in enumerate(avg_gpa_per_year.index)
                # ]
                # ax.legend(handles=handles, title="Years and Avg GPA", bbox_to_anchor=(1.20, 0.5), loc='center right', fontsize=15, title_fontsize=15)

                # # Set the labels
                # ax.tick_params(axis='both', which='major', labelsize=18)
                # ax.set_xlabel("Year", fontsize = 18)
                # ax.set_ylabel("Average GPA", fontsize = 18)

                # Set Dynamic Title
                years.sort()
                if years == ['2019', '2021', '2022', '2023', '2024']:
                    years = ['All Years'] 

                if graduate == 'No':
                    title = f"Average GPA of Working Alumnae per Year in {', '.join(map(str, years))}" if years else "Average GPA per Year"
                    # ax.legend(handles=handles, title="Years and Avg GPA", bbox_to_anchor=(1.25, 0.5), loc='center right', fontsize=15, title_fontsize=15)

                else:
                    # Check if work type is 'All'
                    work.sort()
                    if work == ['Doctorate Biomedical', 'Doctorate Professional', 'Masters Biomedical', 'Masters Professional', 'Ph.D.']:
                        work= ['All']
                    elif work == ['Doctorate Biomedical', 'Doctorate Professional']:
                        work = ['All Doctorate']
                    elif work == ['Masters Biomedical', 'Masters Professional']:
                        work = ['All Masters']
                    elif work == ['Doctorate Biomedical', 'Doctorate Professional', 'Masters Biomedical', 'Masters Professional']:
                        work = ['All Doctorate & Masters']
                    elif work == ['Doctorate Biomedical', 'Masters Biomedical']:
                        work = ['All Biomedical']
                    elif work == ['Doctorate Professional', 'Masters Professional']:
                        work = ['All Professional']
                        
                    if "All" in work:
                        # Handle title for all work types and degrees
                        if len(degrees) <= 4 and "All Degrees" not in degrees:
                            title = f"Average GPA of {', '.join(degrees)} Graduate Degrees per Year in {', '.join(map(str, years))}" if years else "Average GPA per Year"
                        else:
                            title = f"Average GPA of Multiple Graduate Degrees per Year in {', '.join(map(str, years))}" if years else "Average GPA per Year"
                    else:
                        # Handle title when specific work type is selected
                        if len(degrees) <= 4 and "All Degrees" not in degrees:
                            title = f"Average GPA of {', '.join(work)} ({', '.join(degrees)}) Graduate Degrees per Year in {', '.join(map(str, years))}"
                        else:
                            title = f"Average GPA of {', '.join(work)} Filtered Graduate Degrees per Year in {', '.join(map(str, years))}"

                fig.update_layout(
                    title=title,
                    xaxis_title="Year",
                    yaxis_title="Average GPA",
                    font_size=16,
                    bargap=0.2,
                    plot_bgcolor='rgba(0,0,0,0)',
                )


                # # Set the title on the plot
                # ax.set_title(title, fontsize=20)

                # # Add numeric labels on top of each bar
                # for bar in bars.patches:
                #     ax.text(
                #         bar.get_x() + bar.get_width() / 2,
                #         bar.get_height(),
                #         f'{bar.get_height():.2f}',  # Format to 2 decimal places
                #         ha='center',
                #         va='bottom',
                #         fontsize = 18
                #     )

            # # Add grid for readability
            # ax.grid(axis='y', linestyle='--', alpha=0.7)

            # # Rotate x-axis labels for readability
            # ax.tick_params(axis='x', rotation=0)

            # # Increase margins for readability (in case bar labels touch the edge)
            # ax.margins(y=0.1)
            
            return fig

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
        filtered_data = result.copy()
        
        if 'All Degrees' not in degrees:
            filtered_data = result[result['HIGHEST DEGREE FROM GRADUATE SCHOOL'].isin(degrees)]

        degree_counts = filtered_data['HIGHEST DEGREE FROM GRADUATE SCHOOL'].value_counts()
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
            bar_chart = plot_bar_chart(result, years, degrees, work_type, grad_school)
            st.plotly_chart(bar_chart)

        else:
            # Check if there is data for the pie chart (i.e., degree data)
            if ((total_filtered > 1 or 'All Degrees' in degrees) and len(degree_counts) > 1):
                # Create subplots for pie chart and bar chart side by side
                fig = make_subplots(rows=2, cols=1, 
                                    specs=[[{'type': 'domain'}], [{'type': 'xy'}]], # Corrected line.
                                    subplot_titles=["Degree Distribution", "Average GPA"])

                # Plot pie chart for degree distribution
                pie_chart = plot_pie_chart(result, degrees, years=years, work_type=work_type)
                if pie_chart:
                    for trace in pie_chart.data:
                        fig.add_trace(trace, row=1, col=1)

                # Plot bar chart for average GPA per year
                bar_chart = plot_bar_chart(result, years, degrees, work_type, grad_school)
                for trace in bar_chart.data:
                    fig.add_trace(trace, row=2, col=1)

                fig.update_layout(height=800, width=900, title_text="Graduate School Analysis", title_x=0.5)

                st.plotly_chart(fig)

            else:
                # If no data for pie chart, display only the bar chart
                st.write("Pie chart is not displayed for a single degree selection or if no data is available.")
                bar_chart = plot_bar_chart(result, years, degrees, work_type, grad_school)
                st.plotly_chart(bar_chart)

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
            st.text("Hover over the table to search by text or make the table full screen.")
            download_button_csv(result, filename="filtered_data.csv")
            st.dataframe(result)  # Display table after graphs
        else:
            st.write("No data available for download.") 
else:
    st.subheader("No file detected!")
    st.write("Please upload, or reupload, the file 'EHS DataStatistics Phase II (Student Outcomes).xlsx' to start the app.")
    st.write("If the file does not upload, please refresh the page and try again.") 
