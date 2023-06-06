import conftest

def test_login(test_client, captured_templates):
    response = test_client.get("/")

    assert len(captured_templates) == 1

    template, context = captured_templates[0]

    assert template.name == "login.html"
