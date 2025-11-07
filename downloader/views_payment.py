from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.conf import settings
from django.contrib.auth.models import User
from .models import LicenseKey
from .utils_license_sign import sign_license_payload
from .utils_email import send_license_email
from django.utils import timezone
import secrets, json, hmac, hashlib
KO_FI_WEBHOOK_SECRET = getattr(settings, 'KO_FI_WEBHOOK_SECRET', None)
@csrf_exempt
def kofi_webhook(request):
    # Validate signature if secret set (Ko-fi may not provide signature header)
    if KO_FI_WEBHOOK_SECRET:
        sig_header = request.META.get('HTTP_X_KOFI_SIGNATURE') or request.META.get('HTTP_X_HUB_SIGNATURE')
        body = request.body
        if not sig_header:
            return HttpResponseForbidden("missing signature")
        expected = hmac.new(KO_FI_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig_header):
            return HttpResponseForbidden("invalid signature")
    try:
        payload = json.loads(request.body)
    except Exception:
        return HttpResponse(status=400)
    buyer_email = payload.get('email') or payload.get('payer_email') or payload.get('from_email')
    buyer_name = payload.get('name') or payload.get('from_name') or payload.get('payer_name')
    if not buyer_email:
        return JsonResponse({'error':'no_email'}, status=400)
    user, created = User.objects.get_or_create(username=buyer_email, defaults={'email': buyer_email, 'first_name': buyer_name or ''})
    if created:
        user.set_unusable_password(); user.save()
    # For Ko-fi payments we'll grant a premium license with unlimited downloads (while active)
    key = secrets.token_urlsafe(16).upper()
    lic = LicenseKey.objects.create(key=key, owner_email=buyer_email, plan_name='premium', max_devices=5, expires_at=None, active=True)
    payload_dict = {
        'key': lic.key,
        'plan': lic.plan_name,
        'max_devices': lic.max_devices,
        'hwids': [],
        'issued_at': timezone.now().isoformat(),
        'expires_at': None,
        'meta': {'owner': lic.owner_email}
    }
    signed_license = sign_license_payload(payload_dict)
    # Send email with link to EXE (option B) and license attached
    send_license_email(to_email=buyer_email, subject='Tu licencia MusicDown', license_str=signed_license, user=user, download_url=settings.PREPACKAGED_EXE_URL)
    return JsonResponse({'ok': True, 'key': lic.key})
