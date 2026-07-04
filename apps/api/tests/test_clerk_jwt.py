from unittest.mock import MagicMock, patch

from auth.clerk_jwt import decode_clerk_token, resolve_clerk_issuer


def test_resolve_clerk_issuer_from_config():
    with patch("auth.clerk_jwt.settings") as mock_settings:
        mock_settings.clerk_jwt_issuer = "https://test.clerk.accounts.dev"
        mock_settings.clerk_secret_key = "sk_test"
        # Reset module cache
        import auth.clerk_jwt as clerk_jwt_module

        clerk_jwt_module._RESOLVED_ISSUER = None
        assert resolve_clerk_issuer() == "https://test.clerk.accounts.dev"


def test_decode_clerk_token_returns_none_for_invalid_token():
    with patch("auth.clerk_jwt.resolve_clerk_issuer", return_value="https://test.clerk.accounts.dev"), patch(
        "auth.clerk_jwt._get_jwks", return_value={"keys": []}
    ):
        assert decode_clerk_token("not-a-jwt") is None


def test_get_optional_clerk_user_id_with_valid_payload():
    import asyncio

    from auth.dependencies import get_optional_clerk_user_id

    with patch(
        "auth.dependencies.decode_clerk_token",
        return_value={"sub": "user_abc123"},
    ):
        result = asyncio.run(get_optional_clerk_user_id(authorization="Bearer fake-token"))
        assert result == "user_abc123"
