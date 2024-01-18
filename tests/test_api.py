from ipm import api


def test_new():
    api.new("test")


def test_build():
    api.new("test")
    api.build("test")


def test_extract():
    api.build("test")
    api.extract("test\\dist\\test-0.1.0.ipk")


def test_install():
    api.build("test")
    api.install("test\\dist\\test-0.1.0.ipk")
