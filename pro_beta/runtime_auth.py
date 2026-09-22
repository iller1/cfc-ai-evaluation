from __future__ import annotations

import os

from pro_beta.api import MissingIdentityVerifier
from pro_beta.clerk_verifier import ClerkConfig, ClerkIdentityVerifier


def build_identity_verifier_from_environment():
    provider = os.environ.get("PRO_BETA_AUTH_PROVIDER", "").strip().lower()
    if provider != "clerk":
        return MissingIdentityVerifier()

    issuer = os.environ.get("CLERK_ISSUER", "").strip()
    jwks_url = os.environ.get("CLERK_JWKS_URL", "").strip()
    parties = tuple(
        item.strip()
        for item in os.environ.get("CLERK_AUTHORIZED_PARTIES", "").split(",")
        if item.strip()
    )
    return ClerkIdentityVerifier(
        ClerkConfig(
            issuer=issuer,
            jwks_url=jwks_url,
            authorized_parties=parties,
        )
    )
