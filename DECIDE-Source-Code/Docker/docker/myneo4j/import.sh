#!/bin/bash
# neo4j-admin load --from=/var/lib/neo4j/import/sodata.dump --database=neo4j --force
#  --force
neo4j-admin load --from=/var/lib/neo4j/import/sodata.dump --database=neo4j --force
neo4j start
echo "Initiating Neo4J database..."
sleep 5