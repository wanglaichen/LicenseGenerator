#!/usr/bin/env python3
import argparse
import json
import sys

from client.register_client import RegisterApiClient


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--base-url",
        default=None,
        help="服务地址，默认 http://127.0.0.1:9212",
    )

    parser = argparse.ArgumentParser(description="RegMachine Web API 命令行客户端")
    parser.add_argument(
        "--base-url",
        default=None,
        help="服务地址，默认 http://127.0.0.1:9212",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("info", parents=[common], help="查看 API 说明")
    subparsers.add_parser("health", parents=[common], help="检查服务状态")

    machine_md5_parser = subparsers.add_parser("machine-md5", parents=[common], help="生成机器码 MD5")
    machine_md5_parser.add_argument("--machine-code", required=True, help="机器码")
    machine_md5_parser.add_argument(
        "--md5-length",
        type=int,
        default=None,
        help="MD5 截断长度，省略则使用机器码字节数；传 0 可复现硬盘序列号为空的旧版行为",
    )

    register_parser = subparsers.add_parser("register-code", parents=[common], help="生成激活码")
    register_parser.add_argument("--sn", required=True, help="注册码输入")
    register_parser.add_argument("--key", default=None, help="8 字节密钥，省略则使用服务端默认值")

    generate_parser = subparsers.add_parser("generate", parents=[common], help="同时生成 MD5 与激活码")
    generate_parser.add_argument("--machine-code", required=True, help="机器码")
    generate_parser.add_argument("--sn", required=True, help="注册码输入")
    generate_parser.add_argument("--key", default=None, help="8 字节密钥，省略则使用服务端默认值")
    generate_parser.add_argument("--md5-length", type=int, default=None, help="MD5 截断长度")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    client = RegisterApiClient(base_url=args.base_url)

    try:
        if args.command == "info":
            result = client.info()
        elif args.command == "health":
            result = client.health()
        elif args.command == "machine-md5":
            result = client.machine_md5(
                machine_code=args.machine_code,
                md5_length=args.md5_length,
            )
        elif args.command == "register-code":
            result = client.register_code(sn=args.sn, key=args.key)
        else:
            result = client.generate(
                machine_code=args.machine_code,
                sn=args.sn,
                key=args.key,
                md5_length=args.md5_length,
            )
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
