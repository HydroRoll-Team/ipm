from .api import install, extract, build
import argparse


def main():
    parser = argparse.ArgumentParser(description="Infini Package Manager")
    subparsers = parser.add_subparsers(title="subcommands", dest="command")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install a package")
    install_parser.add_argument("uri", help="Path or name of the package")
    install_parser.add_argument("--index", help="Specify a custom package index")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract a package")
    extract_parser.add_argument(
        "package", help="Path or name of the package to extract"
    )
    extract_parser.add_argument(
        "--dist",
        default=".",
        help="Specify extraction directory (default: current directory)",
    )

    # Build command
    build_parser = subparsers.add_parser("build", help="打包 Infini 规则包")
    build_parser.add_argument(
        "package", nargs="?", help="Path or name of the package to build", default="."
    )

    args = parser.parse_args()

    if args.command == "install":
        install(args.uri, args.index)
    elif args.command == "extract":
        extract(args.package, args.dist)
    elif args.command == "build":
        build(args.package)


if __name__ == "__main__":
    main()
