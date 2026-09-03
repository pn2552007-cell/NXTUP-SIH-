import pytest
import sys

if __name__ == "__main__":
    exit_code = pytest.main(["tests/", "-W", "ignore", "-v"])
    sys.exit(exit_code)
