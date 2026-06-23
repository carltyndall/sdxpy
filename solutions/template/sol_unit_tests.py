"""Solution: Unit Tests exercise.

Write unit tests for template expansion using pytest.
Tests cover the Env class, individual handlers, and full end-to-end expansion.
"""

from bs4 import BeautifulSoup

from env import Env
from expander import Expander


# --- Env tests ---

def test_env_find_simple():
    env = Env({"name": "Alice"})
    assert env.find("name") == "Alice"


def test_env_find_missing():
    env = Env({"name": "Alice"})
    assert env.find("missing") is None


def test_env_push_pop():
    env = Env({"outer": 1})
    env.push({"inner": 2})
    assert env.find("outer") == 1
    assert env.find("inner") == 2
    env.pop()
    assert env.find("inner") is None
    assert env.find("outer") == 1


def test_env_stack_shadowing():
    env = Env({"x": "global"})
    env.push({"x": "local"})
    assert env.find("x") == "local"
    env.pop()
    assert env.find("x") == "global"


# --- Variable substitution tests ---

def test_z_var_substitution():
    html = "<html><body><span z-var=\"name\"/></body></html>"
    doc = BeautifulSoup(html, "html.parser")
    expander = Expander(doc.find("html"), {"name": "Alice"})
    expander.walk()
    result = expander.getResult()
    assert "Alice" in result
    assert "UNDEF" not in result


def test_z_var_undefined():
    html = "<html><body><span z-var=\"missing\"/></body></html>"
    doc = BeautifulSoup(html, "html.parser")
    expander = Expander(doc.find("html"), {})
    expander.walk()
    assert "UNDEF" in expander.getResult()


# --- Loop tests ---

def test_z_loop_simple():
    html = (
        "<html><body><ul z-loop=\"item:names\">"
        "<li><span z-var=\"item\"/></li>"
        "</ul></body></html>"
    )
    doc = BeautifulSoup(html, "html.parser")
    expander = Expander(doc.find("html"), {"names": ["a", "b", "c"]})
    expander.walk()
    result = expander.getResult()
    assert "<li><span>a</span></li>" in result
    assert "<li><span>b</span></li>" in result
    assert "<li><span>c</span></li>" in result


def test_z_loop_empty():
    html = (
        "<html><body><ul z-loop=\"item:names\">"
        "<li><span z-var=\"item\"/></li>"
        "</ul></body></html>"
    )
    doc = BeautifulSoup(html, "html.parser")
    expander = Expander(doc.find("html"), {"names": []})
    expander.walk()
    result = expander.getResult()
    assert "<li>" not in result


# --- If tests ---

def test_z_if_true():
    html = "<html><body><div z-if=\"show\"><p>visible</p></div></body></html>"
    doc = BeautifulSoup(html, "html.parser")
    expander = Expander(doc.find("html"), {"show": True})
    expander.walk()
    assert "visible" in expander.getResult()


def test_z_if_false():
    html = "<html><body><div z-if=\"show\"><p>visible</p></div></body></html>"
    doc = BeautifulSoup(html, "html.parser")
    expander = Expander(doc.find("html"), {"show": False})
    expander.walk()
    assert "visible" not in expander.getResult()


# --- Edge case tests ---

def test_plain_text_passthrough():
    html = "<html><body><p>Hello world</p></body></html>"
    doc = BeautifulSoup(html, "html.parser")
    expander = Expander(doc.find("html"), {})
    expander.walk()
    assert "Hello world" in expander.getResult()


def test_nested_handlers():
    html = (
        "<html><body>"
        "<ul z-loop=\"item:stuff\">"
        "<li z-if=\"item\"><span z-var=\"item\"/></li>"
        "</ul>"
        "</body></html>"
    )
    doc = BeautifulSoup(html, "html.parser")
    expander = Expander(doc.find("html"), {"stuff": [True, False, True]})
    expander.walk()
    result = expander.getResult()
    # Li with True should appear; li with False should be suppressed.
    assert result.count("<li>") == 2
