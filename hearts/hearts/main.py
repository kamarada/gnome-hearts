from __future__ import annotations

import sys


def main() -> int:
    from .application import HeartsApplication

    app = HeartsApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
