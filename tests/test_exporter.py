import json
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock

import pytest

from app.exporter import parse_xml, export_to_redis


def test_parse_subdomains(tmp_path):
    xml = """
    <config>
        <subdomains>
            <subdomain>https://example.com</subdomain>
            <subdomain>https://test.com</subdomain>
        </subdomains>
    </config>
    """

    file = tmp_path / "test.xml"
    file.write_text(xml)

    subdomains, cookies = parse_xml(file)

    assert subdomains == [
        "https://example.com",
        "https://test.com"
    ]

    assert cookies == {}


def test_parse_cookies(tmp_path):
    xml = """
    <config>
        <cookies>
            <cookie name="test" host="amazon">value123</cookie>
        </cookies>
    </config>
    """

    file = tmp_path / "test.xml"
    file.write_text(xml)

    subdomains, cookies = parse_xml(file)

    assert cookies == {
        "cookie:test:amazon": "value123"
    }

    assert subdomains == []


def test_missing_cookie_attributes(tmp_path):
    xml = """
    <config>
        <cookies>
            <cookie name="test">value123</cookie>
        </cookies>
    </config>
    """

    file = tmp_path / "test.xml"
    file.write_text(xml)

    with pytest.raises(ValueError):
        parse_xml(file)


def test_invalid_xml(tmp_path):
    file = tmp_path / "invalid.xml"
    file.write_text("<config><subdomains></config>")

    with pytest.raises(ET.ParseError):
        parse_xml(file)


def test_export_to_redis(tmp_path):
    xml = """
    <config>
        <subdomains>
            <subdomain>https://example.com</subdomain>
        </subdomains>
        <cookies>
            <cookie name="test" host="amazon">value123</cookie>
        </cookies>
    </config>
    """

    file = tmp_path / "test.xml"
    file.write_text(xml)

    mock_redis = MagicMock()

    keys = export_to_redis(file, mock_redis)

    mock_redis.mset.assert_called_once_with({
        "subdomains": json.dumps(["https://example.com"]),
        "cookie:test:amazon": "value123"
    })

    assert keys == [
        "subdomains",
        "cookie:test:amazon"
    ]