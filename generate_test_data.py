import uuid
import faker
import os
import datetime

from faker.generator import random
from google.cloud import spanner

INSTANCE_ID = os.environ.get("INSTANCE_ID")
DATABASE_ID = os.environ.get("DATABASE_ID")

# Create a Faker object
fake = faker.Faker()

spanner_client = spanner.Client()
instance = spanner_client.instance(INSTANCE_ID)
database = instance.database(DATABASE_ID)


def delete_everything(tables):
    all_rows = spanner.KeySet(all_=True)
    with database.batch() as batch:
        for table in tables:
            batch.delete(table, all_rows)

    print("Deleted all data.")


# Generate categories
def generate_categories():
    categories = []
    for _ in range(10):
        category_id = uuid.uuid4().hex
        name = fake.word()

        categories.append({
            "category_id": category_id,
            "name": name
        })

    return categories


# Generate customers
def generate_customers():
    customers = []
    for _ in range(20):
        customer_id = uuid.uuid4().hex
        name = fake.name()
        email = fake.email()
        address = fake.address()
        phone_number = fake.phone_number()

        customers.append({
            "customer_id": customer_id,
            "name": name,
            "email": email,
            "address": address,
            "phone_number": phone_number
        })
    return customers


# Generate products
def generate_products(categories):
    products = []
    for _ in range(30):
        product_id = uuid.uuid4().hex
        name = fake.word()
        description = fake.paragraph(2)
        price = round(fake.random_int(10, 1000), 2)
        image_url = fake.image_url()
        category_id = random.choice(categories).get('category_id')

        products.append({
            "product_id": product_id,
            "name": name,
            "description": description,
            "price": price,
            "image_url": image_url,
            "category_id": category_id
        })
    return products


# Generate orders
def generate_orders(customers, products):
    orders = []
    start_date = datetime.date(2023, 12, 10)
    end_date = datetime.date(2024, 12, 10)
    random_time = datetime.time(10, 0, 0)
    for _ in range(15):
        order_id = uuid.uuid4().hex
        customer_id = random.choice(customers).get('customer_id')
        order_date_only = fake.date_between(start_date, end_date)
        order_date = datetime.datetime.combine(order_date_only, random_time)
        total_amount = round(fake.random_int(10, 1000), 2)
        shipping_address = random.choice(customers).get('address')
        billing_address = random.choice(customers).get('address')

        order_items = []
        for _ in range(random.randint(1, 5)):
            product_id = random.choice(products).get('product_id')
            quantity = random.randint(1, 5)

            order_items.append({
                "order_item_id": uuid.uuid4().hex,
                "order_id": order_id,
                "product_id": product_id,
                "quantity": quantity
            })

        orders.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "order_date": order_date,
            "total_amount": total_amount,
            "shipping_address": shipping_address,
            "billing_address": billing_address,
            "order_items": order_items
        })
    return orders


def map_for_insertion(list_of_dict):
    result_array = []
    ordered_columns = list_of_dict[0].keys()
    for row in list_of_dict:
        row_array = []
        for col in ordered_columns:
            row_array.append(row[col])
        result_array.append(tuple(row_array))

    return result_array


def batch_insert(table, list_of_dict):
    with database.batch() as batch:
        batch.insert(
            table=table,
            columns=list_of_dict[0].keys(),
            values=map_for_insertion(list_of_dict)
        )


delete_everything(tables=['order_items', 'orders', 'products', 'customers', 'categories'])

categories = generate_categories()
customers = generate_customers()
products = generate_products(categories)
orders = generate_orders(customers, products)

batch_insert(table='categories', list_of_dict=categories)
batch_insert(table='customers', list_of_dict=customers)
batch_insert(table='products', list_of_dict=products)

orders_columns = ['order_id', 'customer_id', 'order_date', 'total_amount', 'shipping_address', 'billing_address']
order_items = []
for o in orders:
    for i in o['order_items']:
        order_items.append(i)

batch_insert(table='orders', list_of_dict=[{k: x[k] for k in orders_columns} for x in orders])
batch_insert(table='order_items', list_of_dict=order_items)
