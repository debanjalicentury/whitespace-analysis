import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
from plotly.subplots import make_subplots
#import base64

target_uncovered_retailers = pd.read_csv(r'C:\Users\debanjali.basu\Documents\white space analysis\target_uncovered_retailers_bangalore_urban_dist_v1.csv')
site_details = pd.read_excel(r'C:\Users\debanjali.basu\Documents\white space analysis\matched_site_details.xlsx')

avg_data = {
    "villages/ngbrhd": ["Begur n'brhd", "Bellanduru n'brhd"],
    "Territory Code": [512443, 512434],
    "Average Order nos": [37, 25]
}


# Create DataFrame
average_order_df = pd.DataFrame(avg_data)


st.logo('CENTURYPLY_logo.png', link=None, icon_image=None)
#st.sidebar.image('CENTURYPLY_logo.png', width=200)


st.header(":red[Retailer Radar]",divider="gray")
st.markdown(":gray[Track and uncover retailers in any city]")

#data operations
# Filter out rows where 'Retailer_name' is 'Total'
target_uncovered_retailers = target_uncovered_retailers[
    target_uncovered_retailers['Retailer_name'] != 'Total'
]

site_details = site_details[
    site_details['Property_name'] != 'Total'
]

# Split Lat/Lon into separate Latitude and Longitude columns
target_uncovered_retailers[['LAT', 'LON']] = target_uncovered_retailers['Lat/Lon'].str.split(', ', expand=True)
target_uncovered_retailers['LAT'] = target_uncovered_retailers['LAT'].astype(float)
target_uncovered_retailers['LON'] = target_uncovered_retailers['LON'].astype(float)
target_uncovered_retailers.drop(columns='Lat/Lon',inplace=True)

# Filter unique neighborhood names for dropdown
unique_neighborhoods = target_uncovered_retailers['villages/ngbrhd'].drop_duplicates().sort_values()

# Get unique 'Sub Type' values
sub_type_options = target_uncovered_retailers['Sub Type'].unique()

# Create a sidebar
with st.sidebar:
    st.header("Filters")

    # Step 1: User selects a district
    district = st.selectbox("Select a District:", target_uncovered_retailers["District"].unique())

    # Step 2: Filter sub-districts based on district selection
    sub_district_options = target_uncovered_retailers[target_uncovered_retailers["District"] == district]["Sub-District"].unique()
    sub_district = st.selectbox("Select a Sub-District:", sub_district_options)

    # Step 3: Filter cities/villages based on sub-district selection
    city_options = target_uncovered_retailers[(target_uncovered_retailers["District"] == district) & (target_uncovered_retailers["Sub-District"] == sub_district)]["City/Towns"].unique()
    city = st.selectbox("Select a City/Town:", city_options)

    # Step 4: Filter neighborhoods based on city/village selection
    neighborhood_options = target_uncovered_retailers[
        (target_uncovered_retailers["District"] == district) & 
        (target_uncovered_retailers["Sub-District"] == sub_district) & 
        (target_uncovered_retailers["City/Towns"] == city)
    ]["villages/ngbrhd"].unique()
    selected_neighborhood = st.selectbox("Select a Neighborhood/Village:", neighborhood_options)




    # Add a selectbox
    # Add a selectbox for searching neighborhoods with no default value
    #selected_neighborhood = st.selectbox(
    #    "Search by Bangalore Neighborhood:",
    #    options=["Select a Neighborhood"] + unique_neighborhoods.tolist(),
    #    help="Choose a neighborhood from the dropdown"
    #)

    # Add multiselect for filtering
    selected_sub_types = st.multiselect(
        "Select categories to filter records:",
        options=sub_type_options,
        default=sub_type_options,  # Default to all options
        help="Choose one or more category type"
    )


    # checkbox for showing site details
    show_site_details = st.toggle("Show Site Details")

    # Checkbox for showing the map view
    show_map = st.toggle("Show Map View")

    # checkbox for potential order
    show_potential_order = st.toggle("Show Potential Order/Revenue Conversion")

