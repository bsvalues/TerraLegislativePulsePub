#!/bin/bash

# Create a zip file of the GitHub export
echo "Creating a zip archive of the GitHub export..."
zip -r github_export.zip github_export

# Display the location of the zip file
echo "--------------------------------"
echo "GitHub export has been created!"
echo "--------------------------------"
echo "File: github_export.zip"
echo "Size: $(du -h github_export.zip | cut -f1)"
echo ""
echo "Instructions:"
echo "1. Download this zip file from Replit using the Files panel"
echo "2. Extract the zip file on your local machine"
echo "3. Rename 'rename_to_requirements.txt' to 'requirements.txt'"
echo "4. Follow the steps in GITHUB_SETUP.md to create your GitHub repository"
echo "5. Push the contents of the extracted github_export folder to your GitHub repository"
echo ""
echo "The GitHub export has been sanitized to remove any sensitive information or Replit-specific files."