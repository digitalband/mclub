from pydantic import BaseModel


class HealthCheckSchema(BaseModel):
    status: str = "OK"
