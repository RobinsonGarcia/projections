# /Users/robinsongarcia/projects/gnomonic/projection/default_projections.py

from .registry import ProjectionRegistry

from .gnomonic.config import GnomonicConfig
from .gnomonic.grid import GnomonicGridGeneration
from .gnomonic.strategy import GnomonicProjectionStrategy
from .gnomonic.transform import GnomonicTransformer  # Updated to per-projection transformer

from .mercator.config import MercatorConfig
from .mercator.grid import MercatorGridGeneration
from .mercator.strategy import MercatorProjectionStrategy
from .mercator.transform import MercatorTransformer  # Updated to per-projection transformer

# Import your classes
from .stereographic.config import StereographicConfig
from .stereographic.grid import StereographicGridGeneration
from .stereographic.strategy import StereographicProjectionStrategy
from .stereographic.transform import StereographicTransformer


from .azimutal_equidistant.config import AzimutalEquidistantConfig
from .azimutal_equidistant.grid import AzimutalEquidistantGridGeneration
from .azimutal_equidistant.strategy import AzimutalEquidistantProjectionStrategy
from .azimutal_equidistant.transform import AzimutalEquidistantTransformer


from .base.interpolation import BaseInterpolation
from .exceptions import RegistrationError
import logging

# Initialize logger for this module
logger = logging.getLogger('gnomonic_projection.default_projections')

def register_default_projections():
    """
    Register default projections with their components.

    Raises:
        RegistrationError: If registration of any default projection fails.
    """
    logger.debug("Registering default projections.")
    try:
        # Register Gnomonic projection
        ProjectionRegistry.register("gnomonic", {
            "config": GnomonicConfig,
            "grid_generation": GnomonicGridGeneration,
            "projection_strategy": GnomonicProjectionStrategy,
            "interpolation": BaseInterpolation,
            "transformer": GnomonicTransformer,  # Updated to GnomonicTransformer
        })
        logger.info("Default projection 'gnomonic' registered successfully.")

        ProjectionRegistry.register("azimutal_equidistant", {
            "config": AzimutalEquidistantConfig,
            "grid_generation": AzimutalEquidistantGridGeneration,
            "projection_strategy": AzimutalEquidistantProjectionStrategy,
            "interpolation": BaseInterpolation,
            "transformer": AzimutalEquidistantTransformer,  # Updated to GnomonicTransformer
        })
        logger.info("Default projection 'gnomonic' registered successfully.")

        # Register Mercator projection
        ProjectionRegistry.register("mercator", {
            "config": MercatorConfig,
            "grid_generation": MercatorGridGeneration,
            "projection_strategy": MercatorProjectionStrategy,
            "interpolation": BaseInterpolation,
            "transformer": MercatorTransformer,  # Updated to MercatorTransformer
        })


        ProjectionRegistry.register("stereographic", {
        "config": StereographicConfig,
        "grid_generation": StereographicGridGeneration,
        "projection_strategy": StereographicProjectionStrategy,
        "interpolation": BaseInterpolation,           # or your own
        "transformer": StereographicTransformer,       # or your own
    })
        logger.info("Default projection 'mercator' registered successfully.")

    except RegistrationError as e:
        logger.exception("Failed to register default projections.")
        raise RegistrationError(f"Failed to register default projections: {e}") from e
    except Exception as e:
        logger.exception("An unexpected error occurred while registering default projections.")
        raise RegistrationError(f"An unexpected error occurred: {e}") from e

    logger.debug("All default projections registered.")