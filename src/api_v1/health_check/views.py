from fastapi import APIRouter, status

from api_v1.health_check.schemas import HealthCheck

router = APIRouter()


@router.get(
    path="/health",
    response_model=HealthCheck,
    status_code=status.HTTP_200_OK,
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
)
def get_health() -> HealthCheck:
    """
    Endpoint to perform a healthcheck on.

    Other services which rely on proper functioning of the API service will not
    deploy if this endpoint returns any other HTTP status code except 200 (OK).

    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")
