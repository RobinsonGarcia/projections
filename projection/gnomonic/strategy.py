from typing import Any, Tuple
from ..base.strategy import BaseProjectionStrategy
from .config import GnomonicConfig
from ..exceptions import ProcessingError
import numpy as np
import logging

logger = logging.getLogger('gnomonic_projection.gnomonic.strategy')

class GnomonicProjectionStrategy(BaseProjectionStrategy):
    """
    Projection Strategy for Gnomonic Projection.

    This class implements the transformation logic for both forward (Equirectangular to Gnomonic)
    and inverse (Gnomonic to Equirectangular) projections based on spherical trigonometry.
    It ensures accurate mapping between geographic coordinates and planar projection coordinates.

    ## Transformation Methods:

    1. **Forward Transformation:**
       Converts planar X and Y coordinates on the Gnomonic projection plane to geographic latitude and longitude.

    2. **Inverse Transformation:**
       Converts geographic latitude and longitude to planar X and Y coordinates on the Gnomonic projection plane.
    """

    def __init__(self, config: GnomonicConfig) -> None:
        """
        Initialize the GnomonicProjectionStrategy with the given configuration.

        Args:
            config (GnomonicConfig): The configuration object containing projection parameters.

        Raises:
            TypeError: If the config is not an instance of GnomonicConfig.
        """
        logger.debug("Initializing GnomonicProjectionStrategy.")
        # Ensure the provided configuration is of the correct type
        if not isinstance(config, GnomonicConfig):
            error_msg = f"config must be an instance of GnomonicConfig, got {type(config)} instead."
            logger.error(error_msg)
            raise TypeError(error_msg)
        self.config: GnomonicConfig = config
        logger.info("GnomonicProjectionStrategy initialized successfully.")

    def from_projection_to_spherical(self, x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Perform inverse Gnomonic projection from planar grid coordinates to geographic coordinates.

        This method converts planar X and Y coordinates on the Gnomonic projection plane to their corresponding
        geographic latitude and longitude values.

        Args:
            x (np.ndarray): X-coordinates in the planar grid.
            y (np.ndarray): Y-coordinates in the planar grid.

        Returns:
            Tuple[np.ndarray, np.ndarray]: Arrays of latitude and longitude corresponding to the input grid points.

        Raises:
            ProcessingError: If the projection computation fails.
        """
        logger.debug("Starting inverse Gnomonic projection (Planar to Geographic).")
        try:
            # Convert projection center latitude and longitude from degrees to radians
            phi1_rad, lam0_rad = np.deg2rad([self.config.phi1_deg, self.config.lam0_deg])
            logger.debug(f"Projection center (phi1_rad, lam0_rad): ({phi1_rad}, {lam0_rad})")

            # Calculate the radial distance from the projection center for each point
            rho = np.sqrt(x**2 + y**2)
            logger.debug("Computed rho (radial distances) from grid points.")

            # Compute the auxiliary angle 'c' based on radial distance and Earth's radius
            c = np.arctan2(rho, self.config.R)
            sin_c, cos_c = np.sin(c), np.cos(c)
            logger.debug(f"Computed auxiliary angles c, sin_c, cos_c for rho.")

            # Calculate latitude (phi) using the inverse projection equation
            phi = np.arcsin(cos_c * np.sin(phi1_rad) - (y * sin_c * np.cos(phi1_rad)) / rho)
            logger.debug("Computed latitude (phi) for inverse projection.")

            # Calculate longitude (lambda) using the inverse projection equation
            lam = lam0_rad + np.arctan2(
                x * sin_c,
                rho * np.cos(phi1_rad) * cos_c + y * np.sin(phi1_rad) * sin_c
            )
            logger.debug("Computed longitude (lambda) for inverse projection.")

            # Convert latitude and longitude from radians back to degrees
            lat = np.rad2deg(phi)
            lon = np.rad2deg(lam)
            logger.debug("Converted phi and lambda from radians to degrees.")

            logger.debug("Inverse Gnomonic projection computed successfully.")
            return lat, lon
        except Exception as e:
            # Log the exception with traceback and raise a ProcessingError
            error_msg = f"Failed during inverse Gnomonic projection: {e}"
            logger.exception(error_msg)
            raise ProcessingError(error_msg) from e

    def from_spherical_to_projection(self, lat: np.ndarray, lon: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Perform forward Gnomonic projection from geographic coordinates to planar grid coordinates.

        This method converts geographic latitude and longitude values to planar X and Y coordinates
        on the Gnomonic projection plane.

        Args:
            lat (np.ndarray): Latitude values in degrees.
            lon (np.ndarray): Longitude values in degrees.

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: Arrays of X and Y planar coordinates and a mask indicating valid points.

        Raises:
            ProcessingError: If the projection computation fails.
        """
        logger.debug("Starting forward Gnomonic projection (Geographic to Planar).")
        try:
            # Convert projection center latitude and longitude from degrees to radians
            phi1_rad, lam0_rad = np.deg2rad([self.config.phi1_deg, self.config.lam0_deg])
            logger.debug(f"Projection center (phi1_rad, lam0_rad): ({phi1_rad}, {lam0_rad})")

            # Convert input latitude and longitude from degrees to radians
            phi_rad, lam_rad = np.deg2rad([lat, lon])
            logger.debug("Converted input lat/lon to radians.")

            # Compute cosine of the auxiliary angle 'c' using the projection equation
            cos_c = (
                np.sin(phi1_rad) * np.sin(phi_rad) +
                np.cos(phi1_rad) * np.cos(phi_rad) * np.cos(lam_rad - lam0_rad)
            )
            logger.debug("Computed cos_c for forward projection.")

            # Prevent division by zero by replacing zero values with a very small number
            cos_c = np.where(cos_c == 0, 1e-10, cos_c)
            logger.debug("Adjusted cos_c to avoid division by zero.")

            # Calculate planar X coordinate using the forward projection equation
            x = self.config.R * np.cos(phi_rad) * np.sin(lam_rad - lam0_rad) / cos_c
            logger.debug("Computed X planar coordinates for forward projection.")

            # Calculate planar Y coordinate using the forward projection equation
            y = self.config.R * (
                np.cos(phi1_rad) * np.sin(phi_rad) -
                np.sin(phi1_rad) * np.cos(phi_rad) * np.cos(lam_rad - lam0_rad)
            ) / cos_c
            logger.debug("Computed Y planar coordinates for forward projection.")

            # Generate a mask to identify valid projection points where cos_c > 0
            mask = cos_c > 0
            logger.debug("Generated mask for valid projection points (cos_c > 0).")

            logger.debug("Forward Gnomonic projection computed successfully.")
            return x, y, mask
        except Exception as e:
            # Log the exception with traceback and raise a ProcessingError
            error_msg = f"Failed during forward Gnomonic projection: {e}"
            logger.exception(error_msg)
            raise ProcessingError(error_msg) from e