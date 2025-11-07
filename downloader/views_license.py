from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
import json, base64
from .models import LicenseKey, Activation
from .utils_license_sign import sign_license_payload
from django.views.decorators.http import require_POST
def get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
@csrf_exempt
@require_POST
def api_activate(request):
    data = request.POST
    key = data.get('key')
    hwid = data.get('hwid')
    if not key or not hwid:
        return HttpResponseBadRequest('key and hwid required')
    try:
        lic = LicenseKey.objects.get(key=key, active=True)
    except LicenseKey.DoesNotExist:
        return JsonResponse({'error':'invalid_key'}, status=400)
    if lic.expires_at and timezone.now() > lic.expires_at:
        return JsonResponse({'error':'expired'}, status=403)
    active_count = Activation.objects.filter(license=lic, revoked=False).count()
    if active_count >= lic.max_devices:
        return JsonResponse({'error':'device_limit'}, status=403)
    act = Activation.objects.create(license=lic, hwid=hwid, ip=get_client_ip(request))
    payload = {
        'key': lic.key,
        'plan': lic.plan_name,
        'max_devices': lic.max_devices,
        'hwids': [hwid],
        'issued_at': timezone.now().isoformat(),
        'expires_at': lic.expires_at.isoformat() if lic.expires_at else None,
        'meta': {'owner': lic.owner_email}
    }
    signed = sign_license_payload(payload)
    return JsonResponse({'license': signed})
@csrf_exempt
@require_POST
def api_validate(request):
    data = request.POST
    license_str = data.get('license')
    if not license_str:
        return HttpResponseBadRequest('license required')
    try:
        payload_b64, sig_b64 = license_str.split('.')
        payload = json.loads(base64.b64decode(payload_b64).decode())
        key = payload.get('key')
        lic = LicenseKey.objects.filter(key=key).first()
        if not lic or not lic.active:
            return JsonResponse({'valid': False, 'reason':'not_found'})
        if lic.expires_at and timezone.now() > lic.expires_at:
            return JsonResponse({'valid': False, 'reason':'expired'})
        return JsonResponse({'valid': True, 'payload': payload})
    except Exception as e:
        return JsonResponse({'valid': False, 'reason': str(e)})
