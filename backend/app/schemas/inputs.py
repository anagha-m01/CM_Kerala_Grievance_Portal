from pydantic import BaseModel, Field, EmailStr, field_validator

DISTRICTS = ['Thiruvananthapuram', 'Kollam', 'Pathanamthitta', 'Alappuzha', 'Kottayam', 'Idukki', 'Ernakulam', 'Thrissur', 'Palakkad', 'Malappuram', 'Kozhikode', 'Wayanad', 'Kannur', 'Kasaragod']
STATUSES = ['Submitted', 'Under Review', 'In Progress', 'Resolved', 'Reopened']
PRIORITIES = ['Low', 'Medium', 'High']


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    mobile: str = Field(pattern=r'^\+?[0-9]{10,15}$')
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ContactIn(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    subject: str = Field(min_length=3, max_length=200)
    message: str = Field(min_length=5, max_length=4000)


class GrievanceIn(BaseModel):
    district: str
    category: str = Field(min_length=2, max_length=120)
    subject: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=15, max_length=10000)
    ai_summary: str | None = Field(default=None, max_length=1000)
    ai_department: str | None = Field(default=None, max_length=150)
    ai_category: str | None = Field(default=None, max_length=120)
    ai_priority: str | None = None
    ai_fallback: bool = False

    @field_validator('district')
    @classmethod
    def valid_district(cls, value):
        if value not in DISTRICTS:
            raise ValueError('Select a valid Kerala district')
        return value

    @field_validator('ai_priority')
    @classmethod
    def valid_ai_priority(cls, value):
        if value is not None and value not in PRIORITIES:
            raise ValueError('Invalid priority')
        return value


class ReviewIn(BaseModel):
    priority: str | None = None
    remark: str = Field(default='', max_length=2000)

    @field_validator('priority')
    @classmethod
    def valid_priority(cls, value):
        if value is not None and value not in PRIORITIES:
            raise ValueError('Invalid priority')
        return value


class AssignIn(BaseModel):
    department_id: int
    officer_id: int
    remark: str = Field(default='', max_length=2000)


class RemarkIn(BaseModel):
    remark: str = Field(min_length=2, max_length=2500)
    is_public: bool = False


class StatusIn(BaseModel):
    status: str
    remark: str = Field(min_length=3, max_length=2000)


class ReportIn(BaseModel):
    findings: str = Field(min_length=5, max_length=5000)
    action_taken: str = Field(min_length=5, max_length=5000)


class ReportReviewIn(BaseModel):
    decision: str  # approve or request_changes
    remark: str = Field(min_length=3, max_length=2500)


class FeedbackIn(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default='', max_length=2000)


class AIIn(BaseModel):
    description: str = Field(min_length=15, max_length=10000)


class AIResult(BaseModel):
    department: str
    category: str
    priority: str
    summary: str
