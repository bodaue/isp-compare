import pytest

from tests.fixtures.users import *  # noqa: F403
from tests.fixtures.clients import *  # noqa: F403
from tests.fixtures.common import *  # noqa: F403
from tests.fixtures.config import *  # noqa: F403
from tests.fixtures.db import *  # noqa: F403
from tests.fixtures.providers import *  # noqa: F403
from tests.fixtures.reviews import *  # noqa: F403
from tests.fixtures.search_history import *  # noqa: F403
from tests.fixtures.tariffs import *  # noqa: F403

pytestmark = pytest.mark.asyncio
