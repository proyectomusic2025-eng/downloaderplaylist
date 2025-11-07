# Deployment Checklist - MusicDown (step-by-step)

This checklist guides you from zero knowledge to a working deployment with Ko-fi and the downloadable EXE link.

## 1) Prepare code & repo
- [ ] Unzip `musicdown_final.zip` locally.
- [ ] Initialize a Git repository and push to GitHub:
  ```bash
  git init
  git add .
  git commit -m "Initial commit MusicDown with licensing and Ko-fi"
  gh repo create yourusername/musicdown --public --source=. --push
  ```

## 2) Generate RSA keys (server)
- [ ] On your local machine (or server), generate keys (DO NOT commit private key):
  ```bash
  openssl genpkey -algorithm RSA -out license_private.pem -pkeyopt rsa_keygen_bits:4096
  openssl rsa -pubout -in license_private.pem -out license_public.pem
  ```
- [ ] Upload `license_private.pem` to your server (e.g., Render secrets or /run/secrets/) and set environment var `LICENSE_PRIVATE_KEY_PATH` to its path.
- [ ] Copy `license_public.pem` to `client/public.pem` in the project (or embed in compiled exe).

## 3) Configure environment variables (Render / Railway / VPS)
Set the following env vars in your hosting provider:
- DJANGO_SECRET_KEY: a random secret string
- DEBUG=False
- ALLOWED_HOSTS=yourdomain.com
- STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY (if using Stripe for other payments)
- LICENSE_PRIVATE_KEY_PATH=/run/secrets/license_private.pem
- PREPACKAGED_EXE_URL=https://ko-fi.com/downloaderplaylist
- KO_FI_WEBHOOK_SECRET= (optional; set if Ko-fi provides signature token)
- CELERY_BROKER_URL=redis://... (if using Celery)
- EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS

## 4) Deploy to Render (recommended beginner-friendly)
- [ ] Create a Render account.
- [ ] Create a Web Service -> Link your GitHub repo -> Build Command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
- [ ] Start Command: `gunicorn musicdown.wsgi --log-file -`
- [ ] Add Environment Variables (see above).
- [ ] Create a Redis instance on Render and set CELERY_BROKER_URL and CELERY_RESULT_BACKEND accordingly.
- [ ] Create a Worker service on Render: Start command: `celery -A musicdown worker --loglevel=info` and same env vars.

## 5) Email provider
- [ ] Configure SMTP (SendGrid/Mailgun/Gmail app password).
- [ ] Test email sending using Django shell:
  ```bash
  python manage.py shell
  from downloader.utils_email import send_license_email
  send_license_email('your@email.com','test','LICENSE_CONTENT', download_url='https://ko-fi.com/downloaderplaylist')
  ```

## 6) Ko-fi setup (real)
- [ ] Create a Ko-fi account and product for the EXE at https://ko-fi.com/downloaderplaylist.
- [ ] In Ko-fi Dashboard -> Integrations -> Webhooks, add your webhook URL:
  `https://yourdomain.com/webhook/kofi/`
- [ ] If Ko-fi gives a webhook secret/signature, paste it into KO_FI_WEBHOOK_SECRET env var.
- [ ] Test a payment or use Ko-fi test mode to send a webhook. Alternatively test using curl:
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{"email":"test@example.com","amount":5,"name":"Tester"}' https://yourdomain.com/webhook/kofi/
  ```

## 7) Create admin user and test flow
- [ ] Run migrations and create superuser:
  ```bash
  python manage.py migrate
  python manage.py createsuperuser
  ```
- [ ] Login to /admin/ and verify models (LicenseKey, Activation, Plans).
- [ ] Simulate webhook or buy through Ko-fi and verify you receive license email with link.
- [ ] Test client activation with the license. Use activate_cli or the license attached.

## 8) Build client executables (locally)
- [ ] Install PyInstaller locally and build:
  ```bash
  pip install pyinstaller
  pyinstaller --onefile --add-data "client/public.pem:." client/main.py
  pyinstaller --onefile --add-data "client/public.pem:." client/activate_cli.py
  ```
- [ ] Upload the built `main` or `main.exe` to a safe hosting (S3, GitHub Releases, or Render static) and set PREPACKAGED_EXE_URL accordingly.
- [ ] In Ko-fi email you can include the PREPACKAGED_EXE_URL for users to download.

## 9) Final checks
- [ ] Ensure LICENSE_PRIVATE_KEY_PATH is set and file readable by app.
- [ ] Ensure mailbox can send emails.
- [ ] Monitor space in MEDIA_ROOT and set up cleanup cron (`python manage.py cleanup_downloads --days 7`).

## 10) Legal
- [ ] Update Terms & Conditions and Privacy Policy about HWID, email collection and license revocation.
- [ ] Ensure downloaded content complies with copyright rules.
