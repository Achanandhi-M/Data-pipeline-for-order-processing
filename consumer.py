from confluent_kafka import Consumer, Producer
import json
import psycopg2

db_config = {
    'dbname': 'orders_db',
    'user': 'user',
    'password': 'password',
    'host': 'postgres',
    'port': '5432'
}

conn = psycopg2.connect(**db_config)
cursor = conn.cursor()

create_table_query = """
CREATE TABLE IF NOT EXISTS enriched_orders (
    order_id SERIAL PRIMARY KEY,
    product_name TEXT,
    quantity INT,
    price DECIMAL,
    order_date INT,
    total_value DECIMAL
);
"""

cursor.execute(create_table_query)
conn.commit()  
print("Table 'enriched_orders' ensured.")

consumer_config = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'order-group',
    'auto.offset.reset': 'earliest'
}

producer_config = {
    'bootstrap.servers': 'kafka:9092'
}

consumer = Consumer(consumer_config)
producer = Producer(producer_config)

consumer.subscribe(['orders'])

def validate_order(order):
    return order['quantity'] > 0 and order['price'] > 0

try:
    while True:
        msg = consumer.poll(25.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Error: {msg.error()}")
            continue

        if msg.value() is None or len(msg.value()) == 0:
            print("Received empty message, skipping...")
            continue
        
        order = json.loads(msg.value().decode('utf-8'))

        if validate_order(order):
            order['total_value'] = order['quantity'] * order['price']

            insert_query = """
            INSERT INTO enriched_orders (product_name, quantity, price, order_date, total_value)
            VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(insert_query, (order['product_name'], order['quantity'], order['price'], order['order_date'], order['total_value']))
            conn.commit() 

            producer.produce('enriched_orders', json.dumps(order), callback=lambda err, msg: print(f"Produced message to enriched_orders: {msg.key()}: {msg.value()}") if err is None else print(f"Error producing message: {err}"))
        else:
            producer.produce('invalid_orders', json.dumps(order), callback=lambda err, msg: print(f"Produced message to invalid_orders: {msg.key()}: {msg.value()}") if err is None else print(f"Error producing message: {err}"))

        producer.flush()  

finally:
    consumer.close()
    cursor.close()
    conn.close()
