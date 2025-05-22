from pydantic import BaseModel, Field


class ClickData(BaseModel):
    timestamp: int
    element_type: str = Field(..., alias="elementType")
    element_text: str | None = Field(None, alias="elementText")
    page: str
    click_number: int = Field(..., alias="clickNumber")


class UserSessionData(BaseModel):
    session_id: str = Field(..., alias="sessionId")
    start_time: int = Field(..., alias="startTime")
    end_time: int | None = Field(None, alias="endTime")
    total_clicks: int = Field(..., alias="totalClicks")
    click_path: list[ClickData] = Field(..., alias="clickPath")
    user_path: list[str] = Field(..., alias="userPath")
    goal_reached: bool = Field(..., alias="goalReached")
    session_duration: int = Field(..., alias="sessionDuration")

    class Config:
        populate_by_name = True


class AnalyticsStats(BaseModel):
    total_sessions: int
    goal_completion_rate: float
    average_clicks_to_goal: float
    average_session_duration: float
    most_common_path: list[str]
    drop_off_points: dict[str, int]
