"""What app.services.cody relies on from the OpenRouter SDK.

CI never exercises the real client: tests/test_cody_spend.py monkeypatches
`app.api.cody.get_reply`, so the call, the response shape and the exception
classes are all unverified by the suite. An SDK bump could rename any of
them and ship green -- `openrouter_errors.OpenRouterError` in particular is
resolved only when the `except` clause is *evaluated*, which happens on a
real API failure and nowhere else.

These tests pin that contract without touching the network. They are not
tests of the SDK; they are tests of the assumptions this codebase makes
about it, so each failure points at one line in app/services/cody.py or
app/api/cody.py that would need changing.
"""

import inspect

import pytest
from sqlalchemy import select

from app.models import User
from app.services import cody as cody_service


class _FakeMessage:
    def __init__(self, content):
        self.content = content


class _FakeChoice:
    def __init__(self, content):
        self.message = _FakeMessage(content)


class _FakeUsage:
    def __init__(self, prompt_tokens=11, completion_tokens=22, cost=0.000123):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.cost = cost


class _FakeTextPart:
    """A multi-part content entry, as `type`/`text` attributes.

    get_reply keeps only parts whose `type` is "text" -- see the
    `getattr(part, "type", None) == "text"` filter it applies.
    """

    def __init__(self, text, type="text"):
        self.text = text
        self.type = type


class _FakeResponse:
    def __init__(self, content, usage=None):
        self.choices = [_FakeChoice(content)]
        self.usage = usage


class _FakeChat:
    def __init__(self, response, recorder):
        self._response = response
        self._recorder = recorder

    async def send_async(self, **kwargs):
        self._recorder.append(kwargs)
        return self._response


class _FakeClient:
    """Stands in for `OpenRouter`, including its async-context-manager use."""

    def __init__(self, response, recorder, **init_kwargs):
        self.chat = _FakeChat(response, recorder)
        self.init_kwargs = init_kwargs
        self.entered = False
        self.exited = False

    async def __aenter__(self):
        self.entered = True
        return self

    async def __aexit__(self, *exc):
        self.exited = True
        return False


def _install_fake(monkeypatch, response):
    """Replace the OpenRouter symbol get_reply closes over.

    Patched on `app.services.cody`, not on the `openrouter` package: the
    module imported the class by name at import time, so that is the
    binding the function actually uses.
    """
    recorder: list[dict] = []
    created: list[_FakeClient] = []

    def factory(**kwargs):
        client = _FakeClient(response, recorder, **kwargs)
        created.append(client)
        return client

    monkeypatch.setattr(cody_service, "OpenRouter", factory)
    return recorder, created


async def _a_user(db_session, username: str) -> User:
    return (
        await db_session.execute(select(User).where(User.username == username))
    ).scalar_one()


class TestResponseShape:
    """get_reply's reading of the response object."""

    async def test_plain_string_content_is_returned_as_is(
        self, test_user, db_session, monkeypatch
    ):
        monkeypatch.setattr(cody_service.get_settings(), "openrouter_api_key", "or-test-key")
        _install_fake(monkeypatch, _FakeResponse("Binary is base 2.", _FakeUsage()))
        user = await _a_user(db_session, test_user["data"]["username"])

        reply = await cody_service.get_reply(db_session, user, [], "what is binary?")

        assert reply.content == "Binary is base 2."

    async def test_list_content_is_joined_from_text_parts_only(
        self, test_user, db_session, monkeypatch
    ):
        """The provider may answer with a list of content parts instead of a
        string. get_reply concatenates the `text` of the parts whose `type`
        is "text" and drops anything else."""
        monkeypatch.setattr(cody_service.get_settings(), "openrouter_api_key", "or-test-key")
        content = [
            _FakeTextPart("Binary "),
            _FakeTextPart("ignored", type="image"),
            _FakeTextPart("is base 2."),
        ]
        _install_fake(monkeypatch, _FakeResponse(content, _FakeUsage()))
        user = await _a_user(db_session, test_user["data"]["username"])

        reply = await cody_service.get_reply(db_session, user, [], "what is binary?")

        assert reply.content == "Binary is base 2."

    async def test_usage_fields_are_read_by_name(
        self, test_user, db_session, monkeypatch
    ):
        """prompt_tokens / completion_tokens / cost. `cost` is OpenRouter's
        own dollar figure and feeds the spend cap in app.api.cody, so a
        rename here would silently disable that cap."""
        monkeypatch.setattr(cody_service.get_settings(), "openrouter_api_key", "or-test-key")
        usage = _FakeUsage(prompt_tokens=137, completion_tokens=42, cost=0.0009)
        _install_fake(monkeypatch, _FakeResponse("hi", usage))
        user = await _a_user(db_session, test_user["data"]["username"])

        reply = await cody_service.get_reply(db_session, user, [], "hi")

        assert reply.prompt_tokens == 137
        assert reply.completion_tokens == 42
        assert reply.cost_usd == 0.0009

    async def test_absent_usage_degrades_to_none_rather_than_raising(
        self, test_user, db_session, monkeypatch
    ):
        monkeypatch.setattr(cody_service.get_settings(), "openrouter_api_key", "or-test-key")
        _install_fake(monkeypatch, _FakeResponse("hi", None))
        user = await _a_user(db_session, test_user["data"]["username"])

        reply = await cody_service.get_reply(db_session, user, [], "hi")

        assert reply.prompt_tokens is None
        assert reply.completion_tokens is None
        assert reply.cost_usd is None

    async def test_empty_content_becomes_an_empty_string(
        self, test_user, db_session, monkeypatch
    ):
        monkeypatch.setattr(cody_service.get_settings(), "openrouter_api_key", "or-test-key")
        _install_fake(monkeypatch, _FakeResponse(None, _FakeUsage()))
        user = await _a_user(db_session, test_user["data"]["username"])

        reply = await cody_service.get_reply(db_session, user, [], "hi")

        assert reply.content == ""


