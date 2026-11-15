"""
What the App Store upload depends on, held in place.

Nothing here can be seen until an archive is uploaded or a reviewer opens
the app, which is the most expensive place to find it: a missing export
declaration asks a question on every upload, an app-bound-domains flag with
no domain list blocks sign-in entirely, and a hosted sign-in redirect walks
the WebView out of the app.
"""
import plistlib
from pathlib import Path

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
IOS = FRONTEND / "ios" / "App"


def _info():
    return plistlib.loads((IOS / "App" / "Info.plist").read_bytes())


def test_the_export_compliance_answer_is_declared():
    assert _info()["ITSAppUsesNonExemptEncryption"] is False


def test_the_three_languages_are_declared_and_the_phone_is_portrait():
    info = _info()
    assert set(info["CFBundleLocalizations"]) == {"en", "tr", "de"}
    assert info["UISupportedInterfaceOrientations"] == ["UIInterfaceOrientationPortrait"]


def test_a_privacy_manifest_ships_in_the_app_and_declares_no_tracking():
    manifest = plistlib.loads((IOS / "App" / "PrivacyInfo.xcprivacy").read_bytes())
    assert manifest["NSPrivacyTracking"] is False
    assert all(d["NSPrivacyCollectedDataTypeTracking"] is False
               for d in manifest["NSPrivacyCollectedDataTypes"])
    project = (IOS / "App.xcodeproj" / "project.pbxproj").read_text()
    assert "PrivacyInfo.xcprivacy in Resources" in project, "the file exists but is not in the build"


def test_nothing_limits_the_webview_to_an_empty_domain_list():
    """The flag without WKAppBoundDomains blocks Clerk and the API."""
    config = (FRONTEND / "capacitor.config.ts").read_text()
    code = "\n".join(line for line in config.splitlines() if not line.strip().startswith("//"))
    assert "limitsNavigationsToAppBoundDomains" not in code or "WKAppBoundDomains" in _info()


def test_the_native_shell_signs_in_inside_the_app_without_social_buttons():
    app = (FRONTEND / "src" / "App.jsx").read_text()
    gate = app[app.index("function SignedOutGate"):app.index("function ProtectedRoute")]
    assert "isNativeApp()" in gate and "<SignIn" in gate and "withSignUp" in gate
    main = (FRONTEND / "src" / "main.jsx").read_text()
    assert "appearance={isNativeApp() ? NATIVE_APPEARANCE : undefined}" in main
    assert "socialButtons" in main
