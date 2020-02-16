from mysync import MySync
import argparse


def init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="NextCloud folder synchronize CLI client.",
                                     description='Options for NextCloud sync client')
    parser.add_argument("--url", dest="url", type=str)
    parser.add_argument("--login", dest="login", type=str)
    parser.add_argument("--password", dest="password", type=str)
    parser.add_argument("--days-threshold", type=int)
    parser.add_argument("--remove-local", dest="remove_local", action="store_true")
    parser.add_argument("--local-dir", dest="local_dir", type=str, required=True)
    parser.add_argument("--remote-dir", dest="remote_dir", type=str)
    parser.add_argument("--exclusions", dest="exclusions", nargs="+", type=str)
    parser.add_argument("--log-file", dest="log_file", type=argparse.FileType('w'))
    return parser


if __name__ == "__main__":
    args = init_parser().parse_args()
    try:
        sync_client = MySync(url=args.url,
                             days_threshold=args.days_threshold,
                             remove_locally=args.remove_local,
                             log_file=args.log_file)
        sync_client.connect(login=args.login, password=args.password)
        sync_client.sync(local_dir=args.local_dir, remote_dir=args.remote_dir, exclude_items=args.exclusions)
    except:
        exit(1)
    else:
        exit(0)
