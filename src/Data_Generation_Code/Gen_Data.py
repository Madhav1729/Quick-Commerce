import random
import pandas as pd
from geopy.distance import geodesic
from geopy.point import Point
from models import * # Assuming models contain all necessary classes
from datetime import datetime, timedelta
import os

#Paths to config files
PATHS_TO_CONFIGS = []

i = 1
while True:
    path = f"quick_commerce/Data/Generated_datasets_and_input_instance/Instance_{i}/Config.txt"
    try:
        with open(path, 'r') as file:
            PATHS_TO_CONFIGS.append(path)
    except FileNotFoundError:
        break
    i += 1

# Load config data from config files
config_data = []
for path in PATHS_TO_CONFIGS:
    with open(path, 'r') as file:
        config_data.append(file.readlines())



# Load city data from CSV
cities_df = pd.read_csv("quick_commerce/Data/Raw_data/indian-cities.csv")
def generate_data(data):
        """Generate data for the Quick Commerce system."""
        # Constants
        NUM_CITIES = int(data[0].strip())
        NUM_OPERATORS = int(data[1].strip())
        NUM_STORES_PER_OPERATOR = int(data[2].strip())
        NUM_CUSTOMERS = int(data[3].strip())
        NUM_VEHICLES = int(data[4].strip())
        NUM_VEHICLE_TYPES = int(data[5].strip())
        NUM_ITEM_TYPES_FOR_INVENTORY = int(data[6].strip())
        NUM_SHIPMENT_REQUESTS = int(data[7].strip())
        NUM_VEHICLE_OPERATOS = int(data[8].strip())
        NUM_VEHICLE_OWNERS = int(data[9].strip())
        

        print(f"Generating data for Instance {Index_Of_Config} with the following parameters:")
        print(f"NUM_CITIES: {NUM_CITIES}")
        print(f"NUM_OPERATORS: {NUM_OPERATORS}")
        print(f"NUM_STORES_PER_OPERATOR: {NUM_STORES_PER_OPERATOR}")
        print(f"NUM_CUSTOMERS: {NUM_CUSTOMERS}")
        print(f"NUM_VEHICLES: {NUM_VEHICLES}")
        print(f"NUM_VEHICLE_TYPES: {NUM_VEHICLE_TYPES}")
        print(f"NUM_ITEM_TYPES_FOR_INVENTORY: {NUM_ITEM_TYPES_FOR_INVENTORY}")
        print(f"NUM_SHIPMENT_REQUESTS: {NUM_SHIPMENT_REQUESTS}")
        print(f"NUM_VEHICLE_OPERATOS: {NUM_VEHICLE_OPERATOS}")
        print(f"NUM_VEHICLE_OWNERS: {NUM_VEHICLE_OWNERS}")



        # Lists to hold generated data
        city_list = []
        def generate_cities():
            """Generate city data based on input CSV and store in city_list."""
            for i in range(NUM_CITIES):
                city = City(
                    city_id=i + 1,
                    name=cities_df.iloc[i]['City'],
                    center_latitude=cities_df.iloc[i]['Lat'],
                    center_longitude=cities_df.iloc[i]['Long'],
                    radius=random.uniform(10, 30),  # Random radius between 10 and 30 km
                    district=cities_df.iloc[i]['City'],
                    state=cities_df.iloc[i]['State'],
                    country=cities_df.iloc[i]['country'],
                    population=random.randint(1_000_000, 15_000_000),  # Random population between 1M and 15M
                    list_of_operators=[]
                )
                city_list.append(city)

        generate_cities()  # Populate city_list
        city_df = pd.DataFrame([vars(city) for city in city_list])  # Create DataFrame from city_list


        def generate_random_points(center_point, radius, num_points):
            """Generate random geographic points within a specified radius of a center point."""
            points = []
            for _ in range(num_points):
                distance = random.uniform(0, radius)
                angle = random.uniform(0, 360)
                destination = geodesic(kilometers=distance).destination(center_point, angle)
                points.append((destination.latitude, destination.longitude))
            return points

        def generate_operators():
            """Generate operator data with random attributes."""
            operators = []

            for i in range(NUM_OPERATORS):
                operator = Operator(
                    operator_id=i + 1,
                    name=f"Operator_{i + 1}",
                    contact_email=f"help@operator{i + 1}.com",
                    contact_phone=f"+91-{random.randint(9000000000, 9999999999)}",
                    contact_person_name=f"Person_{i + 1}",
                    registered_name=f"Registered_Operator_{i + 1}",
                    registered_address=f"Address_{i + 1}",
                    operates_in=random.sample(range(1, NUM_CITIES + 1),10),
                    start_time=datetime.combine(datetime.today(), datetime.strptime("09:00", "%H:%M").time()),
                    Max_number_of_orders_each_vehicle_can_take= 1,
                    end_time=datetime.combine(datetime.today(), datetime.strptime("21:00", "%H:%M").time()),
                    list_of_stores=[]
                )
                # Associate operator with the cities they operate in
                for j in operator.operates_in:
                    city_list[j - 1].list_of_operators.append(operator.operator_id)
                operators.append(operator)
            return operators

        operators = generate_operators()  # Populate operators list

        def generate_stores():
            """Generate store data for each operator in their respective cities."""
            stores = []
            store_id = 1  # Track the store_id across all operators and cities
            
            for i in range(NUM_OPERATORS):  # Loop through each operator
                for city_id in operators[i].operates_in:  # Loop through each city the operator operates in
                    store_points = generate_random_points(
                        Point(city_list[city_id - 1].center_latitude, city_list[city_id - 1].center_longitude),
                        radius=city_list[city_id - 1].radius, 
                        num_points=NUM_STORES_PER_OPERATOR
                    )
                    
                    for k in range(NUM_STORES_PER_OPERATOR):  # Create stores for this operator in this city
                        store = Store(
                            store_id=store_id,
                            operator_id=i + 1,
                            city_id=city_id,
                            location_latitude=store_points[k][0],
                            location_longitude=store_points[k][1],
                            contact_email=f"store{store_id}@{city_list[city_id - 1].name.lower()}.com",
                            contact_mobile=random.randint(9000000000, 9999999999),
                            start_time=datetime.combine(datetime.today(), datetime.strptime("09:00", "%H:%M").time()),
                            end_time=datetime.combine(datetime.today(), datetime.strptime("21:00", "%H:%M").time()),
                            inventory_capacity=random.randint(1000, 5000)
                        )
                        
                        # Add store_id to the operator's list_of_stores and increment store_id
                        operators[i].list_of_stores.append(store_id)
                        stores.append(store)
                        store_id += 1  # Increment the store ID to avoid duplicates
            
            return stores

        stores = generate_stores()  # Populate stores list

        def generate_customers():
            """Generate customer data with random locations within city boundaries."""
            customers = []
            for i in range(1, NUM_CUSTOMERS + 1):
                city_id = random.choice(range(1, NUM_CITIES + 1))
                while(city_list[city_id-1].list_of_operators == []):
                    city_id = random.choice(range(1, NUM_CITIES + 1))
                city = city_list[city_id - 1]
                distance = random.uniform(0, city.radius)
                angle = random.uniform(0, 360)
                destination = geodesic(kilometers=distance).destination(Point(city.center_latitude, city.center_longitude), angle)
                customer = Customer(
                    customer_id=i,
                    city_id=city_id,
                    location_latitude=destination.latitude,
                    location_longitude=destination.longitude,
                    address=f"Address_{i}",
                    preferred_delivery_window=(f"{random.randint(1, 12)} AM", f"{random.randint(1, 12)} PM")
                )
                customers.append(customer)
            return customers

        customers = generate_customers()  # Populate customers list

        def generate_vehicles():
            """Generate vehicle data with random attributes."""
            vehicles = []
            for i in range(1, NUM_VEHICLES + 1):
                vehicle = Vehicle(
                    vehicle_id=i,
                    vehicle_type_id=random.choice(range(1, NUM_VEHICLE_TYPES + 1)),
                    owner=f"Owner_{i}",
                    driver=f"Driver_{i}",
                    vehicle_operator=random.choice(range(1, NUM_OPERATORS + 1)),
                    fuel_type=random.choice(["Petrol", "Diesel", "Electric"]),
                    vehicle_status=random.choice(["Available", "In Use", "Under Maintenance"]),
                    number_plate=f"AB-{random.randint(10, 99)}-AB-{random.randint(1000, 9999)}"
                )
                vehicles.append(vehicle)
            return vehicles

        vehicles = generate_vehicles()  # Populate vehicles list

        def generate_vehicle_types():
            """Generate vehicle type data with random attributes."""
            vehicle_type_names=["two wheeler","three wheeler closed","three wheeler open","four wheeler closed","four wheeler open"]
            vehicle_types = []
            for i in range(1, NUM_VEHICLE_TYPES+1 ):
                vehicle_type = VehicleType(
                    id=i,
                    name=vehicle_type_names[i-1],
                    weight_carrying_capacity=round(random.uniform(500, 2000), 2),
                    container_space_length=round(random.uniform(1, 10), 2),
                    container_space_breadth=round(random.uniform(1, 10), 2),
                    container_space_height=round(random.uniform(1, 10), 2)
                )
                vehicle_types.append(vehicle_type)
            return vehicle_types

        vehicle_types = generate_vehicle_types()  # Populate vehicle types list

        def generate_vehicle_operators():
            vehicle_operators = []
            for i in range(1,NUM_VEHICLE_OPERATOS+1):
                vehicle_operator = VehicleOperator(
                    vehicle_operator_id=i,
                    Name = f"vehicle_operator_{i}", 
                    PAN = f"ABCDE{random.randint(1000,9999)}F",
                    Aadhar = f"{random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)}",
                    City = city_list[random.randint(0,NUM_CITIES-1)].name,
                    Address = f"Address_{i}",
                    Rating = round(random.uniform(1,5),2)
                )
                vehicle_operators.append(vehicle_operator)
            return vehicle_operators
        
        vehicle_operators = generate_vehicle_operators() #Populate vehicle operators list

        def generate_vehicle_owners():
            vehicle_owners = []
            for i in range(1,NUM_VEHICLE_OWNERS+1):
                vehicle_owner = VehicleOwner(
                    vehicle_owner_Id = i,
                    Name = f"vehicle_owner_{i}",
                    PAN = f"ABCDE{random.randint(1000,9999)}F",
                    Aadhar = f"{random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)}",
                    City = city_list[random.randint(0,NUM_CITIES-1)].name,
                    Address = f"Address_{i}",
                    Rating = round(random.uniform(1,5),2)
                )
                vehicle_owners.append(vehicle_owner)
            return vehicle_owners

        vehicle_owners = generate_vehicle_owners() #Populate vehicle owners list

        def generate_drivers():
            """Generate driver data with random attributes."""
            drivers = []
            for city in city_list:
                for i in range(0,len(city.list_of_operators)):
                    for j in range(1, 100):
                        driver = Driver(
                            id=len(drivers) + 1,
                            name=f"Driver_{len(drivers) + 1}",
                            city=city.city_id,
                            pan=f"ABCDE{random.randint(1000, 9999)}F",
                            aadhar=f"{random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}",
                            dl_number=f"DL-{random.randint(1000, 9999)}-{random.randint(100000, 999999)}",
                            dl_for_vehicle_types=random.sample(range(1, NUM_VEHICLE_TYPES + 1), random.randint(1, 3)),
                            Available=random.choice([True, False]),
                        )
                        drivers.append(driver)

            return drivers

        drivers = generate_drivers()  # Populate drivers list

        def generate_item_type_for_inventory():
            """Generate inventory items with random attributes."""
            items = []
            for i in range(1, NUM_ITEM_TYPES_FOR_INVENTORY + 1):
                item = InventoryItem(
                    item_id=i,
                    name=f"Item_{i}",
                    item_type=random.choice(["Electronics", "Clothing", "Food", "Furniture", "Books"]),
                    weight=round(random.uniform(0.1, 10), 2),
                    dimensions=(round(random.uniform(0.1, 1), 2), round(random.uniform(0.1, 1), 2), round(random.uniform(0.1, 1), 2)),
                    special_handling_requirements=random.choice(["Fragile", "Perishable", "Hazardous", "None"])
                )
                items.append(item)
            return items

        item_type_for_inventory = generate_item_type_for_inventory()  # Populate inventory items list

        
            

        def generate_random_time(start_time, end_time):
            """Generate a random time between start_time and end_time."""
            time_delta = end_time - start_time
            random_seconds = random.randint(0, int(time_delta.total_seconds()))
            return start_time + timedelta(seconds=random_seconds)

        def generate_shipment_requests():
            """Generate shipment requests with random pickup and delivery times."""
            shipment_requests = []
            start_time = datetime.combine(datetime.today(), datetime.strptime("09:00", "%H:%M").time())
            end_time = datetime.combine(datetime.today(), datetime.strptime("21:00", "%H:%M").time())

            for i in range(NUM_SHIPMENT_REQUESTS):
                pickup_time = generate_random_time(start_time, end_time)
                delivery_time = generate_random_time(pickup_time, end_time)

                shipment = ShipmentRequest(
                    shipment_id=f"shipment_{i + 1}",
                    facility_id=random.choice(range(1, NUM_STORES_PER_OPERATOR + 1)),
                    customer_id=random.choice(range(1, NUM_CUSTOMERS + 1)),
                    vehicle_id=random.choice(range(1, NUM_VEHICLES + 1)),
                    pickup_time=pickup_time,
                    delivery_time=delivery_time,
                    items_shipped=random.sample(range(1, NUM_ITEM_TYPES_FOR_INVENTORY + 1), random.randint(1, 5)),
                    shipment_value=random.uniform(100, 1000),
                    payment_status=random.choice(["Paid", "Unpaid"])
                )
                shipment_requests.append(shipment)

            return shipment_requests

        # shipment_requests = generate_shipment_requests()  # Populate shipment requests list
        def inventory():
            inventory_details=[]
            start_inventory_id=1

            for i in range(len(stores)):
                store = stores[i]
                inventory = Inventory(
                    id = start_inventory_id,
                    List_of_items = [],
                    number_of_items_per_type = [],
                    operator_id=store.operator_id,
                    total_number_of_items=0,
                    city_id=store.city_id,
                    store_id = store.store_id
                )
                for item in item_type_for_inventory:
                    inventory.List_of_items.append(item.item_id)
                    inventory.number_of_items_per_type.append(random.randint(10, 100))
                    inventory.total_number_of_items+=inventory.number_of_items_per_type[-1]
                inventory_details.append(inventory)
                start_inventory_id+=1

            return inventory_details

        inventory_details = inventory()

        def generate_available_drivers(N=100):
            """Generate at least 30 available drivers for each city."""
            driver_id = 1
            vehicle_id = 1
            available_drivers = []
            
            for city in city_list:
                operators = city.list_of_operators
                if len(operators) == 0:
                    continue

                city_id = city.city_id
                center_latitude = city.center_latitude
                center_longitude = city.center_longitude

                # Generate at least 30 driver locations for each city
                driver_locations = generate_random_points(
                    Point(center_latitude, center_longitude),
                    radius=city.radius, 
                    num_points=max(N, 30)  # Ensure at least 30 drivers
                )
                
                # Ensure there are locations generated
                if not driver_locations:
                    continue
                
                for driver_location in driver_locations:
                    driver_latitude, driver_longitude = driver_location

                    available_driver = AvailableDriver(
                        driver_id=drivers[((driver_id - 1) + len(drivers)) % len(drivers)].id,  # Cycle through drivers
                        city_id=city_id,
                        vehicle_id=vehicles[(vehicle_id - 1) % len(vehicles)].vehicle_id,  # Cycle through vehicles
                        name=f"Driver_{driver_id}",
                        latitude=driver_latitude,
                        longitude=driver_longitude,
                        operators_id=random.choice(city.list_of_operators),
                        is_available=True,
                        availability_time=None,
                        max_delivery_radius=None,
                        pending_orders_count=None
                    )
                    
                    available_drivers.append(available_driver)
                    
                    driver_id += 1
                    vehicle_id += 1

                    # Optional: Reset driver_id and vehicle_id if they exceed limits
                    if driver_id > len(drivers):
                        driver_id = 1
                    if vehicle_id > len(vehicles):
                        vehicle_id = 1

            return available_drivers
        
        available_drivers = generate_available_drivers()
  # Populate available drivers list

        def generate_requests(N):
            requests = []
            request_id = 1
            customer_id = 1
            for city in city_list:
                operators = city.list_of_operators
                if(len(operators) == 0):
                    print(f"No operators in {city}")
                    continue

                center_latitude = city.center_latitude
                center_longitude = city.center_longitude

                number_of_requests_in_city = N
                delivery_location = generate_random_points(
                    Point(center_latitude, center_longitude),
                    radius=city.radius, 
                    num_points=number_of_requests_in_city
                )
                
                

                for i in range(1, number_of_requests_in_city + 1):
                    delivery_items = []
                    max_number_of_items = random.randint(1, len(item_type_for_inventory) + 1)
                    for _ in range(1,  max_number_of_items + 1):
                        item_id = random.choice(item_type_for_inventory).item_id
                        delivery_item = (item_id, random.randint(1, 20))
                        delivery_items.append(delivery_item)

                    # if(len(customers) <= customer_id):
                    #     print("create more customers")
                    #     break
                    
                    request = Request(
                        Request_id = request_id,
                        Customer_id = customers[customer_id - 1].customer_id, # assures there is an id, better than writing customer_id directly
                        operators_id= random.choice(city.list_of_operators),
                        Request_placing_time = datetime.combine(datetime.today(), datetime.strptime("09:00", "%H:%M").time()),
                        Delivery_latitude = delivery_location[i - 1][0],
                        Delivery_longitude = delivery_location[i- 1][1],
                        Delivery_city_id= city.city_id,
                        Delivery_address = f"Address_{request_id}",
                        items_in_this_request = delivery_items
                    )
                    request_id += 1
                    customer_id += 1
                    requests.append(request)

            return requests

        requests = generate_requests(30)

        # Save all generated data to respective CSV files
        operators_df = pd.DataFrame([vars(operator) for operator in operators])
        stores_df = pd.DataFrame([vars(store) for store in stores])
        drivers_df = pd.DataFrame([vars(driver) for driver in drivers])
        items_df = pd.DataFrame([vars(item) for item in item_type_for_inventory])
        customers_df = pd.DataFrame([vars(customer) for customer in customers])
        vehicles_df = pd.DataFrame([vars(vehicle) for vehicle in vehicles])
        vehicle_types_df = pd.DataFrame([vars(vehicle_type) for vehicle_type in vehicle_types])
        inventory_df = pd.DataFrame([vars(inventory) for inventory in inventory_details])
        # requests_df = pd.DataFrame([vars(request) for request in shipment_requests])
        available_drivers_df=pd.DataFrame([vars(driver) for driver in available_drivers])
        requests_df=pd.DataFrame([vars(request) for request in requests])
        vehiclle_operators_df=pd.DataFrame([vars(vehicle_operator) for vehicle_operator in vehicle_operators])
        vehicle_owners_df=pd.DataFrame([vars(vehicle_owner) for vehicle_owner in vehicle_owners])
        active_requests_df=pd.DataFrame()
        unserviced_requests_df=pd.DataFrame()
        completed_requests_df=pd.DataFrame()

        # Check if output directory exists
        output_directory = f"quick_commerce/Data/Generated_datasets_and_input_instance/Instance_{Index_Of_Config}/Generated_data"
        os.makedirs(output_directory, exist_ok=True)

        # Save data to CSV files
        try:
            city_df.to_csv(f"{output_directory}/cities.csv", index=False)
            operators_df.to_csv(f"{output_directory}/quick_commerce_operators.csv", index=False)
            stores_df.to_csv(f"{output_directory}/stores.csv", index=False)
            drivers_df.to_csv(f"{output_directory}/drivers.csv", index=False)
            items_df.to_csv(f"{output_directory}/item_type_for_inventory.csv", index=False)
            customers_df.to_csv(f"{output_directory}/customers.csv", index=False)
            vehicles_df.to_csv(f"{output_directory}/vehicles.csv", index=False)
            vehicle_types_df.to_csv(f"{output_directory}/vehicle_types.csv", index=False)
            # requests_df.to_csv(f"{output_directory}/shipment_requests.csv", index=False)
            requests_df.to_csv(f"{output_directory}/requests.csv", index=False)
            inventory_df.to_csv(f"{output_directory}/inventory.csv", index=False)
            available_drivers_df.to_csv(f"{output_directory}/available_drivers.csv", index=False)
            active_requests_df.to_csv(f"{output_directory}/active_requests.csv", index=False)
            unserviced_requests_df.to_csv(f"{output_directory}/unserviced_requests.csv", index=False)
            completed_requests_df.to_csv(f"{output_directory}/completed_requests.csv", index=False)
            vehiclle_operators_df.to_csv(f"{output_directory}/vehicle_operators.csv", index=False)
            vehicle_owners_df.to_csv(f"{output_directory}/vehicle_owners.csv", index=False)
        except Exception as e:
            print(f"Error saving data to CSV files: {e}")

    
# Generate data for each configuration
Index_Of_Config = 1
for data in config_data:
    generate_data(data)
    print(f"Data has been saved to the respective CSV files for Instance {Index_Of_Config}.")
    Index_Of_Config += 1


print("Data has been saved to the respective CSV files.")