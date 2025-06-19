import csv
import pandas as pd
import sys
import math
from dataclasses import dataclass
from functools import lru_cache
from scipy.spatial import KDTree

@dataclass
class Assignment:
    Assigned_driver_id: str
    Request_id: str
    store_id: int
    Assigned_Driver_latitude: float
    Assigned_Driver_longitude: float
    Request_latitude: float
    Request_longitude: float
    store_latitude: float
    store_longitude: float
    Distance: float

# Haversine formula remains the same
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Load CSV data into dictionaries for fast access
def load_csv(file_path, key_column):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        return {row[key_column]: row for row in reader}

drivers = load_csv('quick_commerce/Data/Generated_datasets_and_input_instance/Instance_1/Generated_data/available_drivers.csv', 'driver_id')
requests = load_csv('quick_commerce/Data/Generated_datasets_and_input_instance/Instance_1/Generated_data/requests.csv', 'Request_id')
stores = load_csv('quick_commerce/Data/Generated_datasets_and_input_instance/Instance_1/Generated_data/stores.csv', 'store_id')

# Prepare KD trees for fast nearest-neighbor lookup
def build_kd_tree(data, lat_key, lon_key):
    points = [(float(item[lat_key]), float(item[lon_key])) for item in data.values()]
    return KDTree(points), points

driver_kd_tree, driver_coords = build_kd_tree(drivers, 'latitude', 'longitude')
store_kd_tree, store_coords = build_kd_tree(stores, 'location_latitude', 'location_longitude')

# Memoize distance calculations to avoid redundant work
@lru_cache(maxsize=None)
def cached_haversine(lat1, lon1, lat2, lon2):
    return haversine(lat1, lon1, lat2, lon2)

# Find 30 nearest drivers and stores using KD Tree
def find_best_driver_store(request):
    delivery_lat = float(request['Delivery_latitude'])
    delivery_lon = float(request['Delivery_longitude'])

    best_driver = None
    best_store = None
    best_dist = sys.maxsize

    # Find 30 nearest drivers
    _, nearest_driver_indices = driver_kd_tree.query((delivery_lat, delivery_lon), k=30)
    nearest_drivers = [list(drivers.values())[i] for i in nearest_driver_indices]

    # Find 30 nearest stores
    _, nearest_store_indices = store_kd_tree.query((delivery_lat, delivery_lon), k=30)
    nearest_stores = [list(stores.values())[i] for i in nearest_store_indices]

    # Iterate over nearest drivers
    for driver in nearest_drivers:
        # if driver['is_available'] == 'False':
        #     continue
        
        driver_lat = float(driver['latitude'])
        driver_lon = float(driver['longitude'])

        # Iterate over nearest stores for each driver
        for store in nearest_stores:
            store_lat = float(store['location_latitude'])
            store_lon = float(store['location_longitude'])

            # Calculate total distance (driver -> store -> delivery location)
            distance_driver_to_store = cached_haversine(driver_lat, driver_lon, store_lat, store_lon)
            distance_store_to_request = cached_haversine(store_lat, store_lon, delivery_lat, delivery_lon)
            total_distance = distance_driver_to_store + distance_store_to_request

            # Update if we find a better (shorter) total path
            if total_distance < best_dist:
                best_dist = total_distance
                best_driver = driver
                best_store = store

    return best_driver, best_store, best_dist

# Process each request
def process_request(request):
    best_driver, best_store, total_distance = find_best_driver_store(request)

    if best_driver and best_store:
        assignment = Assignment(
            Assigned_driver_id=best_driver['driver_id'],
            Request_id=request['Request_id'],
            store_id=best_store['store_id'],
            Assigned_Driver_latitude=float(best_driver['latitude']),
            Assigned_Driver_longitude=float(best_driver['longitude']),
            Request_latitude=float(request['Delivery_latitude']),
            Request_longitude=float(request['Delivery_longitude']),
            store_latitude=float(best_store['location_latitude']),
            store_longitude=float(best_store['location_longitude']),
            Distance=total_distance
        )
        return assignment

# Prepare for writing to CSV
output_file = 'assignments3.csv'

# Process all requests and write results in batch
assignments = []
count = 1
for request in requests.values():
    assignment = process_request(request)
    if assignment:
        assignments.append(assignment)
        print(count)
        count += 1

# Batch write to CSV after processing all requests
# with open(output_file, mode='w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(['Assigned_driver_id', 'Request_id', 'store_id', 'Assigned_Driver_latitude', 'Assigned_Driver_longitude',
#                      'Request_latitude', 'Request_longitude', 'store_latitude', 'store_longitude', 'Distance'])
#     for assignment in assignments:
#         writer.writerow([
#             assignment.Assigned_driver_id,
#             assignment.Request_id,
#             assignment.store_id,
#             assignment.Assigned_Driver_latitude,
#             assignment.Assigned_Driver_longitude,
#             assignment.Request_latitude,
#             assignment.Request_longitude,
#             assignment.store_latitude,
#             assignment.store_longitude,
#             assignment.Distance
#         ])

# print(f"Assignments appended to {output_file}.")

instance = 1

assignments_df = pd.DataFrame(assignments)
assignments_df.to_csv(f"quick_commerce/Algo_Output/Algo_3/Instance_{instance}/assignments_total_path_optimized.csv", index=False)

print(f"Assignments for Instance {instance} saved to assignments.csv")