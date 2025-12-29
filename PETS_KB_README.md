# Pets Knowledge Base Workshop

This workshop demonstrates how to create a Bedrock Knowledge Base with pet care information and use it with Strands Agents.

## Prerequisites

1. **AWS Account** with appropriate permissions for:
   - Amazon Bedrock
   - Amazon S3
   - Amazon OpenSearch Serverless
   - IAM roles and policies

2. **AWS CLI configured** with your credentials:
   ```bash
   aws configure
   ```

3. **Python environment** with required dependencies:
   ```bash
   pip install -e .
   ```

## Quick Setup

### Option 1: Automated Setup (Recommended)

Run the automated setup script:

```bash
python setup_pets_kb.py
```

This script will:
1. Download `pets-kb-files.zip` from the workshop URL
2. Extract the pet care documents
3. Create an S3 bucket with a random suffix
4. Create a Bedrock Knowledge Base with OpenSearch Serverless
5. Upload the documents to S3
6. Start an ingestion job to sync the data

**Note:** This process takes approximately 7-9 minutes to complete.

### Option 2: Manual Setup

If you prefer manual setup:

1. **Download and extract the data:**
   ```bash
   curl -LO https://d3k0crbaw2nl4d.cloudfront.net/pets-kb-files.zip
   unzip pets-kb-files.zip
   ```

2. **Create S3 bucket and upload files:**
   ```bash
   random_suffix=$(uuidgen | cut -c1-8 | tr '[:upper:]' '[:lower:]')
   s3_bucket="bedrock-kb-bucket-${random_suffix}"
   aws s3 mb "s3://${s3_bucket}"
   aws s3 sync pets-kb-files/ "s3://${s3_bucket}"
   ```

3. **Create the Knowledge Base using the AWS Console or CLI**

## Using the Pets Agent

After setup is complete, you'll receive a Knowledge Base ID. Use it to run the demo agent:

```bash
python pets_agent_demo.py <KNOWLEDGE_BASE_ID>
```

### Example Usage

```bash
python pets_agent_demo.py ABCD1234EFGH
```

The agent can answer questions like:
- "What should I feed my puppy?"
- "How often should I take my cat to the vet?"
- "What are signs of illness in dogs?"
- "How do I train my dog to sit?"
- "What vaccinations does my pet need?"

## Files Description

- **`setup_pets_kb.py`** - Automated setup script for the knowledge base
- **`pets_agent_demo.py`** - Interactive demo of the pets knowledge base agent
- **`create_knowledge_base.py`** - Core class for managing Bedrock Knowledge Bases
- **`README.md`** - This documentation file

## Architecture

The setup creates the following AWS resources:

1. **S3 Bucket** - Stores the pet care documents
2. **OpenSearch Serverless Collection** - Vector database for embeddings
3. **Bedrock Knowledge Base** - Manages the RAG pipeline
4. **IAM Roles and Policies** - Secure access between services
5. **Vector Index** - Enables semantic search

## Troubleshooting

### Common Issues

1. **AWS Credentials Not Configured**
   ```
   Error: AWS credentials not configured properly.
   ```
   **Solution:** Run `aws configure` or set environment variables

2. **Insufficient Permissions**
   ```
   Error: User is not authorized to perform: bedrock:CreateKnowledgeBase
   ```
   **Solution:** Ensure your AWS user/role has Bedrock permissions

3. **Region Not Supported**
   ```
   Error: Bedrock is not available in this region
   ```
   **Solution:** Use a supported region (us-east-1, us-west-2, etc.)

### Cleanup

To delete all created resources:

```python
from create_knowledge_base import BedrockKnowledgeBase

# Initialize with your KB details
kb = BedrockKnowledgeBase(kb_name="your-kb-name")

# Delete everything (including S3 bucket and IAM resources)
kb.delete_kb(delete_s3_bucket=True, delete_iam_roles_and_policies=True)
```

## Next Steps

1. **Customize the Agent** - Modify the system prompt in `pets_agent_demo.py`
2. **Add More Tools** - Integrate additional Strands tools
3. **Build a Web Interface** - Create a web app using the agent
4. **Add Your Own Data** - Upload additional pet care documents to the S3 bucket

## Support

For issues with:
- **Strands Agents** - Check the [Strands documentation](https://strandsagents.com)
- **AWS Bedrock** - Refer to the [AWS Bedrock documentation](https://docs.aws.amazon.com/bedrock/)
- **This Workshop** - Create an issue in the repository

## License

This workshop is provided under the Apache License 2.0.