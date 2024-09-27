# Kafka Order Processing Application

This application is designed to process orders from a JSON server using Apache Kafka. It consists of a producer that fetches orders, a consumer that validates and enriches those orders, and a PostgreSQL database to store the enriched data.

## Overview

The application has the following components:

- **JSON Server**: Provides a REST API to simulate an order database.
- **Kafka**: Acts as a message broker to handle communication between the producer and consumer.
- **PostgreSQL**: Stores enriched order data.
- **Kafka Connect**: Manages the integration of data between Kafka and PostgreSQL using source and sink connectors.

## Features

- Fetches orders from a JSON server.
- Validates orders to ensure they have positive quantities and prices.
- Enriches valid orders by calculating the total value.
- Stores enriched orders in a PostgreSQL database.
- Sends invalid orders to a separate Kafka topic for further handling.

## Requirements

- Docker
- Docker Compose

## Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/kafka-order-processing.git
   cd kafka-order-processing
   ```

2. **Configure the Environment**

   Make sure to update the database credentials in the `docker-compose.yml` file if necessary.

3. **Start the Application**

   Use Docker Compose to build and run the application:

   ```bash
   docker-compose up --build
   ```

4. **Verify Services are Running**

   After the containers start, ensure all services are running correctly by accessing the following URLs:
   - Kafka Connect: [http://localhost:8083](http://localhost:8083)
   - JSON Server: [http://localhost:8080](http://localhost:8080)

5. **Create Kafka Connectors**

   To set up the source and sink connectors, run the following commands in separate terminal windows:

   ```bash
   # Create HttpSourceConnector
            
   curl -X POST -H "Content-Type: application/json" --data '{
     "name": "http-source-connector",
     "config": {
       "connector.class": "io.confluent.connect.http.HttpSourceConnector",
       "tasks.max": "1",
       "url": "http://json-server:8080/orders",
       "topic.name.pattern": "orders",
       "confluent.topic.bootstrap.servers": "kafka:9092",
       "key.converter": "org.apache.kafka.connect.storage.StringConverter",
       "value.converter.schemas.enable": "true",
       "key.converter.schema.registry.url": "http://localhost:8081",
       "value.converter.schema.registry.url": "http://localhost:8081",
       "poll.interval.ms": "30000",
       "http.offset.mode": "SIMPLE_INCREMENTING",
       "http.initial.offset": "0",
       "confluent.topic.replication.factor": "1"
     }
   }' http://localhost:8083/connectors
  
  
   # Create JdbcSinkConnector
   
   curl -X POST -H "Content-Type: application/json" --data '{
     "name": "postgres-sink-connector",
     "config": {
       "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
       "tasks.max": "1",
       "connection.url": "jdbc:postgresql://postgres:5432/orders_db",
       "connection.user": "user",
       "connection.password": "password",
       "topics": "enriched_orders",
       "insert.mode": "insert",
       "auto.create": "true",
       "auto.evolve": "true",
       "key.converter": "org.apache.kafka.connect.storage.StringConverter",
       "value.converter": "io.confluent.connect.avro.AvroConverter",
       "value.converter.schema.registry.url": "http://localhost:8081",
       "key.converter.schema.registry.url": "http://localhost:8081"
     }
   }' http://localhost:8083/connectors
   ```

## Usage

- After the connectors are created, the application will start processing orders.
- Valid orders will be enriched and stored in the PostgreSQL database (`enriched_orders` table).
- Invalid orders will be published to the `invalid_orders` topic.

## Troubleshooting

- Ensure Docker and Docker Compose are installed and running.
- Check the logs for individual services using `docker-compose logs` for any errors.

## Acknowledgments

- [Apache Kafka](https://kafka.apache.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Confluent](https://www.confluent.io/)
- [JSON Server](https://github.com/typicode/json-server)

