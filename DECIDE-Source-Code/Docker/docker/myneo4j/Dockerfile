# Use an official Neo4j image as the base
FROM neo4j:4.4

# # Copy your .dump file into the container
# COPY DECIDE-KnowledgeBase.dump /var/lib/neo4j/data/databases/

RUN echo "Building the Docker image..."

# Copy your import script and .dump file into the container
COPY import.sh /var/lib/neo4j/
COPY sodata.dump /var/lib/neo4j/import/
# COPY data /var/lib/neo4j
# Make the import script executable
# RUN chmod +x /var/lib/neo4j/import.sh
# RUN bash /var/lib/neo4j/import.sh

RUN neo4j-admin load --from=/var/lib/neo4j/import/sodata.dump --database=neo4j --force
RUN echo "Initiating Neo4J database..."
# RUN sleep 5

# Expose necessary ports
EXPOSE 7474 7687

# Set environment variables (optional)
ENV NEO4J_AUTH=neo4j/knowledgeextraction

# Entrypoint command to start Neo4j
CMD ["neo4j"]
# CMD ["bash", "-c", "while true; do sleep 1; done"]