# Filter the DataFrame based on sub-type selection
if selected_sub_types:
    target_uncovered_retailers = target_uncovered_retailers[target_uncovered_retailers['Sub Type'].isin(selected_sub_types)]
else:
    target_uncovered_retailers = target_uncovered_retailers  # Show the full DataFrame if no selection is made


if selected_neighborhood == "Select a Neighborhood":
    # Show total stats when no neighborhood is selected
    total_neighborhoods = unique_neighborhoods.nunique()
    total_records = len(target_uncovered_retailers)
    st.write(f"**Total unique neighborhoods:** {total_neighborhoods}")
    st.write(f"**Total records in the dataset:** {total_records}")
    st.dataframe(target_uncovered_retailers)
    if show_map:
            st.write("Map View of Uncovered Retailers:")
            st.map(target_uncovered_retailers[['LAT', 'LON']])
else:
    # Filter DataFrame based on the selected neighborhood
    filtered_df = target_uncovered_retailers[
        target_uncovered_retailers['villages/ngbrhd'] == selected_neighborhood
    ].reset_index(drop=True)

    # Identify constant columns
    constant_columns = [
        col for col in filtered_df.columns 
        if filtered_df[col].nunique() == 1
    ]

    # Create a summary row for constant columns
    summary = {col: filtered_df[col].iloc[0] for col in constant_columns}
    summary_df = pd.DataFrame([summary])

    # Exclude constant columns from the displayed DataFrame
    filtered_display_df = filtered_df.drop(columns=constant_columns)

    if not filtered_df.empty:
        # Display summary row
        st.write(f"Summary for **{selected_neighborhood}**:")
        st.dataframe(summary_df)
        # Display the filtered DataFrame
        st.write(f"Displaying **{len(filtered_display_df)}** uncovered retailers in **{selected_neighborhood}**:")
        st.dataframe(filtered_display_df)

        #show map
        #if show_map:
            #st.write("Map View of Uncovered Retailers:")
            #st.map(filtered_df[['LAT', 'LON']])
        
        show_sites = site_details[
             site_details['Bangalore_city_ngbrhd'] == selected_neighborhood
             ].reset_index(drop=True)
        
        #show site details
        if show_site_details: 
             st.write(f"Displaying **{len(show_sites)}** Site details of **{selected_neighborhood}**")
             st.dataframe(show_sites)
             

        #show interactive map of both retailers and sites
        if show_map:
             # Create a map
             st.write("Map View of Uncovered Retailers and Site Details")

             # Create options for the user
             view_option = st.radio(
                "Select map view:",
                ("Uncovered Retailers", "Sites", "Both"),
                index=2
            )

             m = folium.Map(location=[12.9716, 77.5946], zoom_start=12)

             # Add markers based on user selection
             if view_option == "Uncovered Retailers" or view_option == "Both":
             
             # Add markers for uncovered retailers
                for _, row in filtered_df.iterrows():
                # Format the popup text to include both Retailer Name and Estimated Monthly Revenue
                    popup_text = f"""
                    <b>Retailer Name:</b> {row['Retailer_name']}<br>
                    <b>Estimated Monthly Revenue:</b> ₹{row['Estmtd _Mnthly_Revn']:,}  <!-- Format revenue with commas -->
                    """
                    folium.Marker(
                        location=[row["LAT"], row["LON"]],
                        #popup=row[["Retailer_name","Estmtd_Mnthly_Revn"]],
                        popup=folium.Popup(popup_text, max_width=300),
                        icon=folium.Icon(color="red",icon="shopping-cart",icon_size=(25, 25))
                    ).add_to(m)

             if view_option == "Sites" or view_option == "Both":

             # Add markers for shops
                for _, row in show_sites.iterrows():
                # Format the popup text to include both Retailer Name and Estimated Monthly Revenue
                    popup_text = f"""
                    <b>Property Name:</b> {row['Property_name']}<br>
                    <b>No. of Apartments:</b> {row['No_of_apartments']}<br>  <!-- Format revenue with commas -->
                    <b>Min. cost of each apartment:</b> ₹{row['Min_cost_per_apartment']}
                    """
                    folium.Marker(
                        location=[row["Lat"], row["Long"]],
                        #popup=row[["Property_name","No_of_apartments"]],
                        popup=folium.Popup(popup_text, max_width=300),
                        icon=folium.Icon(color="green", icon="home",icon_size=(25, 25))
                    ).add_to(m)

             # Display in Streamlit
             st_data = st_folium(m, width=700, height=500)
        
        if show_potential_order:
             st.write("**Calculate Potential Order Generation**")
             # Add a slider to allow the user to select a value between 0 and 0.99
             conversion_rate = st.slider(
                label="Select Conversion Rate",  # Label for the slider
                min_value=0.0,                  # Minimum value
                max_value=1.0,                 # Maximum value
                value=0.05,                     # Default value
                step=0.05                       # Step size
                )
             competition_adjustment_factor = st.slider(
                label = "Select competion adjustment conversion factor",
                min_value=0.0,                  #0.2 -> 80% lost to competition
                max_value=1.0,
                value=1.0,
                step=0.05,
                help='Percentage of conversion from competition'
                )
             
             avg_new = average_order_df[average_order_df['villages/ngbrhd'] == selected_neighborhood].reset_index(drop=True)
             #st.dataframe(average_order_df)
             st.dataframe(avg_new)
             
             
             avg_order = average_order_df[average_order_df['villages/ngbrhd'] == selected_neighborhood]['Average Order nos'].values[0]
             total_retailers = filtered_df[filtered_df['villages/ngbrhd'] == selected_neighborhood].shape[0]
        
        
             # Calculate number of converted retailers
             converted_retailers = int(total_retailers * conversion_rate)
        
             # Calculate potential revenue
             potential_order = converted_retailers * avg_order
             potential_order = float(potential_order) 
        
             # Calculate competition-adjusted revenue
             comp_adjusted_order = potential_order * competition_adjustment_factor
        
             # Append results
             results = {
                'Region': selected_neighborhood,
                'Total Uncovered Retailers' : total_retailers,
                'Conversion_Rate': conversion_rate,
                'Converted_Retailers': converted_retailers,
                'Potential_Order': potential_order,
                'Competition_Adjusted_Order': comp_adjusted_order
            }

             # Create a DataFrame with the results
             potential_df = pd.DataFrame([results])
             st.dataframe(potential_df)

             # Calculate adjustment
             potential_df['Adjustment'] = potential_df['Potential_Order'] - potential_df['Competition_Adjusted_Order']

             # Waterfall chart
             fig = go.Figure()
             # Filter the data for the single region
             region_data = potential_df.iloc[0]


             fig.add_trace(go.Waterfall(
                name=region_data['Region'],
                orientation='v',
                measure=['relative', 'relative', 'total'],
                x=['Potential Order', 'Adjustment', 'Competition Adjusted Order'],
                y=[region_data['Potential_Order'], -region_data['Adjustment'], region_data['Competition_Adjusted_Order']],
                connector={"line": {"color": "rgba(63, 63, 63, 0.5)"}},
                text=[f"{region_data['Potential_Order']:,.2f}", f"-{region_data['Adjustment']:,.2f}", f"{region_data['Competition_Adjusted_Order']:,.2f}"],
                textposition="outside",
                ))

             # Layout
             fig.update_layout(
             title=f"Waterfall Chart for {region_data['Region']}",
             waterfallgap=0.5,
             yaxis_title="Order Quantity",
             xaxis_title="Stages",
                )

             #fig.show()
            
             #st.write("This chart shows the potential and adjusted orders for the selected region"),

             st.plotly_chart(fig)






# Main content area
#st.write("You selected:", selected_neighborhood)
#st.write("Slider value:", selected_sub_types)