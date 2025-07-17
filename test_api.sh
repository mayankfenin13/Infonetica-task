#!/bin/bash

BASE_URL="http://localhost:5002"
echo "Testing Workflow Engine API..."

echo "1. Testing health endpoint..."
curl -s -X GET $BASE_URL/health | python3 -m json.tool

echo -e "\n2. Creating workflow definition..."
RESPONSE=$(curl -s -X POST $BASE_URL/api/definitions \
  -H "Content-Type: application/json" \
  -d @test_workflow.json)
echo $RESPONSE | python3 -m json.tool

echo -e "\n3. Getting workflow definition..."
curl -s -X GET $BASE_URL/api/definitions/simple_approval | python3 -m json.tool

echo -e "\n4. Starting workflow instance..."
INSTANCE_RESPONSE=$(curl -s -X POST $BASE_URL/api/instances \
  -H "Content-Type: application/json" \
  -d '{"definition_id": "simple_approval"}')
echo $INSTANCE_RESPONSE | python3 -m json.tool

# Extract instance ID from response
INSTANCE_ID=$(echo $INSTANCE_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['data']['id'])" 2>/dev/null)

if [ ! -z "$INSTANCE_ID" ]; then
  echo -e "\n5. Getting workflow instance..."
  curl -s -X GET $BASE_URL/api/instances/$INSTANCE_ID | python3 -m json.tool

  echo -e "\n6. Getting available actions..."
  curl -s -X GET $BASE_URL/api/instances/$INSTANCE_ID/actions | python3 -m json.tool

  echo -e "\n7. Executing action 'submit_for_review'..."
  curl -s -X POST $BASE_URL/api/instances/$INSTANCE_ID/actions/submit_for_review | python3 -m json.tool

  echo -e "\n8. Getting updated instance state..."
  curl -s -X GET $BASE_URL/api/instances/$INSTANCE_ID | python3 -m json.tool
else
  echo "Failed to get instance ID"
fi

echo -e "\nAPI testing complete!"
