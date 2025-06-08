#!/bin/bash
set -e

# TerraFusion One-Click Production Deploy (Netlify)

function print_progress() {
  local msg=$1
  echo -e "\033[1;36m[msg] $msg\033[0m"
}

print_progress "Building frontend..."
npm run build --prefix frontend

print_progress "Deploying to Netlify..."
netlify deploy --prod --dir=frontend/out --message "Automated production deploy" --json > deploy_result.json

print_progress "Deployment complete!"
DEPLOY_URL=$(jq -r '.url' deploy_result.json)
echo "Production site live at: $DEPLOY_URL" 