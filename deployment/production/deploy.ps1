# TerraFusion One-Click Production Deploy (Netlify)

function Print-Progress($msg) {
    Write-Host "[msg] $msg" -ForegroundColor Cyan
}

Print-Progress "Building frontend..."
npm run build --prefix frontend

Print-Progress "Deploying to Netlify..."
netlify deploy --prod --dir=frontend/out --message "Automated production deploy" --json | Out-File -Encoding utf8 deploy_result.json

Print-Progress "Deployment complete!"
$deployResult = Get-Content deploy_result.json | ConvertFrom-Json
Write-Host "Production site live at: $($deployResult.url)" -ForegroundColor Green 