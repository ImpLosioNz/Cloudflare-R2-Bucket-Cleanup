#!/usr/bin/env python3
"""
Cloudflare R2 Bucket Cleanup Script
Deletes all objects (images and folders) from a specified R2 bucket.

Requirements:
- pip install boto3
- Cloudflare R2 API credentials
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import time
from typing import List, Dict

class R2BucketCleaner:
    def __init__(self, account_id: str, access_key: str, secret_key: str, bucket_name: str):
        """
        Initialize the R2 bucket cleaner.
        
        Args:
            account_id: Your Cloudflare account ID
            access_key: R2 API access key
            secret_key: R2 API secret key
            bucket_name: Name of the bucket to clean
        """
        self.bucket_name = bucket_name
        self.account_id = account_id
        
        # Configure R2 client
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='auto'  # R2 uses 'auto' as region
        )
    
    def list_all_objects(self) -> List[Dict]:
        """List all objects in the bucket."""
        print(f"📋 Listing all objects in bucket '{self.bucket_name}'...")
        
        objects = []
        continuation_token = None
        
        try:
            while True:
                # Prepare list_objects_v2 parameters
                params = {
                    'Bucket': self.bucket_name,
                    'MaxKeys': 1000  # Maximum objects per request
                }
                
                if continuation_token:
                    params['ContinuationToken'] = continuation_token
                
                # List objects
                response = self.s3_client.list_objects_v2(**params)
                
                # Add objects to our list
                if 'Contents' in response:
                    objects.extend(response['Contents'])
                    print(f"   Found {len(response['Contents'])} objects in this batch...")
                
                # Check if there are more objects
                if not response.get('IsTruncated', False):
                    break
                    
                continuation_token = response.get('NextContinuationToken')
                
        except ClientError as e:
            print(f"❌ Error listing objects: {e}")
            return []
        
        print(f"✅ Total objects found: {len(objects)}")
        return objects
    
    def delete_objects_batch(self, objects: List[Dict]) -> bool:
        """Delete objects in batches of 1000 (AWS S3 limit)."""
        if not objects:
            return True
            
        # Prepare delete request
        delete_keys = [{'Key': obj['Key']} for obj in objects]
        
        try:
            response = self.s3_client.delete_objects(
                Bucket=self.bucket_name,
                Delete={
                    'Objects': delete_keys,
                    'Quiet': False  # Set to True to suppress successful deletion output
                }
            )
            
            # Check for errors
            if 'Errors' in response and response['Errors']:
                print(f"❌ Some deletions failed:")
                for error in response['Errors']:
                    print(f"   - {error['Key']}: {error['Message']}")
                return False
            
            # Report successful deletions
            if 'Deleted' in response:
                print(f"✅ Successfully deleted {len(response['Deleted'])} objects")
                
            return True
            
        except ClientError as e:
            print(f"❌ Error deleting batch: {e}")
            return False
    
    def filter_images(self, objects: List[Dict]) -> List[Dict]:
        """Filter objects to include only common image formats."""
        image_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
            '.webp', '.svg', '.ico', '.avif', '.heic', '.heif'
        }
        
        image_objects = []
        for obj in objects:
            key_lower = obj['Key'].lower()
            if any(key_lower.endswith(ext) for ext in image_extensions):
                image_objects.append(obj)
        
        print(f"🖼️  Found {len(image_objects)} image files out of {len(objects)} total objects")
        return image_objects
    
    def clean_bucket(self, images_only: bool = False, dry_run: bool = False):
        """
        Clean the bucket by deleting all objects or just images.
        
        Args:
            images_only: If True, delete only image files
            dry_run: If True, show what would be deleted without actually deleting
        """
        print(f"🧹 Starting bucket cleanup for '{self.bucket_name}'")
        print(f"   Mode: {'Images only' if images_only else 'All objects'}")
        print(f"   Dry run: {'Yes' if dry_run else 'No'}")
        print("-" * 50)
        
        # List all objects
        all_objects = self.list_all_objects()
        if not all_objects:
            print("✅ Bucket is already empty or no objects found.")
            return
        
        # Filter objects if needed
        objects_to_delete = self.filter_images(all_objects) if images_only else all_objects
        
        if not objects_to_delete:
            print("✅ No matching objects found to delete.")
            return
        
        # Show what will be deleted
        print(f"\n📋 Objects to delete ({len(objects_to_delete)}):")
        for i, obj in enumerate(objects_to_delete[:10]):  # Show first 10
            size_mb = obj['Size'] / (1024 * 1024)
            print(f"   {i+1:3d}. {obj['Key']} ({size_mb:.2f} MB)")
        
        if len(objects_to_delete) > 10:
            print(f"   ... and {len(objects_to_delete) - 10} more objects")
        
        if dry_run:
            print("\n🔍 DRY RUN: No objects were actually deleted.")
            return
        
        # Confirm deletion
        print(f"\n⚠️  WARNING: This will permanently delete {len(objects_to_delete)} objects!")
        confirm = input("Type 'DELETE' to confirm: ").strip()
        
        if confirm != 'DELETE':
            print("❌ Operation cancelled.")
            return
        
        # Delete objects in batches
        print(f"\n🗑️  Starting deletion...")
        batch_size = 1000  # AWS S3 limit
        total_deleted = 0
        
        for i in range(0, len(objects_to_delete), batch_size):
            batch = objects_to_delete[i:i + batch_size]
            print(f"\n   Processing batch {i//batch_size + 1} ({len(batch)} objects)...")
            
            if self.delete_objects_batch(batch):
                total_deleted += len(batch)
            else:
                print(f"❌ Failed to delete batch {i//batch_size + 1}")
            
            # Small delay between batches to avoid rate limiting
            if i + batch_size < len(objects_to_delete):
                time.sleep(0.5)
        
        print(f"\n✅ Cleanup completed! Deleted {total_deleted} objects.")


def main():
    """Main function with command line argument support."""
    import argparse
    
    # Set up command line arguments
    parser = argparse.ArgumentParser(
        description='Delete objects from Cloudflare R2 bucket',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 delete.py --dry-run                 # See what would be deleted
  python3 delete.py --dry-run --images-only   # See what images would be deleted
  python3 delete.py --delete-all               # Delete everything (BE CAREFUL!)
  python3 delete.py --delete-images            # Delete only images
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--dry-run', '-d', action='store_true',
                      help='Show what would be deleted without actually deleting')
    group.add_argument('--delete-all', '-a', action='store_true', 
                      help='Delete ALL objects (DANGEROUS!)')
    group.add_argument('--delete-images', '-i', action='store_true',
                      help='Delete only image files')
    
    parser.add_argument('--images-only', action='store_true',
                       help='When used with --dry-run, show only images')
    
    args = parser.parse_args()
    
    # Configuration - Replace with your actual R2 credentials
    config = {
        'account_id': 'your-cloudflare-account-id',
        'access_key': 'your-r2-access-key',
        'secret_key': 'your-r2-secret-key',
        'bucket_name': 'your-bucket-name'
    }
    
    # Validate configuration
    if any(value.startswith('your-') for value in config.values()):
        print("❌ Please update the configuration with your actual R2 credentials!")
        print("\nRequired values:")
        print("- account_id: Your Cloudflare account ID")
        print("- access_key: Your R2 API access key")
        print("- secret_key: Your R2 API secret key") 
        print("- bucket_name: Name of the bucket to clean")
        return
    
    try:
        # Initialize cleaner
        cleaner = R2BucketCleaner(**config)
        
        # Determine what to do based on arguments
        if args.dry_run:
            print("=== DRY RUN MODE ===")
            images_only = args.images_only
            cleaner.clean_bucket(images_only=images_only, dry_run=True)
        elif args.delete_all:
            print("=== DELETE ALL MODE ===")
            cleaner.clean_bucket(images_only=False, dry_run=False)
        elif args.delete_images:
            print("=== DELETE IMAGES MODE ===")
            cleaner.clean_bucket(images_only=True, dry_run=False)
        
    except NoCredentialsError:
        print("❌ AWS credentials not found. Please check your access key and secret key.")
    except ClientError as e:
        print(f"❌ AWS client error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
