import pandas as pd
import folium

data = pd.read_csv('../datasets/Generated_datasets/stores.csv')

latitude, longitude = data['location_latitude'].mean(), data['location_longitude'].mean()
map_osm = folium.Map(location=[latitude, longitude], zoom_start=13)

def get_color(capacity):
    if capacity > 4000:
        return 'darkred'
    elif 3000 < capacity <= 4000:
        return 'red'
    elif 2000 < capacity <= 3000:
        return 'orange'
    else:
        return 'green'

for index, row in data.iterrows():
    popup_text = f"""
    <b>Store ID:</b> {row['store_id']}<br>
    <b>Email:</b> {row['contact_email']}<br>
    <b>Mobile:</b> {row['contact_mobile']}<br>
    <b>Inventory Capacity:</b> {row['inventory_capacity']}<br>
    <b>Start Time:</b> {row['start_time']}<br>
    <b>End Time:</b> {row['end_time']}
    """
    
    folium.CircleMarker(
        location=[row['location_latitude'], row['location_longitude']],
        radius=10,
        color=get_color(row['inventory_capacity']),
        fill=True,
        fill_color=get_color(row['inventory_capacity']),
        fill_opacity=0.7,
        popup=popup_text,
        tooltip=f"Store {row['store_id']} ({row['contact_email']})"
    ).add_to(map_osm)

map_osm.save("store_locations_map.html")
print("Map has been saved as store_locations_map.html")
