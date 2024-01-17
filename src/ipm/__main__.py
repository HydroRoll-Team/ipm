from .api import install, extract, build
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        prog="ipm", description="Infini 包管理器", exit_on_error=False
    )
    subparsers = parser.add_subparsers(
        title="指令", dest="command", metavar="<operation>"
    )

    # Install command
    install_parser = subparsers.add_parser("install", help="安装一个 Infini 规则包到此计算机")
    install_parser.add_argument("uri", help="Infini 包的统一资源标识符")
    install_parser.add_argument("--index", help="IPM 包服务器")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="解压缩 Infini 包")
    extract_parser.add_argument("package", help="Infini 包路径")
    extract_parser.add_argument(
        "--dist",
        default=".",
        help="特定的解压路径 (默认: 当前工作目录)",
    )

    # Build command
    build_parser = subparsers.add_parser("build", help="打包 Infini 规则包")
    build_parser.add_argument("package", nargs="?", help="Infini 库路径", default=".")

    args = parser.parse_args(sys.argv[1:] or ["-h"])

    if args.command == "install":
        install(args.uri, args.index, echo=True)
    elif args.command == "extract":
        extract(args.package, args.dist)
    elif args.command == "build":
        build(args.package)


if __name__ == "__main__":
    main()
