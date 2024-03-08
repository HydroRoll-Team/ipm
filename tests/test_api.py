from ipm import api

import shutil


def test_new():
    api.new("test")
    shutil.rmtree("test", ignore_errors=True)


# def test_build():
#     api.new("test")
#     api.build("test")
#     shutil.rmtree("test", ignore_errors=True)


# def test_extract():
#     api.new("test")
#     api.build("test")
#     api.extract("./test/dist/test-0.1.0.ipk")
#     shutil.rmtree("test", ignore_errors=True)


# def test_install():
#     api.new("test")
#     api.build("test")
#     api.install("./test/dist/test-0.1.0.ipk")
#     shutil.rmtree("test", ignore_errors=True)


# def test_uninstall():
#     api.uninstall("test", is_confirm=True)


# def test_check():
#     api.new("test")
#     api.check("test")
#     shutil.rmtree("test", ignore_errors=True)
