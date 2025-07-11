Cloudflare R2 Bucket Cleanup Tool
A powerful Python script for efficiently managing and cleaning up your Cloudflare R2 storage buckets. This tool allows you to delete all objects or selectively remove only image files from your R2 buckets with comprehensive safety features.
✨ Features

🗑️ Bulk deletion - Delete all objects or just images from R2 buckets
🔍 Dry run mode - Preview what will be deleted before actual deletion
🚀 Efficient batch processing - Handles large buckets with thousands of files
🛡️ Safety features - Confirmation prompts and comprehensive error handling
📊 Progress tracking - Real-time progress reporting during operations
🎯 Flexible filtering - Support for image-only deletion with common formats
💻 Command line interface - Easy-to-use CLI with multiple options

🚀 Quick Start
Prerequisites

Python 3.6 or higher
Cloudflare R2 bucket and API credentials

Installation

Clone the repository:
bashgit clone https://github.com/yourusername/r2-bucket-cleanup.git
cd r2-bucket-cleanup

Install required dependencies:
bashpip install boto3

Configure your credentials:
Edit the script and update the config dictionary with your Cloudflare R2 credentials:
pythonconfig = {
    'account_id': 'your-cloudflare-account-id',
    'access_key': 'your-r2-access-key', 
    'secret_key': 'your-r2-secret-key',
    'bucket_name': 'your-bucket-name'
}


Getting Your Cloudflare R2 Credentials

Account ID: Found in your Cloudflare dashboard sidebar
API Credentials:

Go to Cloudflare Dashboard → R2 Object Storage → Manage R2 API tokens
Create a new API token with R2 permissions
Note down the Access Key ID and Secret Access Key



📖 Usage
Command Line Options
bash# Preview what would be deleted (recommended first step)
python3 delete.py --dry-run

# Preview only images that would be deleted
python3 delete.py --dry-run --images-only

# Delete all objects (BE CAREFUL!)
python3 delete.py --delete-all

# Delete only image files
python3 delete.py --delete-images

# Show help and all available options
python3 delete.py --help
Example Workflow

Start with a dry run to see what will be affected:
bashpython3 delete.py --dry-run

If you only want to delete images, preview first:
bashpython3 delete.py --dry-run --images-only

When ready, execute the actual deletion:
bashpython3 delete.py --delete-images  # For images only
# OR
python3 delete.py --delete-all     # For everything


🛡️ Safety Features

Dry Run Mode: Always test with --dry-run first to see what will be deleted
Confirmation Prompts: The script requires typing 'DELETE' to confirm destructive operations
Batch Processing: Efficient handling of large buckets without timeouts
Error Handling: Comprehensive error reporting and graceful failure handling
Progress Tracking: Real-time feedback on deletion progress

📁 Supported Image Formats
The script recognizes and can filter the following image formats:

JPEG/JPG
PNG
GIF
BMP
TIFF/TIF
WebP
SVG
ICO
AVIF
HEIC/HEIF

⚠️ Important Warnings

🔥 IRREVERSIBLE OPERATIONS: Deleted objects cannot be recovered
📋 ALWAYS DRY RUN FIRST: Use --dry-run to preview before deleting
💾 BACKUP CRITICAL DATA: Ensure you have backups of important files
🔒 SECURE CREDENTIALS: Never commit your API credentials to version control

🐛 Troubleshooting
Common Issues
Error: "Please update the configuration"

Make sure you've replaced all placeholder values in the config dictionary

Error: "AWS credentials not found"

Verify your access key and secret key are correct
Ensure your R2 API token has the necessary permissions

Error: "Access Denied"

Check that your API token has R2 read/write permissions
Verify the bucket name is correct and you have access to it

Large bucket timeouts

The script handles large buckets automatically with pagination
For very large buckets (100k+ objects), the operation may take several minutes
