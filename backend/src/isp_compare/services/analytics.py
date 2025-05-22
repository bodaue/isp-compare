from collections import Counter

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.user_analytics import UserAnalytics
from isp_compare.schemas.analytics import AnalyticsStats


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_analytics_stats(self) -> AnalyticsStats:
        total_sessions_result = await self._session.execute(
            select(func.count(UserAnalytics.id))
        )
        total_sessions = total_sessions_result.scalar() or 0

        if total_sessions == 0:
            return AnalyticsStats(
                total_sessions=0,
                goal_completion_rate=0.0,
                average_clicks_to_goal=0.0,
                average_session_duration=0.0,
                most_common_path=[],
                drop_off_points={},
            )

        # Сессии с достигнутой целью
        completed_sessions_result = await self._session.execute(
            select(func.count(UserAnalytics.id)).where(
                UserAnalytics.goal_reached.is_(True)
            )
        )
        completed_sessions = completed_sessions_result.scalar() or 0

        # Среднее количество кликов до цели
        avg_clicks_result = await self._session.execute(
            select(func.avg(UserAnalytics.total_clicks)).where(
                UserAnalytics.goal_reached.is_(True)
            )
        )
        avg_clicks = avg_clicks_result.scalar() or 0.0

        # Средняя продолжительность сессии
        avg_duration_result = await self._session.execute(
            select(func.avg(UserAnalytics.session_duration)).where(
                UserAnalytics.session_duration.isnot(None)
            )
        )
        avg_duration = avg_duration_result.scalar() or 0.0

        # Получаем все пути пользователей
        user_paths_result = await self._session.execute(
            select(UserAnalytics.user_path).where(UserAnalytics.user_path.isnot(None))
        )
        user_paths = [row[0] for row in user_paths_result.fetchall()]

        # Самый популярный путь
        path_strings = [" -> ".join(path) for path in user_paths if path]
        most_common_path = []
        if path_strings:
            most_common = Counter(path_strings).most_common(1)
            if most_common:
                most_common_path = most_common[0][0].split(" -> ")

        # Точки отката (где пользователи чаще всего уходят)
        drop_off_points = {}
        for path in user_paths:
            if path and len(path) > 1:
                last_page = path[-1]
                drop_off_points[last_page] = drop_off_points.get(last_page, 0) + 1

        goal_completion_rate = (
            (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0.0
        )

        return AnalyticsStats(
            total_sessions=total_sessions,
            goal_completion_rate=round(goal_completion_rate, 2),
            average_clicks_to_goal=round(avg_clicks, 1),
            average_session_duration=round(avg_duration / 1000, 1)
            if avg_duration
            else 0.0,  # конвертируем в секунды
            most_common_path=most_common_path,
            drop_off_points=dict(
                sorted(drop_off_points.items(), key=lambda x: x[1], reverse=True)[:5]
            ),
        )
