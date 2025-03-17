from typing import TypeVar

from fastapi_pagination import Page
from fastapi_pagination.customization import (
    CustomizedPage,
    UseFieldsAliases,
)

T = TypeVar("T")


CustomPage = CustomizedPage[
    Page[T],
    UseFieldsAliases(
        items="content",
        size="pageSize",
        page="pageNumber",
        pages="totalPages",
        total="totalElements",
    ),
]