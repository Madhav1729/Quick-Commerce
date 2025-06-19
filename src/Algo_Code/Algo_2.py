import pandas as pd
import numpy as np
import sys
import os
from math import sqrt, radians, sin, cos, atan2
from dataclasses import dataclass

path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data_Generation_Code'))
sys.path.append(path)
from models import AvailableDriver,Store

RADIUS_OF_EARTH = 6371  # Radius of the Earth in kilometers

class KDTreeNode:
    def __init__(self, point, driver_id, left=None, right=None):
        self.point = point  # A tuple representing (latitude, longitude)
        self.id = driver_id
        self.left = left
        self.right = right

class Rect:
    def __init__(self, min_point, max_point):
        self.min_point = min_point  # (min_latitude, min_longitude)
        self.max_point = max_point  # (max_latitude, max_longitude)

    def trim_left(self, cd, point):
        """Trim the left side of the bounding box based on the current dimension (cd) and point."""
        if cd == 0:  # Latitude
            return Rect(self.min_point, (point[0], self.max_point[1]))
        else:  # Longitude
            return Rect((self.min_point[0], self.min_point[1]), (self.max_point[0], point[1]))

    def trim_right(self, cd, point):
        """Trim the right side of the bounding box based on the current dimension (cd) and point."""
        if cd == 0:  # Latitude
            return Rect((point[0], self.min_point[1]), self.max_point)
        else:  # Longitude
            return Rect((self.min_point[0], point[1]), (self.max_point[0], self.max_point[1]))

class KDTree:
    def __init__(self, points_with_ids):
        """Initialize the KD-Tree with a list of points and driver IDs."""
        if not points_with_ids:
            self.root = None  # No data to build the tree
        else:
            self.root = self.build_tree(points_with_ids)

    def build_tree(self, points_with_ids_and_orders, depth=0):
        """Recursively build the KD-Tree from a list of points with driver IDs and orders count."""
        if not points_with_ids_and_orders:
            return None
        
        # Alternate between splitting on latitude and longitude
        k = len(points_with_ids_and_orders[0][0])  # k=2 for (latitude, longitude)
        axis = depth % k
        
        # Sort points and choose median as pivot
        points_with_ids_and_orders.sort(key=lambda x: x[0][axis])  # Sort by the axis (latitude or longitude)
        median_index = len(points_with_ids_and_orders) // 2
        
        # Create node and construct subtrees
        return KDTreeNode(
            point=points_with_ids_and_orders[median_index][0],
            driver_id=points_with_ids_and_orders[median_index][1],
            left=self.build_tree(points_with_ids_and_orders[:median_index], depth + 1),
            right=self.build_tree(points_with_ids_and_orders[median_index + 1:], depth + 1)
        )

    def distance(self, point1, point2):
        """Calculate the great-circle distance between two points on the Earth."""
        lat1, lon1 = map(radians, point1)
        lat2, lon2 = map(radians, point2)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return RADIUS_OF_EARTH * c

    def point_to_rect_distance(self, point, rect):
        """Calculate the minimum distance from a point to the bounding box defined by the rectangle."""
        lat, lon = point
        min_lat, min_lon = rect.min_point
        max_lat, max_lon = rect.max_point

        # Compute the closest point on the rectangle to the point
        closest_lat = max(min_lat, min(lat, max_lat))
        closest_lon = max(min_lon, min(lon, max_lon))

        # Calculate the distance from the point to this closest point
        return sqrt((lat - closest_lat) ** 2 + (lon - closest_lon) ** 2)

    def nearest_neighbor_drivers(self, Q, T, cd, best, best_dist, BB,operator_id):
        """Find the nearest neighbor to the query point Q in the KD-Tree T."""
        if T is None or self.point_to_rect_distance(Q, BB) > best_dist:
            return best, best_dist  # Return the current best if bounding box is too far

        # Calculate the distance from Q to the current node's point
        dist = self.distance(Q, T.point)
        
        # Update best point and distance if a better point is found
        if dist < best_dist and available_drivers[T.id - 1].is_available and available_drivers[T.id - 1].operators_id == operator_id:
            best = T
            best_dist = dist

        # Determine the next dimension (cd) to explore
        next_cd = (cd + 1) % len(Q)

        # Visit the subtrees in the most promising order
        if Q[cd] < T.point[cd]:
            # Explore left subtree first
            best, best_dist = self.nearest_neighbor_drivers(Q, T.left, next_cd, best, best_dist, BB.trim_left(cd, T.point),operator_id)
            best, best_dist = self.nearest_neighbor_drivers(Q, T.right, next_cd, best, best_dist, BB.trim_right(cd, T.point),operator_id)
        else:
            # Explore right subtree first
            best, best_dist = self.nearest_neighbor_drivers(Q, T.right, next_cd, best, best_dist, BB.trim_right(cd, T.point),operator_id)
            best, best_dist = self.nearest_neighbor_drivers(Q, T.left, next_cd, best, best_dist, BB.trim_left(cd, T.point),operator_id)

        return best, best_dist

    def nearest_neighbor_stores(self, Q, T, cd, best, best_dist, BB,operator_id):
        """Find the nearest neighbor to the query point Q in the KD-Tree T."""
        if T is None or self.point_to_rect_distance(Q, BB) > best_dist:
            return best, best_dist  # Return the current best if bounding box is too far

        # Calculate the distance from Q to the current node's point
        dist = self.distance(Q, T.point)
        
        # Update best point and distance if a better point is found
        if dist < best_dist and stores[T.id - 1].operator_id == operator_id:
            best = T
            best_dist = dist

        # Determine the next dimension (cd) to explore
        next_cd = (cd + 1) % len(Q)

        # Visit the subtrees in the most promising order
        if Q[cd] < T.point[cd]:
            # Explore left subtree first
            best, best_dist = self.nearest_neighbor_stores(Q, T.left, next_cd, best, best_dist, BB.trim_left(cd, T.point),operator_id)
            best, best_dist = self.nearest_neighbor_stores(Q, T.right, next_cd, best, best_dist, BB.trim_right(cd, T.point),operator_id)
        else:
            # Explore right subtree first
            best, best_dist = self.nearest_neighbor_stores(Q, T.right, next_cd, best, best_dist, BB.trim_right(cd, T.point),operator_id)
            best, best_dist = self.nearest_neighbor_stores(Q, T.left, next_cd, best, best_dist, BB.trim_left(cd, T.point),operator_id)

        return best, best_dist

