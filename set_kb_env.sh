#!/bin/bash

# Environment variables for the pets knowledge base
export STRANDS_KNOWLEDGE_BASE_ID="DGRJWBIGET"
export OPENSEARCH_COLLECTION_ID="fcjdfjp7robyhszlil9l"
export OPENSEARCH_ENDPOINT="https://fcjdfjp7robyhszlil9l.us-east-1.aoss.amazonaws.com"
export OPENSEARCH_HOST="fcjdfjp7robyhszlil9l.us-east-1.aoss.amazonaws.com"

# Add to bashrc for persistence
echo "export STRANDS_KNOWLEDGE_BASE_ID=\"${STRANDS_KNOWLEDGE_BASE_ID}\"" >> ~/.bashrc
echo "export OPENSEARCH_HOST=\"$OPENSEARCH_HOST\"" >> ~/.bashrc

echo "Environment variables set:"
echo "STRANDS_KNOWLEDGE_BASE_ID=$STRANDS_KNOWLEDGE_BASE_ID"
echo "OPENSEARCH_COLLECTION_ID=$OPENSEARCH_COLLECTION_ID"
echo "OPENSEARCH_ENDPOINT=$OPENSEARCH_ENDPOINT"
echo "OPENSEARCH_HOST=$OPENSEARCH_HOST"

echo ""
echo "Added to ~/.bashrc:"
tail -2 ~/.bashrc