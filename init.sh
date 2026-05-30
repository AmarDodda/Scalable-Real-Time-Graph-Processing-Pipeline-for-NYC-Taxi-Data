#!/bin/bash
echo "Waiting for Kafka Connect to start listening on localhost ⏳"

while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' localhost:8083/)" != "200" ]]; do 
  echo "$(date) Kafka Connect listener HTTP state: $(curl -s -o /dev/null -w ''%{http_code}'' localhost:8083/) (waiting for 200)"
  sleep 5
done

echo "Kafka Connect REST API is up! 🚀"

echo "Creating Neo4j Sink Connector 🛠️"

curl -X POST -H "Content-Type: application/json" --data @/config/sink.neo4j.json http://localhost:8083/connectors

echo "Connector created"
