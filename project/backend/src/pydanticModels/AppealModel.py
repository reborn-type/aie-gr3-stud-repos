from pydantic import BaseModel, ConfigDict, Field

class AppealCreateModel(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Не могу войти в приложение",
                "text": "Face ID крутится и возвращает на экран логина. Пароль верный.",
            }
        }
    )

    title: str = Field(
        ...,
        min_length=1,
        description="Краткий заголовок обращения пользователя",
        examples=["Не могу войти в приложение"],
    )
    text: str = Field(
        ...,
        min_length=1,
        description="Полный текст обращения пользователя",
        examples=["Face ID крутится и возвращает на экран логина. Пароль верный."],
    )


class AppealModel(AppealCreateModel):
    id: int = Field(..., ge=1, description="Уникальный идентификатор обращения", examples=[1])

class ResponseModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Не могу войти в приложение",
                "text": "Face ID крутится и возвращает на экран логина. Пароль верный.",
                "department": "APP_LOGIN",
                "percent_of_confidence": 87.65,
            }
        },
    )

    id: int = Field(..., ge=1, description="Уникальный идентификатор обращения", examples=[1])
    title: str = Field(..., description="Заголовок обращения", examples=["Не могу войти в приложение"])
    text: str = Field(
        ...,
        description="Содержание обращения",
        examples=["Face ID крутится и возвращает на экран логина. Пароль верный."],
    )
    department: str = Field(
        ...,
        description="Предсказанный моделью отдел или класс обращения",
        examples=["APP_LOGIN"],
    )
    percent_of_confidence: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Уверенность модели в процентах, округленная до двух знаков после запятой",
        examples=[87.65],
    )
    
