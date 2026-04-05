from src.infrastructure.http.user_agent_parser import parse_user_agent


def test_parse_mobile_safari() -> None:
    ua = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 "
        "Mobile/15E148 Safari/604.1"
    )
    info = parse_user_agent(ua)
    assert info.device_type == "mobile"
    assert info.os_name == "ios"
    assert info.browser_name == "safari"


def test_parse_desktop_chrome() -> None:
    ua = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
    info = parse_user_agent(ua)
    assert info.device_type == "desktop"
    assert info.os_name == "windows"
    assert info.browser_name == "chrome"
