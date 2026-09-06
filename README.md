# AP Invoice Control

AP Invoice Control is a browser-based proof of concept for bringing invoice capture, validation, exceptions, approvals, and reporting into one controlled AP workspace. It is a working demo, not a production finance system.

## What the prototype demonstrates

- Structured invoice capture with vendor, tax, TDS/RCM, PO, agreement, cost-centre, and GL fields.
- Validation for required fields, tax reconciliation, GSTIN/PAN format, duplicates, vendor-master consistency, PO and agreement checks, payment terms, and MSME 45-day rules.
- Risk scoring and named exception resolution or approved override records.
- Segregation of duties across AP Maker, AP Reviewer, Approver, and Finance Admin roles.
- An audit trail for status changes, approvals, and overrides.
- Dashboard and invoice-register views, plus an Excel export with register, validation, exception, vendor-summary, and dashboard sheets.
- Editable demo master data and business-rule tolerances.

For a complete walkthrough, including a staged duplicate-detection example and role-switching sequence, see [DEMO_SCRIPT.md](DEMO_SCRIPT.md).

## Run locally

Open `index.html` in a modern browser. The demo data and in-progress work are saved in that browser's local storage. Use **Master Data → Business Rules → Reset demo data** to restore the original seeded data.

## GitHub Pages — one command

1. Create a short-lived **fine-grained personal access token** at [GitHub token settings](https://github.com/settings/personal-access-tokens/new). Choose your account as resource owner, choose **All repositories** (because the repository does not exist yet), and grant:
   - **Administration: Read and write**
   - **Contents: Read and write**
   - **Pages: Read and write**
   - **Workflows: Read and write**

   A classic token with `repo` and `workflow` scopes also works. Revoke the temporary token after deployment.

2. From this folder, run:

   ```powershell
   python .\deploy_to_github.py
   ```

3. Paste the token at the hidden prompt. The script creates a public `ap-invoice-control` repository, uploads the application and documentation, enables Pages from `main` at the repository root, and prints the live address.

To use another repository name:

```powershell
python .\deploy_to_github.py --repo ap-invoice-control-demo
```

The token stays in memory only; it is not saved or printed.

## Automatic updates

`.github/workflows/deploy.yml` is an optional GitHub Actions deployment workflow. It publishes every normal push to `main`. To use it instead of direct branch publishing, bootstrap the repository with:

```powershell
python .\deploy_to_github.py --pages-mode workflow
```

Then push a normal commit to `main` to start the first Actions deployment.

## Prototype and security boundaries

- This demo has no ERP, vendor-master, GSTN, identity, or production database integration. Use sample or anonymised data only.
- Browser state is local to each browser profile; it is not shared, backed up, or suitable as an audit system of record.
- Excel export and dashboard charts load their pinned libraries from cdnjs, so those features need internet access.
- The source includes an experimental Claude document-extraction call. A public static site cannot safely hold an AI API credential, and the current prototype does not include an authenticated backend. Do not use real invoices or add an API key to `index.html`; route extraction through an authenticated server-side service before production use.
- The deployment script excludes `.env` files, but review everything before making a repository public.

