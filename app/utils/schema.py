from pydantic import BaseModel
from humps import camelize


def to_camel(string):
    return camelize(string)


class AutoCamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True
