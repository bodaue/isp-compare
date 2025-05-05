import pytest

from tests.fixtures.auth import *  # noqa: F403
from tests.fixtures.clients import *  # noqa: F403
from tests.fixtures.common import *  # noqa: F403
from tests.fixtures.config import *  # noqa: F403
from tests.fixtures.db import *  # noqa: F403

pytestmark = pytest.mark.asyncio
