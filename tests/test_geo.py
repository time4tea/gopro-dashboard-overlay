from gopro_overlay.geo import attrs_for_style, available_map_styles



def test_available_styles():
    styles = available_map_styles()
    assert len(styles) == 31
    assert "osm" in styles
    assert "cyclosm" in styles
    assert "tf-cycle" in styles
    assert "geo-osm-carto" in styles
    assert "local" in styles

def test_attrs_for_style():
    for style in available_map_styles():
        assert attrs_for_style(style) is not None


def test_example_style_attrs():
    assert attrs_for_style("tf-cycle")["url"] == "https://{subdomain}.tile.thunderforest.com/cycle/{z}/{x}/{y}.{ext}?apikey={api_key}"
    assert attrs_for_style("geo-osm-carto")["url"] == "https://maps.geoapify.com/v1/tile/osm-carto/{z}/{x}/{y}.png?apiKey={api_key}"