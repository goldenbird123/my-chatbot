from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class MemoryData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str = ""
    learning: str = ""
    project: str = ""
    likes: str = ""

    @field_validator("name", "learning", "project", "likes", mode="before")
    @classmethod
    def normalize_text(cls, value):
        if value is None:
            return ""
        value = str(value).strip()
        return value

    @classmethod
    def safe_parse(cls, payload):
        try:
            return cls.model_validate(payload)
        except ValidationError:
            return cls()


class MemoryExtractionResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    memory: bool = False
    data: MemoryData = Field(default_factory=MemoryData)

    @field_validator("memory", mode="before")
    @classmethod
    def normalize_memory_flag(cls, value):
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes"}
        return bool(value)

    @classmethod
    def safe_parse(cls, payload):
        try:
            return cls.model_validate(payload)
        except ValidationError:
            return cls()
