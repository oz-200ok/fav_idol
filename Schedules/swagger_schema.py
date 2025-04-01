from drf_yasg import openapi

# 삭제 성공 응답 스키마
delete_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "schedule": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="일정 ID"),
                "group_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="그룹 ID"
                ),
                "title": openapi.Schema(
                    type=openapi.TYPE_STRING, description="일정 제목"
                ),
            },
        ),
    },
)

# 수정 및 등록 성공 응답 스키마
update_create_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "group_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="그룹 ID"),
        "schedule_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="일정 ID"),
    },
)


# 공통 응답 생성 함수
def generate_swagger_response(description, schema):
    return {
        200: openapi.Response(description=f"{description} 성공", schema=schema),
        201: openapi.Response(description=f"{description} 등록 성공", schema=schema),
        404: openapi.Response(description="리소스를 찾을 수 없음"),
    }
