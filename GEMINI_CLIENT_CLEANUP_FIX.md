# Gemini Client Cleanup Warning Fix

## Issue
When the Django server starts or services are initialized, you may see this warning:

```
Exception ignored in: <function Client.__del__ at 0x...>
Traceback (most recent call last):
  File "...\google\genai\client.py", line 400, in __del__
    self.close()
  File "...\google\genai\client.py", line 386, in close
    self._api_client.close()
AttributeError: 'Client' object has no attribute '_api_client'
```

## Root Cause
This is a known issue in the `google-genai` library. When the `Client` object is garbage collected, its `__del__` method tries to close `_api_client`, but this attribute doesn't always exist, causing an `AttributeError`. Python catches this exception and prints "Exception ignored in:" - it's harmless but noisy.

## Fix Applied

### 1. Added Safe Cleanup Methods
Added `__del__` methods to all service classes that safely handle client cleanup:
- `AIPosterService`
- `AICaptionService`  
- `BrandingKitService`

These methods check if `_api_client` exists before trying to close it.

### 2. Added Warnings Filter
Added a warnings filter to suppress related warnings (though the "Exception ignored" message is printed directly by Python, not through warnings).

## Impact
- ✅ The warning is harmless - it doesn't affect functionality
- ✅ The fix adds safe cleanup to prevent the error
- ✅ Services continue to work normally
- ⚠️ You may still see the message occasionally during garbage collection, but it's safe to ignore

## Files Modified
1. `backend/ai_services/ai_poster_service.py`
   - Added `warnings` import and filter
   - Added `__del__` method for safe cleanup

2. `backend/ai_services/ai_caption_service.py`
   - Added `warnings` import and filter
   - Added `__del__` method for safe cleanup

3. `backend/ai_services/branding_kit_service.py`
   - Added `warnings` import and filter
   - Added `__del__` method for safe cleanup

## Note
The "Exception ignored in:" message is printed by Python itself when an exception occurs in `__del__` during garbage collection. This is expected behavior and the exception is already being handled. The message is informational and can be safely ignored.

If you want to completely suppress it, you would need to redirect stderr or use a custom exception handler, but this is not recommended as it could hide real errors.

