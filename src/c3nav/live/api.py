from typing import Annotated, List
from annotated_types import Ge, Lt, MaxLen, MinLen
from django.core.handlers.wsgi import WSGIRequest
from ninja import Field as APIField
from ninja import Router as APIRouter
from pydantic import PositiveInt, SecretBytes, field_validator

from c3nav.api.auth import APIKeyAuth, auth_permission_responses, auth_responses, validate_responses
from c3nav.api.exceptions import API404, APIConflict, APIRequestValidationFailed
from c3nav.api.schema import BaseSchema

live_api_router = APIRouter(tags=["live"])

class ExampleSchema(BaseSchema):
    """
    Current example
    """
    some_string: str = APIField(
        title="the riddle",
        description="of newhampton"
    )
    some_bool: bool = APIField(
        title="somethingsome bool",
        description="if True, example fun example"
    )
    some_list: list[str] = APIField(
        title="list of things",
        description="excellent examples may come to you",
    )

    @field_validator("some_bool")
    def some_bool_must_be_true(cls, some_bool):
        if some_bool != True:
            raise ValueError("some_bool must be true")
        return some_bool

class EnrollRequestSchema(BaseSchema):
    """
    This schema contains the request format for enrolling a pubkey
    """
    pubkey: Annotated[List[Annotated[int, Lt(256), Ge(0)]], MinLen(256), MaxLen(256)] = APIField(
        title="AES 256 pubkey",
        description="Your client-side public key for live location sharing"
    )

@live_api_router.get('/get/', summary="get example",
                     description="Returns example about the current example",
                     response={200: ExampleSchema, **auth_responses})
def get_example(request):
    return ExampleSchema(
        some_string="test123",
        some_bool=True,
        some_list=["item1","item2"]
    )


@live_api_router.put('/enroll/', summary="Enroll public key",
                     description="Enroll your public key for live location sharing",
                     response={200: EnrollRequestSchema, **validate_responses, **auth_responses})
def put_example(request, pubkey: EnrollRequestSchema):
    return pubkey
