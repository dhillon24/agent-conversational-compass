
#!/bin/bash

# Qdrant Collection Initialization Script
# This script creates the necessary collections and sets up the schema

QDRANT_URL=${QDRANT_URL:-"http://localhost:6333"}
COLLECTION_NAME="customer_conversations"
VECTOR_SIZE=512

echo "Initializing Qdrant collections..."
echo "Qdrant URL: $QDRANT_URL"

# Wait for Qdrant to be ready
echo "Waiting for Qdrant to be ready..."
until curl -f "$QDRANT_URL/health" > /dev/null 2>&1; do
    echo "Waiting for Qdrant..."
    sleep 2
done

echo "Qdrant is ready!"

# Create the customer conversations collection
echo "Creating collection: $COLLECTION_NAME"

curl -X PUT "$QDRANT_URL/collections/$COLLECTION_NAME" \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": '"$VECTOR_SIZE"',
      "distance": "Cosine"
    },
    "optimizers_config": {
      "default_segment_number": 2
    },
    "replication_factor": 1
  }'

echo ""
echo "Collection created successfully!"

# Create payload index for efficient filtering
echo "Creating payload indexes..."

# Index for user_id filtering
curl -X PUT "$QDRANT_URL/collections/$COLLECTION_NAME/index" \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "user_id",
    "field_schema": "keyword"
  }'

# Index for timestamp filtering
curl -X PUT "$QDRANT_URL/collections/$COLLECTION_NAME/index" \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "timestamp",
    "field_schema": "datetime"
  }'

# Index for conversation type filtering
curl -X PUT "$QDRANT_URL/collections/$COLLECTION_NAME/index" \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "type",
    "field_schema": "keyword"
  }'

echo ""
echo "Payload indexes created successfully!"

# Verify collection creation
echo "Verifying collection..."
curl -X GET "$QDRANT_URL/collections/$COLLECTION_NAME" | python3 -m json.tool

echo ""
echo "Qdrant initialization complete!"
echo ""
echo "Collection '$COLLECTION_NAME' is ready with:"
echo "- Vector size: $VECTOR_SIZE (CLIP embeddings)"
echo "- Distance metric: Cosine similarity"
echo "- Indexed fields: user_id, timestamp, type"
echo "- Optimized for conversation storage and retrieval"
