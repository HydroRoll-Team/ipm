from ipm.api import build, extract, install


def test_build():
    build("C:\\Users\\fu050\\Desktop\\coc")


def test_extract():
    build("C:\\Users\\fu050\\Desktop\\coc")
    extract("C:\\Users\\fu050\\Desktop\\coc\\dist\\coc-0.1.0-alpha.1.ipk")


def test_install():
    build("C:\\Users\\fu050\\Desktop\\coc")
    install("C:\\Users\\fu050\\Desktop\\coc\\dist\\coc-0.1.0-alpha.1.ipk")
