"""Base cloud."""

from damasen.mixins.enhanced import EnhancedWithData


class Cloud(EnhancedWithData):

    """Base class for all clouds."""

    allow_no_python_file = False
    allow_no_data_file = True
