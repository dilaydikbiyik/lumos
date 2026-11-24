"""
The Clerk token check: what it accepts, what it refuses, and what it costs.
"""
import asyncio
import time
from unittest.mock import patch

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from jwt.algorithms import RSAAlgorithm

from backend.middleware import verify_clerk as vc


@pytest.fixture
def keys(monkeypatch):
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk = RSAAlgorithm.to_jwk(private.public_key(), as_dict=True) | {"kid": "k1", "alg": "RS256", "use": "sig"}
    fetches = []

    async def fake_get(force=False):
        fetches.append(force)
        return {"keys": [jwk]}

    monkeypatch.setattr(vc, "_get_jwks", fake_get)
    return private, fetches


class _Req:
    def __init__(self, token):
        self.headers = {"authorization": f"Bearer {token}"}


def _run(token):
    async def go():
        with patch.object(vc, "_security", side_effect=lambda r: _creds(token)):
            return await vc.get_current_user(_Req(token))
    return asyncio.run(go())


async def _creds(token):
    from fastapi.security import HTTPAuthorizationCredentials
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def _token(private, **claims):
    body = {"sub": "user_abc", "exp": int(time.time()) + 600} | claims
    return jwt.encode(body, private, algorithm="RS256", headers={"kid": "k1"})


def test_a_valid_token_returns_its_subject(keys):
    private, _ = keys
    assert _run(_token(private)) == "user_abc"


@pytest.mark.parametrize("forge", ["hs256_with_public_key", "expired", "other_key", "none_alg"])
def test_forged_or_stale_tokens_are_refused_without_detail(keys, forge):
    private, _ = keys
    if forge == "expired":
        token = _token(private, exp=int(time.time()) - 10)
    elif forge == "other_key":
        other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        token = _token(other)
    elif forge == "none_alg":
        token = jwt.encode({"sub": "user_abc", "exp": int(time.time()) + 600}, None,
                           algorithm="none", headers={"kid": "k1"})
    else:
        token = jwt.encode({"sub": "user_abc", "exp": int(time.time()) + 600},
                           "public-key-as-secret", algorithm="HS256", headers={"kid": "k1"})
    with pytest.raises(HTTPException) as err:
        _run(token)
    assert err.value.status_code == 401 and err.value.detail == "Token verification failed"


def test_a_forged_token_cannot_make_the_server_refetch_keys_every_time(monkeypatch):
    calls = []

    class Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def get(self, url, timeout=5):
            calls.append(url)

            class R:
                def raise_for_status(self):
                    pass

                def json(self):
                    return {"keys": []}
            return R()

    monkeypatch.setattr(vc, "_jwks_cache", None)
    monkeypatch.setattr(vc.httpx, "AsyncClient", lambda: Client())
    asyncio.run(vc._get_jwks())
    for _ in range(20):
        asyncio.run(vc._get_jwks(force=True))
    assert len(calls) == 1
