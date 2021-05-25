import topgg


def test_topgg_validates_version() -> None:
    assert topgg.__version__.split(".") == [
        str(getattr(topgg.version_info, i)) for i in ("major", "minor", "micro")
    ]
