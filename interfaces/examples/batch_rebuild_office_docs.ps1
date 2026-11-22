<#
.SYNOPSIS
    GoDOCXEDIT Sample Batch Rebuild Script (PowerShell)
    License: MIT License (see LICENSE-INTERFACES). Applies ONLY to this script,
    NOT to GoDOCXEDIT.exe (governed by LICENSE / EULA).

.DESCRIPTION
    Demonstrates a safe 2-step enterprise workflow using GoDOCXEDIT.exe Headless CLI:
    1. Read-only compatibility audit of legacy Office documents.
    2. Batch rebuild into a completely separate output directory (never overwrites originals).

.EXAMPLE
    .\batch_rebuild_office_docs.ps1 `
        -ExePath "C:\Tools\GoDOCXEDIT\GoDOCXEDIT.exe" `
        -InputDir "D:\LegacyOfficeDocs" `
        -OutputDir "D:\WordAndGoogleDocsReady" `
        -CjkFont "Microsoft JhengHei" `
        -LatinFont "Calibri"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ExePath,

    [Parameter(Mandatory = $true)]
    [string]$InputDir,

    [Parameter(Mandatory = $true)]
    [string]$OutputDir,

    [string]$Format = "docx",
    [string]$CjkFont = "Microsoft JhengHei",
    [string]$LatinFont = "Calibri"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $ExePath -PathType Leaf)) {
    throw "GoDOCXEDIT.exe not found at: $ExePath"
}
if (-not (Test-Path -LiteralPath $InputDir -PathType Container)) {
    throw "Input directory not found at: $InputDir"
}

$ReportDir = Join-Path -Path $OutputDir -ChildPath "_godocxedit_reports"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

$AuditReport = Join-Path -Path $ReportDir -ChildPath "audit_report.json"
$BatchReport = Join-Path -Path $ReportDir -ChildPath "batch_report.json"

Write-Host "=== Step 1: Read-Only Compatibility Audit ==="
$auditProc = Start-Process -FilePath $ExePath -ArgumentList @(
    "audit", $InputDir,
    "--json",
    "--report", $AuditReport
) -Wait -PassThru -NoNewWindow

if (Test-Path -LiteralPath $AuditReport) {
    $auditJson = Get-Content -LiteralPath $AuditReport -Raw -Encoding UTF8 | ConvertFrom-Json
    Write-Host ("Audit Summary -> Total: {0}, NeedsNormalization: {1}, Clean: {2}, Skipped: {3}, Failed: {4}" -f `
        $auditJson.summary.total, `
        $auditJson.summary.needsNormalization, `
        $auditJson.summary.cleanCompatible, `
        $auditJson.summary.skipped, `
        $auditJson.summary.failed)
}

Write-Host "=== Step 2: Safe Batch Rebuild (Separate Output Directory) ==="
$batchProc = Start-Process -FilePath $ExePath -ArgumentList @(
    "batch", $InputDir,
    "--output", $OutputDir,
    "--format", $Format,
    "--cjk-font", $CjkFont,
    "--latin-font", $LatinFont,
    "--json",
    "--report", $BatchReport
) -Wait -PassThru -NoNewWindow

if (Test-Path -LiteralPath $BatchReport) {
    $batchJson = Get-Content -LiteralPath $BatchReport -Raw -Encoding UTF8 | ConvertFrom-Json
    Write-Host ("Batch Summary -> Total: {0}, Succeeded: {1}, Normalized: {2}, Skipped: {3}, Failed: {4}" -f `
        $batchJson.summary.total, `
        $batchJson.summary.succeeded, `
        $batchJson.summary.normalized, `
        $batchJson.summary.skipped, `
        $batchJson.summary.failed)
    Write-Host "Full JSON report saved to: $BatchReport"
}

exit $batchProc.ExitCode
