import enum

from humps import camelize
from pydantic import BaseConfig, BaseModel, validator


def to_camel(string):
    return camelize(string)


class TemplateConfig(BaseConfig):
    alias_generator = to_camel
    allow_population_by_field_name = True
    orm_mode = True


class TemplateModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True
        use_enum_values = True

    @validator('*', pre=True)
    def empty_str_to_none_and_clear_whitespace(cls, v):
        if isinstance(v, str):
            v_strip = v.strip()
            if v_strip == '':
                raise ValueError("cannot be empty")
            else:
                return v_strip
        else:
            return v


def convert_enum_to_string(myenum: enum.Enum):
    enum_list = [e.value for e in myenum]
    return f"({', '.join(enum_list)})"
