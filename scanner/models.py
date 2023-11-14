from enum import Enum
from uuid import UUID

from loguru import logger
from pydantic import BaseModel, Field, ValidationError

# NB: https://docs.pydantic.dev/latest/concepts/performance/#performance-tips


class Address(BaseModel):
    city: str
    line1: str
    line2: str | None
    state: str
    country: str
    postal_code: str


class EmploymentStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    terminated = "terminated"
    retired = "retired"


class EmploymentType(str, Enum):
    full_time = "full-time"
    part_time = "part-time"
    contractor = "contractor"
    seasonal = "seasonal"
    temporary = "temporary"
    other = "other"


class Period(str, Enum):
    hourly = "hourly"
    weekly = "weekly"
    biweekly = "biweekly"
    semimonthly = "semimonthly"
    monthly = "monthly"
    annual = "annual"
    salary = "salary"


class BasePay(BaseModel):
    amount: str
    period: Period
    currency: str


class PayCycle(str, Enum):
    daily = "daily"
    weekly = "weekly"
    biweekly = "biweekly"
    semimonthly = "semimonthly"
    monthly = "monthly"
    quarterly = "quarterly"


class PlatformIds(BaseModel):
    employee_id: str
    position_id: str
    platform_user_id: str


class IndentityArgyleComposite(BaseModel):
    id: UUID = Field(..., description="UUID of the identity")
    account: UUID = Field(..., description="UUID of the account associated with the identity")
    address: Address
    first_name: str
    last_name: str
    full_name: str
    birth_date: str = Field(
        ...,
        description="Date of birth in ISO 8601 format. If values are obfuscated (rare), a dash will replace the value (e.g. --01-31 when the year is obfuscated)",
    )
    email: str
    phone_number: str
    picture_url: str
    employment_status: EmploymentStatus = Field(..., description="The employment status relevant to the identity.")
    employment_type: EmploymentType = Field(..., description="Type of employment.")
    job_title: str
    ssn: str
    marital_status: str
    gender: str
    hire_date: str = Field(
        ...,
        description="Timestamp (ISO 8601) of the user's most recent employment start date",
    )
    termination_date: str | None = Field(None, description="Timestamp (ISO 8601) when the user was terminated")
    base_pay: BasePay
    pay_cycle: PayCycle
    platform_ids: PlatformIds
    created_at: str
    updated_at: str
    metadata: dict


def create_identity(**data) -> IndentityArgyleComposite:
    try:
        return IndentityArgyleComposite(**data)
    except ValidationError as exc:
        logger.error(exc.errors())


error_create = [
    {
        "type": "uuid_parsing",
        "loc": ("id",),
        "msg": "Input should be a valid UUID, invalid length: expected length 32 for simple format, found 19",
        "input": "1640675392815476736",
        "ctx": {"error": "invalid length: expected length 32 for simple format, found 19"},
        "url": "https://errors.pydantic.dev/2.4/v/uuid_parsing",
    },
    {
        "type": "uuid_parsing",
        "loc": ("account",),
        "msg": "Input should be a valid UUID, invalid length: expected length 32 for simple format, found 8",
        "input": "1941e405",
        "ctx": {"error": "invalid length: expected length 32 for simple format, found 8"},
        "url": "https://errors.pydantic.dev/2.4/v/uuid_parsing",
    },
    {
        "type": "string_type",
        "loc": ("birth_date",),
        "msg": "Input should be a valid string",
        "input": None,
        "url": "https://errors.pydantic.dev/2.4/v/string_type",
    },
    {
        "type": "string_type",
        "loc": ("phone_number",),
        "msg": "Input should be a valid string",
        "input": None,
        "url": "https://errors.pydantic.dev/2.4/v/string_type",
    },
    {
        "type": "enum",
        "loc": ("employment_type",),
        "msg": "Input should be 'full-time', 'part-time', 'contractor', 'seasonal', 'temporary' or 'other'",
        "input": "fullTime",
        "ctx": {"expected": "'full-time', 'part-time', 'contractor', 'seasonal', 'temporary' or 'other'"},
    },
    {
        "type": "string_type",
        "loc": ("ssn",),
        "msg": "Input should be a valid string",
        "input": None,
        "url": "https://errors.pydantic.dev/2.4/v/string_type",
    },
    {
        "type": "string_type",
        "loc": ("marital_status",),
        "msg": "Input should be a valid string",
        "input": None,
        "url": "https://errors.pydantic.dev/2.4/v/string_type",
    },
    {
        "type": "string_type",
        "loc": ("gender",),
        "msg": "Input should be a valid string",
        "input": None,
        "url": "https://errors.pydantic.dev/2.4/v/string_type",
    },
    {
        "type": "string_type",
        "loc": ("hire_date",),
        "msg": "Input should be a valid string",
        "input": None,
        "url": "https://errors.pydantic.dev/2.4/v/string_type",
    },
    {
        "type": "missing",
        "loc": ("base_pay", "amount"),
        "msg": "Field required",
        "input": {},
        "url": "https://errors.pydantic.dev/2.4/v/missing",
    },
    {
        "type": "missing",
        "loc": ("base_pay", "period"),
        "msg": "Field required",
        "input": {},
        "url": "https://errors.pydantic.dev/2.4/v/missing",
    },
    {
        "type": "missing",
        "loc": ("base_pay", "currency"),
        "msg": "Field required",
        "input": {},
        "url": "https://errors.pydantic.dev/2.4/v/missing",
    },
    {
        "type": "string_type",
        "loc": ("pay_cycle",),
        "msg": "Input should be a valid string",
        "input": None,
        "url": "https://errors.pydantic.dev/2.4/v/string_type",
    },
]