class TestCallShape:
    """How get_reply calls the SDK: the context manager and the kwargs."""

    async def test_the_client_is_used_as_an_async_context_manager(
        self, test_user, db_session, monkeypatch
    ):
        monkeypatch.setattr(cody_service.get_settings(), "openrouter_api_key", "or-test-key")
        _, created = _install_fake(monkeypatch, _FakeResponse("hi", _FakeUsage()))
        user = await _a_user(db_session, test_user["data"]["username"])

        await cody_service.get_reply(db_session, user, [], "hi")

        assert len(created) == 1
        assert created[0].entered, "get_reply must enter the client's async context"
        assert created[0].exited, "and leave it, so the HTTP session is closed"
        assert created[0].init_kwargs == {"api_key": "or-test-key"}

    async def test_send_async_is_called_with_the_keywords_we_pass(
        self, test_user, db_session, monkeypatch
    ):
        monkeypatch.setattr(cody_service.get_settings(), "openrouter_api_key", "or-test-key")
        recorder, _ = _install_fake(monkeypatch, _FakeResponse("hi", _FakeUsage()))
        user = await _a_user(db_session, test_user["data"]["username"])

        await cody_service.get_reply(db_session, user, [], "what is a pointer?")

        assert len(recorder) == 1
        call = recorder[0]
        assert set(call) == {"model", "messages", "max_tokens"}
        assert call["max_tokens"] == 1024
        # system prompt first, the user's new message last
        assert call["messages"][0]["role"] == "system"
        assert call["messages"][-1] == {
            "role": "user",
            "content": "what is a pointer?",
        }


class TestSdkSurfaceExists:
    """The SDK symbols this codebase names, checked against the installed
    package rather than a fake -- this is the half a mock cannot prove."""

    def test_openrouter_class_is_an_async_context_manager(self):
        from openrouter import OpenRouter

        assert hasattr(OpenRouter, "__aenter__"), "get_reply uses `async with OpenRouter(...)`"
        assert hasattr(OpenRouter, "__aexit__")

    def test_the_constructor_accepts_api_key(self):
        from openrouter import OpenRouter

        parameters = inspect.signature(OpenRouter.__init__).parameters
        assert "api_key" in parameters, sorted(parameters)

    def test_chat_send_async_exists_and_takes_our_keywords(self):
        from openrouter import OpenRouter

        # The chat namespace is built per-instance, so introspect an instance
        # rather than the class. Constructing the client performs no I/O --
        # the key is a placeholder and nothing is ever sent with it.
        client = OpenRouter(api_key="or-not-a-real-key")
        assert hasattr(client, "chat")
        assert hasattr(client.chat, "send_async")

        parameters = inspect.signature(client.chat.send_async).parameters
        for name in ("model", "messages", "max_tokens"):
            assert name in parameters, f"{name} missing; have {sorted(parameters)}"

    @pytest.mark.parametrize("name", ["OpenRouterError", "NoResponseError"])
    def test_the_exception_classes_app_api_cody_catches_are_resolvable(self, name):
        """app/api/cody.py names these in an `except (...)` tuple, which
        Python evaluates only when an exception reaches it -- i.e. on a real
        API failure. They are also lazily exported, so they do not appear in
        dir(openrouter.errors); getattr is the check that means anything.
        """
        from openrouter import errors

        exc = getattr(errors, name, None)
        assert exc is not None, f"openrouter.errors.{name} is gone"
        assert isinstance(exc, type) and issubclass(exc, BaseException)
