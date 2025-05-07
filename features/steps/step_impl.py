from behave import given, when, then
import subprocess
import shlex
from pathlib import Path

@given('un repositorio con packfile "{path}"')
def step_impl(context, path):
    repo_path = Path(path)
    if not repo_path.exists():
        raise AssertionError(f"Fixture repo not found at {path}")

@when('ejecuto "{cmd}"')
def step_impl(context, cmd):
    context.result = subprocess.run(
        shlex.split(cmd),
        capture_output=True,
        text=True
    )

@then('el exit code es {code}')
def step_impl(context, code):
    assert context.result.returncode == int(code), f"Expected {code}, got {context.result.returncode}"

@then('la salida contiene "{msg}"')
def step_impl(context, msg):
    assert msg in context.result.stdout, f"'{msg}' not found in output: {context.result.stdout}"

