from pydantic import BaseModel, Field

class UserRequest(BaseModel):
    business_name: str = Field(description="Business name")
    business_niche: str = Field(description="Type of business")
    keywords: list[str] = Field(description="Business keywords")
    phone_number: str = Field(description="Phone number")