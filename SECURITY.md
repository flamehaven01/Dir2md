# Security Policy

## Supported Versions
- Current `main` branch
- Latest tagged release (see CHANGELOG)

## Reporting a Vulnerability
- Email: info@flamehaven.space
- Include reproduction steps, affected version/commit, expected vs actual behavior, and any PoC.
- We acknowledge within 3 business days; fixes are developed privately and disclosed once patched.

## Handling Secrets and Licenses
- Set `DIR2MD_LICENSE` via environment variable or a local `.env` (never commit secrets).
- Keep separate dev/prod keys; rotate regularly.
- Default excludes `.env*`, `*.pem`, `*.key`. Do not remove these from ignore lists.

### Quick Setup
```bash
cp .env.example .env
export DIR2MD_LICENSE="PRO-your_license_key"
dir2md --version
```

## Pre-commit Safety Checks
```bash
git diff --cached | grep -i "PRO-\\|license\\|key\\|secret" || true
git secrets --scan || true
```

## Response Process
1) Triage and reproduce.  
2) Patch and regression-test.  
3) Publish advisory (and CVE if applicable) with upgrade guidance.  

## Contact
- Security: info@flamehaven.space
- License/support: https://flamehaven.space/
