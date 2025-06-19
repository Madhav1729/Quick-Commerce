import pandas as pd
from quick_commerce.src.Data_Generation_Code.Gen_Data import city_list, operators, stores, customers
from quick_commerce.src.Data_Generation_Code.models import *

#run this for all instances in the Generated_datasets folder
city_list_df = pd.read_csv("quick_commerce/Data/Generated_datasets_and_input_instance/Instance_1/Generated_data/stores.csv")
city_list = []
for index, row in city_list_df.iterrows():
    city_list.append(
        City(
            row["city_id"],
            row["name"],
            row["center_latitude"],
            row["center_longitude"],
            row["radius"],
            row["district"],
            row["state"],
            row["country"],
            row["population"],
            row["list_of_operators"],
        )
    )

operators_df = pd.read_csv("quick_commerce/Data/Generated_datasets_and_input_instance/Instance_1/Generated_data/quick_commerce_operators.csv")
# create a list of objects from the operators_df
operators = []
for index, row in operators_df.iterrows():
    operators.append(
        Operator(
            row["operator_id"],
            row["name"],
            row["contact_email"],
            row["contact_phone"],
            row["contact_person_name"],
            row["registered_name"],
            row["registered_address"],
            row["operates_in"],
            row["start_time"],
            row["end_time"],
            row["list_of_stores"],
        )
    )
stores_df = pd.read_csv("quick_commerce/Data/Generated_datasets_and_input_instance/Instance_1/Generated_data/stores.csv")
# create a list of objects from the stores_df
stores = []
for index, row in stores_df.iterrows():
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
            row["inventory_capacity"],
        )
    )
customers_df = pd.read_csv("quick_commerce/Data/Generated_datasets_and_input_instance/Instance_1/Generated_data/customers.csv")
# create a list of objects from the customers_df
customers = []
for index, row in customers_df.iterrows():
    customers.append(
        Customer(
            row["customer_id"],
            row["location_latitude"],
            row["location_longitude"],
            row["address"],
            row["city_id"],
        )
    )


def verify_cities_data():
    cities_df = pd.read_csv("quick_commerce/Data/Generated_datasets_and_input_instance/Instance_1/Generated_data/cities.csv")

    for city in city_list:
        if city.name not in cities_df["City"].values:
            print(f"City {city.name} not found in the dataset")
        # for each city in city_list , for each item in list_of operators check if the operator matches with the operator id in operators list
        for operator in city.list_of_operators:
            if operator not in [operator.operator_id for operator in operators]:
                print(f"Operator {operator} not found in the dataset")

    print("Cities data verified successfully")


verify_cities_data()


def verify_operators_data():
    for operator in operators:
        for city in operator.operates_in:
            if city not in [city.city_id for city in city_list]:
                print(
                    f"City {city} of operator {operator.operator_id} not found in the dataset"
                )
        # for each operator in operators list, for each item in list_of_stores check if the store matches with the store id in stores list
        for store in operator.list_of_stores:
            if store not in [store.store_id for store in stores]:
                print(
                    f"Store {store} of operator {operator.operator_id} not found in the dataset"
                )

    print("Operators data verified successfully")


verify_operators_data()


def verify_stores_data():
    for store in stores:

        # for each store in stores list, check if the city matches with the city id in city list
        if store.city_id not in [city.city_id for city in city_list]:
            print(
                f"City {store.city_id} of store {store.store_id} not found in the dataset"
            )

        # for each store in stores list, check if the operator matches with the operator id in operators list
        if store.operator_id not in [operator.operator_id for operator in operators]:
            print(
                f"Operator {store.operator_id} of store {store.store_id} not found in the dataset"
            )

        # checking whether the start time is greater than end time
        if store.start_time > store.end_time:
            print(f"Store {store.store_id} start time is greater than end time")

        # checking whether the inventory capacity is negative
        if store.inventory_capacity < 0:
            print(f"Store {store.store_id} inventory capacity is negative")

        # checking whether the operator operates in the city of the store
        if store.city_id not in operators[store.operator_id - 1].operates_in:
            print(
                f"City {store.city_id} of store {store.store_id} not found in the list of cities of operator {store.operator_id}"
            )
        # checking whether the store id in the list of stores of the operator is same as the store id
        if store.store_id not in operators[store.operator_id - 1].list_of_stores:
            print(
                f"Store {store.store_id} not found in the list of stores of operator {store.operator_id}"
            )
        # checking whether store latitude and longitude are within the city radius
        if (
            store.location_latitude - city_list[store.city_id - 1].center_latitude
        ) ** 2 + (
            store.location_longitude - city_list[store.city_id - 1].center_longitude
        ) ** 2 > city_list[
            store.city_id - 1
        ].radius ** 2:
            print(
                f"Store {store.store_id} latitude and longitude are not within the city radius"
            )
    print("Stores data verified successfully")


verify_stores_data()


def verify_customers():
    for customer in customers:

        # check if the city id is present in the city list
        if customer.city_id not in [city.city_id for city in city_list]:
            print(
                f"City {customer.city_id} of customer {customer.customer_id} not found in the dataset"
            )
        # checking whether the customer latitude and longitude are within the city radius
        if (
            customer.location_latitude - city_list[customer.city_id - 1].center_latitude
        ) ** 2 + (
            customer.location_longitude
            - city_list[customer.city_id - 1].center_longitude
        ) ** 2 > city_list[
            customer.city_id - 1
        ].radius ** 2:
            print(
                f"Customer {customer.customer_id} latitude and longitude are not within the city radius"
            )
    print("Customers data verified successfully")


verify_customers()

