import os
from confluent_kafka.avro import AvroConsumer, AvroProducer
from confluent_kafka import avro

# Load Avro schema
order_schema = avro.load("order_schema.avsc")  # Load the schema directly using the file path

# Consumer configuration
consumer_config = {
    'bootstrap.servers': 'kafka:29092',
    'group.id': 'order-group',
    'auto.offset.reset': 'earliest',
    'schema.registry.url': 'http://schema-registry:8081'
}

# Producer configuration
producer_config = {
    'bootstrap.servers':  'kafka:29092',
    'schema.registry.url': 'http://schema-registry:8081'
}

# Create consumer and producer
consumer = AvroConsumer(consumer_config)
producer = AvroProducer(producer_config, default_value_schema=order_schema)

# Subscribe to the 'orders' topic
consumer.subscribe(['orders'])

def validate_order(order):
    """Validation logic for the order."""
    return order['quantity'] > 0 and order['price'] > 0

try:
    while True:
        msg = consumer.poll(25.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Error: {msg.error()}")
            continue
        
        order = msg.value()  # Deserialize the Avro message
        print(f"Received order: {order}")  # Debugging line

        # Enrich or send to invalid orders based on validation
        if validate_order(order):
            order['total_value'] = order['quantity'] * order['price']
            producer.produce('enriched_orders', value=order, key=str(order['order_id']))  # Ensure the key is a string
        else:
            producer.produce('invalid_orders', value=order, key=str(order['order_id']))  # Ensure the key is a string

        producer.flush()  # Flush producer to send the messages

except Exception as e:
    print(f"Exception occurred: {e}")
finally:
    consumer.close()