# Loop through each instance
for instance in range(1, 4):
    try:
        available_drivers = []
        stores=[]
        available_drivers_df = pd.read_csv(f"quick_commerce/Data/Generated_datasets_and_input_instance/Instance_{instance}/Generated_data/available_drivers.csv")
        stores_df = pd.read_csv(f"quick_commerce/Data/Generated_datasets_and_input_instance/Instance_{instance}/Generated_data/stores.csv")
        for index, row in available_drivers_df.iterrows():
            available_drivers.append(
                AvailableDriver(
                    row["driver_id"],
                    row["name"],
                    row["latitude"],
                    row["longitude"],
                    row["city_id"],
                    row["vehicle_id"],
                    row["operators_id"],
                    row["is_available"],
                    row["max_delivery_radius"],
                    row["pending_orders_count"],
                    row["availability_time"]
                )
            )
        requests = pd.read_csv(f"quick_commerce/Data/Generated_datasets_and_input_instance/Instance_{instance}/Generated_data/requests.csv")
      
        for index,row in stores_df.iterrows():
            stores.append(
                Store(
                    row["store_id"],
                    row["operator_id"],
                    row["city_id"],
                    row["location_latitude"],
                    row["location_longitude"],
                    row["contact_email"],
                    row["contact_mobile"],
                    row["start_time"],
                    row["end_time"],
                    row["inventory_capacity"]
                )
            )
    except FileNotFoundError as e:
        print(f"Error: {e}")
        continue  # Skip to the next instance if there's an error

    # Check if necessary columns exist in both CSVs
    required_columns_drivers = ['city_id', 'latitude', 'longitude', 'driver_id']
    required_columns_requests = ['Delivery_latitude', 'Delivery_longitude', 'Delivery_city_id', 'Request_id']

    if not all(column in available_drivers_df.columns for column in required_columns_drivers):
        print(f"Error: Required columns {required_columns_drivers} not found in available_drivers.csv for instance {instance}")
        continue

    if not all(column in requests.columns for column in required_columns_requests):
        print(f"Error: Required columns {required_columns_requests} not found in requests.csv for instance {instance}")
        continue

    # Create a dictionary of KD-Trees for each city
    city_kd_trees = {}
    stores_kd_trees = {}

    for city_id, group in available_drivers_df.groupby('city_id'):
        driver_locations_with_ids = [(tuple([row['latitude'], row['longitude']]), row['driver_id']) for _, row in group.iterrows() if row['is_available']]
        if driver_locations_with_ids:
            city_kd_trees[city_id] = KDTree(driver_locations_with_ids)

    assignments = []
    
    for city_id, group in stores_df.groupby('city_id'):
        store_locations_with_ids = [(tuple([row['location_latitude'], row['location_longitude']]), row['store_id']) for _, row in group.iterrows() ]
        if store_locations_with_ids:
            stores_kd_trees[city_id] = KDTree(store_locations_with_ids)

    # Iterate through each request
    for _, request in requests.iterrows():
        request_location = (request['Delivery_latitude'], request['Delivery_longitude'])
        city_id = request['Delivery_city_id']

        # Find the KD-Tree for the request's city
        kd_tree_for_stores = stores_kd_trees.get(city_id)
        
        if kd_tree_for_stores is None or kd_tree_for_stores.root is None:
            print(f"No stores available in city with id {city_id} for instance {instance}")
            continue  # No drivers available in this city

        # Initialize bounding box for nearest neighbor search
        bounding_box_for_request = Rect((request['Delivery_latitude'] - 0.1, request['Delivery_longitude'] - 0.1),
                            (request['Delivery_latitude'] + 0.1, request['Delivery_longitude'] + 0.1))
        # Find the nearest driver
        best_store_node, best_distance_to_store = kd_tree_for_stores.nearest_neighbor_stores(request_location, kd_tree_for_stores.root, 0, None, float('inf'), bounding_box_for_request,operator_id=request['operators_id'])
        
        if best_store_node:
            best_store=stores[best_store_node.id - 1]
        
        kd_tree_for_driver = city_kd_trees.get(city_id)
        #bounding box for driver
        bounding_box_for_driver = Rect((best_store.location_latitude - 0.1, best_store.location_longitude - 0.1),
                            (best_store.location_latitude + 0.1, best_store.location_longitude + 0.1))
        best_driver_node, best_distance_to_driver = kd_tree_for_driver.nearest_neighbor_drivers((best_store.location_latitude, best_store.location_longitude), kd_tree_for_driver.root, 0, None, float('inf'), bounding_box_for_driver,operator_id=request['operators_id'])
        
        
        if kd_tree_for_driver is None or kd_tree_for_driver.root is None:
            print(f"No drivers available in city with id {city_id} for instance {instance}")
            continue  # No drivers available in this city
        
        if best_driver_node:
            best_driver = available_drivers[best_driver_node.id - 1]
            # Assign driver to the request and mark as unavailable
            best_driver.is_available = False
            assignments.append({
                "Request_id": request['Request_id'],
                "Assigned_store_id": best_store.store_id,
                "Assigned_store_latitude": best_store.location_latitude,
                "Assigned_store_longitude": best_store.location_longitude,
                "Assigned_driver_id": best_driver.driver_id,
                "Assigned_Driver_latitude": best_driver.latitude,
                "Assigned_Driver_longitude": best_driver.longitude,
                "Request_latitude": request['Delivery_latitude'],
                "Request_longitude": request['Delivery_longitude'],
                "Distance_to_store": best_distance_to_store,
                "Distance_to_driver": best_distance_to_driver,
                "Total_Distance": best_distance_to_store+best_distance_to_driver
            })

    # Save assignments to a CSV file
    if not os.path.exists(f"quick_commerce/Algo_Output/Algo_2/Instance_{instance}"):
        os.makedirs(f"quick_commerce/Algo_Output/Algo_2/Instance_{instance}")
    
    assignments_df = pd.DataFrame(assignments)
    assignments_df.sort_values(by="Total_Distance",inplace=True)
    assignments_df.to_csv(f"quick_commerce/Algo_Output/Algo_2/Instance_{instance}/assignments.csv", index=False)

    print(f"Assignments for Instance {instance} saved to assignments.csv")