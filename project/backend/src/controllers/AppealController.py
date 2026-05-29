from fastapi import APIRouter, HTTPException, Request, status

from data.AppealData import get_appeals, get_appeal_by_id, create_appeal, delete_appeals, delete_appeal_by_id

from pydanticModels.AppealModel import AppealCreateModel, ResponseModel

from models.inference import predict_label

router = APIRouter(
    prefix="/appeals",
    tags=["Appeals"],
)


@router.get(
    "/",
    response_model=list[ResponseModel],
    summary="Получить список обращений",
    description="Возвращает все обращения, сохраненные в базе данных.",
    responses={
        200: {
            "description": "Список обращений успешно получен",
        },
    },
)
async def read_appeals():
    return get_appeals()

@router.get(
    "/{appeal_id}",
    response_model=ResponseModel,
    summary="Получить обращение по ID",
    description="Возвращает одно обращение по его уникальному идентификатору.",
    responses={
        200: {
            "description": "Обращение найдено",
        },
        404: {
            "description": "Обращение с указанным ID не найдено",
            "content": {
                "application/json": {
                    "example": {"detail": "Обращение не найдено"},
                }
            },
        },
    },
)
async def read_appeal_by_id(appeal_id: int):
    appeal = get_appeal_by_id(appeal_id)

    if appeal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Обращение не найдено",
        )

    return appeal

@router.post(
    "/predict",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
    summary="Создать и классифицировать обращение",
    description=(
        "Принимает заголовок и текст обращения, классифицирует его с помощью "
        "загруженной ML-модели, сохраняет обращение в базе данных и возвращает "
        "созданную запись с предсказанным отделом и процентом уверенности."
    ),
    responses={
        201: {
            "description": "Обращение успешно классифицировано и создано",
        },
        422: {
            "description": "Ошибка валидации входных данных",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "string_too_short",
                                "loc": ["body", "title"],
                                "msg": "String should have at least 1 character",
                                "input": "",
                            }
                        ]
                    },
                }
            },
        },
    },
)
async def add_appeal(appeal: AppealCreateModel, request: Request):
    prediction = predict_label(
        appeal.title,
        appeal.text,
        tokenizer=request.app.state.tokenizer,
        model=request.app.state.model,
    )

    created_appeal = create_appeal(
        title=appeal.title,
        text=appeal.text,
        department=prediction['pred_label'],
        percent_of_confidence=round(prediction["confidence"] * 100, 2),
    )

    return created_appeal

@router.delete(
    "/",
    summary="Удалить все обращения",
    description="Удаляет все обращения из базы данных.",
    responses={
        200: {
            "description": "Все обращения успешно удалены",
            "content": {
                "application/json": {
                    "example": {"message": "Все обращения удалены"},
                }
            },
        },
    },
)
async def remove_appeals():
    return delete_appeals()

@router.delete(
    "/{appeal_id}",
    summary="Удалить обращение по ID",
    description="Удаляет одно обращение по его уникальному идентификатору.",
    responses={
        200: {
            "description": "Обращение успешно удалено",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Обращение удалено",
                        "appeal": {
                            "id": 1,
                            "title": "Не могу войти в приложение",
                            "text": "Face ID крутится и возвращает на экран логина. Пароль верный.",
                            "department": "APP_LOGIN",
                            "percent_of_confidence": 87.65,
                        },
                    },
                }
            },
        },
        404: {
            "description": "Обращение с указанным ID не найдено",
            "content": {
                "application/json": {
                    "example": {"detail": "Обращение не найдено"},
                }
            },
        },
    },
)
async def remove_appeal_by_id(appeal_id: int):
    deleted_appeal = delete_appeal_by_id(appeal_id)

    if deleted_appeal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Обращение не найдено",
        )

    return {
        "message": "Обращение удалено",
        "appeal": deleted_appeal,
    }
