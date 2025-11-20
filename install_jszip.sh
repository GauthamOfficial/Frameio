#!/bin/bash
# Install JSZip for branding kit zip functionality

echo "Installing JSZip and TypeScript types..."

# Install JSZip
npm install jszip@^3.10.1

# Install TypeScript types for JSZip
npm install --save-dev @types/jszip@^3.4.1

echo "✅ JSZip installation complete!"
echo "You can now use the zip download functionality in the branding kit page."
