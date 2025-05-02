$ErrorActionPreference = "Stop"

$hookDir = ".git/hooks"
$srcDir = ".hooks"

if (-Not (Test-Path $hookDir)) {
    Write-Error ".git directory not found. Have you run 'git init'?"
    exit 1
}

Write-Host "Installing Git hooks..."

$preCommit = Join-Path $srcDir "pre-commit"
$postCommit = Join-Path $srcDir "post-commit"

Copy-Item $preCommit -Destination (Join-Path $hookDir "pre-commit") -Force
Copy-Item $postCommit -Destination (Join-Path $hookDir "post-commit") -Force

# Ensure they are executable (Git for Windows supports this in bash mode; native Git sometimes needs help)
# The following is mostly cosmetic for PowerShell users; Windows doesn't require +x
# but Git Bash may still benefit, so we try setting it via WSL or bash if available

try {
    if (Get-Command bash -ErrorAction SilentlyContinue) {
        bash -c "chmod +x .git/hooks/pre-commit .git/hooks/post-commit"
        Write-Host "Made hooks executable via bash."
    }
    else {
        Write-Host "Skipping chmod: 'bash' not found. If using Git Bash, you may want to set executable bits manually."
    }
} catch {
    Write-Warning "Could not set executable bits. Proceeding anyway."
}

Write-Host "Git hooks installed successfully."
