#!/usr/bin/env python3
"""
Pets Knowledge Base Setup Script

This script downloads the pets-kb-files.zip from the workshop URL,
extracts it, and creates a Bedrock Knowledge Base with the pet data.

Usage:
    python setup_pets_kb.py
"""

import os
import sys
import zipfile
import requests
import uuid
import boto3
from create_knowledge_base import BedrockKnowledgeBase

def download_and_extract_pets_data():
    """Download and extract the pets knowledge base files."""
    
    # Check for local pets-kb.zip file first
    local_zip = "pets-kb.zip"
    pets_kb_url = "https://d3k0crbaw2nl4d.cloudfront.net/pets-kb-files.zip"
    zip_filename = "pets-kb-files.zip"
    extract_dir = "pets-kb-files"
    
    # Check if already extracted
    if os.path.exists(extract_dir):
        print(f"Found existing {extract_dir}/ directory, using existing files...")
        return extract_dir
    
    # Check for local pets-kb.zip file
    if os.path.exists(local_zip):
        print(f"Found local {local_zip}, using this file...")
        zip_filename = local_zip
    elif os.path.exists(zip_filename):
        print(f"Found existing {zip_filename}, using local file...")
    else:
        print(f"Downloading pets knowledge base files from {pets_kb_url}...")
        
        try:
            # Download the zip file
            response = requests.get(pets_kb_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(zip_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Downloaded {zip_filename}")
            
        except Exception as e:
            print(f"Error downloading pets data: {e}")
            print(f"\nPlease manually download the file:")
            print(f"1. Download from: {pets_kb_url}")
            print(f"2. Save as: {zip_filename} or pets-kb.zip")
            print(f"3. Run this script again")
            sys.exit(1)
    
    try:
        # Extract the zip file
        print(f"Extracting {zip_filename}...")
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall()
        
        print(f"Extracted files to {extract_dir}/")
        return extract_dir
        
    except Exception as e:
        print(f"Error extracting pets data: {e}")
        sys.exit(1)

def upload_files_to_s3(bucket_name, local_dir):
    """Upload files from local directory to S3 bucket."""
    
    s3_client = boto3.client('s3')
    
    print(f"Uploading files from {local_dir}/ to s3://{bucket_name}/...")
    
    try:
        # Walk through all files in the directory
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_path = os.path.join(root, file)
                # Create S3 key by removing the local directory prefix
                s3_key = os.path.relpath(local_path, local_dir).replace('\\', '/')
                
                print(f"  Uploading {local_path} -> s3://{bucket_name}/{s3_key}")
                s3_client.upload_file(local_path, bucket_name, s3_key)
        
        print("Upload completed successfully!")
        
    except Exception as e:
        print(f"Error uploading files to S3: {e}")
        sys.exit(1)

def main():
    """Main function to set up the pets knowledge base."""
    
    print("=== Pets Knowledge Base Setup ===")
    print()
    
    # Generate a random suffix for unique resource names
    random_suffix = str(uuid.uuid4())[:8].lower()
    
    # Knowledge base configuration
    kb_name = f"pets-knowledge-base-{random_suffix}"
    kb_description = "Knowledge base containing information about pets, pet care, and veterinary advice"
    bucket_name = f"bedrock-kb-bucket-{random_suffix}"
    
    print(f"Knowledge Base Name: {kb_name}")
    print(f"S3 Bucket Name: {bucket_name}")
    print()
    
    # Step 1: Check for pets data
    pets_data_dir = "pets-kb-files"
    if not os.path.exists(pets_data_dir):
        pets_data_dir = download_and_extract_pets_data()
    else:
        print(f"Found existing {pets_data_dir}/ directory, using existing files...")
    
    # Step 2: Create the Bedrock Knowledge Base
    print("Creating Bedrock Knowledge Base...")
    print("This process takes approximately 7-9 minutes to complete.")
    print()
    
    try:
        kb = BedrockKnowledgeBase(
            kb_name=kb_name,
            kb_description=kb_description,
            data_bucket_name=bucket_name,
            embedding_model="amazon.titan-embed-text-v1"
        )
        
        print("Knowledge Base created successfully!")
        
        # Step 3: Upload pets data to S3
        upload_files_to_s3(bucket_name, pets_data_dir)
        
        # Step 4: Start ingestion job
        print("Starting ingestion job to sync data with Knowledge Base...")
        kb.start_ingestion_job()
        
        print("Ingestion job completed!")
        
        # Display final information
        print()
        print("=== Setup Complete ===")
        print(f"Knowledge Base ID: {kb.get_knowledge_base_id()}")
        print(f"S3 Bucket: {kb.get_bucket_name()}")
        print()
        print("Your pets knowledge base is now ready to use!")
        print("You can now create agents that use this knowledge base to answer questions about pets.")
        
        # Clean up local files
        import shutil
        shutil.rmtree(pets_data_dir)
        print(f"Cleaned up local directory: {pets_data_dir}")
        
    except Exception as e:
        print(f"Error creating knowledge base: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check if AWS credentials are configured
    try:
        # Try to get caller identity to verify credentials work
        session = boto3.Session()
        sts_client = session.client('sts')
        identity = sts_client.get_caller_identity()
        print(f"AWS Account: {identity['Account']}")
        print(f"AWS User/Role: {identity['Arn']}")
        print()
    except Exception as e:
        print(f"Error: AWS credentials not configured properly: {e}")
        print("Please configure your AWS credentials using one of these methods:")
        print("1. aws configure")
        print("2. Set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION")
        print("3. Use IAM roles (if running on EC2)")
        sys.exit(1)
    
    main()