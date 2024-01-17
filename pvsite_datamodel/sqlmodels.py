"""SQLAlchemy definition of the pvsite database schema."""

from __future__ import annotations

# This means we can use Typing of objects that have jet to be defined
import enum
import uuid
from datetime import datetime
from typing import List

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.schema import UniqueConstraint

Base = declarative_base()


class CreatedMixin:
    """Mixin to add created datetime to model."""

    created_utc = sa.Column(sa.DateTime, default=lambda: datetime.utcnow())


class UserSQL(Base, CreatedMixin):
    """Class representing the users table.

    Each user row specifies a single user.
    """

    __tablename__ = "users"
    __tables_args__ = (UniqueConstraint("email", name="idx_email"),)

    user_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    email = sa.Column(sa.String(255), index=True, unique=True)
    site_group_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("site_groups.site_group_uuid"),
        nullable=False,
        comment="The foreign key to the site_groups table",
    )

    # Relationships
    site_group: "SiteGroupSQL" = relationship("SiteGroupSQL", back_populates="users")
    api_request = relationship("APIRequestSQL", back_populates="user")


class SiteGroupSQL(Base, CreatedMixin):
    """Class representing the site_groups table.

    Each site_group row specifies a single group of sites.
    """

    __tablename__ = "site_groups"

    site_group_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    site_group_name = sa.Column(sa.String(255), index=True, unique=True)

    # Relationships
    # N-N
    sites: List["SiteSQL"] = relationship(
        "SiteSQL", secondary="site_group_sites", back_populates="site_groups"
    )
    # 1-N, one site group can have many users
    users: List[UserSQL] = relationship("UserSQL", back_populates="site_group")


class SiteGroupSiteSQL(Base, CreatedMixin):
    """Class representing the site_group_sites table.

    Each site_group_site row specifies a single site in a site group.
    """

    __tablename__ = "site_group_sites"
    __table_args__ = (UniqueConstraint("site_group_uuid", "site_uuid", name="idx_site_group_site"),)

    site_group_site_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    site_group_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("site_groups.site_group_uuid"),
        nullable=False,
        comment="The foreign key to the site_groups table",
    )
    site_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("sites.site_uuid"),
        nullable=False,
        comment="The foreign key to the sites table",
    )


class SiteAssetType(enum.Enum):
    """Enum type representing a site's asset type."""

    pv = 1
    wind = 2


class SiteSQL(Base, CreatedMixin):
    """Class representing the sites table.

    Each site row specifies a single panel or cluster of panels
    found on a residential house or commercial building. Their
    data is provided by a client.

    *Approximate size: *
    4 clients * ~1000 sites each = ~4000 rows
    """

    __tablename__ = "sites"

    site_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    client_site_id = sa.Column(
        sa.Integer, index=True, comment="The ID of the site as given by the providing client"
    )
    client_site_name = sa.Column(
        sa.String(255), index=True, comment="The ID of the site as given by the providing client"
    )

    country = sa.Column(
        sa.String(255), server_default="uk", comment="The country in which the site is located"
    )
    region = sa.Column(
        sa.String(255), comment="The region within the country in which the site is located"
    )
    dno = sa.Column(sa.String(255), comment="The Distribution Node Operator that owns the site")
    gsp = sa.Column(sa.String(255), comment="The Grid Supply Point in which the site is located")

    asset_type = sa.Column(
        sa.Enum(SiteAssetType, name="site_asset_type"),
        nullable=False,
        server_default=SiteAssetType.pv.name,
    )

    # For metadata `NULL` means "we don't know".
    orientation = sa.Column(
        sa.Float, comment="The rotation of the panel in degrees. 180° points south"
    )
    tilt = sa.Column(
        sa.Float, comment="The tile of the panel in degrees. 90° indicates the panel is vertical"
    )
    latitude = sa.Column(sa.Float)
    longitude = sa.Column(sa.Float)
    capacity_kw = sa.Column(
        sa.Float, comment="The physical limit on the production capacity of the site"
    )
    inverter_capacity_kw = sa.Column(sa.Float, comment="The inverter capacity of the site")
    module_capacity_kw = sa.Column(sa.Float, comment="The PV module nameplate capacity of the site")

    ml_id = sa.Column(
        sa.Integer,
        autoincrement=True,
        nullable=False,
        unique=True,
        comment="Auto-incrementing integer ID of the site for use in ML training",
    )

    forecasts: List["ForecastSQL"] = relationship("ForecastSQL", back_populates="site")
    generation: List["GenerationSQL"] = relationship("GenerationSQL")
    inverters: List["InverterSQL"] = relationship(
        "InverterSQL", back_populates="site", cascade="all, delete-orphan"
    )
    site_groups: List["SiteGroupSQL"] = relationship(
        "SiteGroupSQL", secondary="site_group_sites", back_populates="sites"
    )


class GenerationSQL(Base, CreatedMixin):
    """Class representing the generation table.

    Each generation row specifies a generated power output over a
    given time range for a site.

    *Approximate size: *
    Generation populated every 5 minutes per site * 4000 sites = ~1,125,000 rows per day
    """

    __tablename__ = "generation"
    __table_args__ = (
        UniqueConstraint("site_uuid", "start_utc", "end_utc", name="uniq_cons_site_start_end"),
    )

    generation_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    site_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("sites.site_uuid"),
        nullable=False,
        index=True,
        comment="The site for which this geenration yield belongs to",
    )
    generation_power_kw = sa.Column(
        sa.Float,
        nullable=False,
        comment="The actual generated power in kW at this site for this datetime interval",
    )

    start_utc = sa.Column(
        sa.DateTime,
        nullable=False,
        index=True,
        comment="The start of the time interval over which this generated power value applies",
    )
    end_utc = sa.Column(
        sa.DateTime,
        nullable=False,
        comment="The end of the time interval over which this generated power value applies",
    )

    site: SiteSQL = relationship("SiteSQL", back_populates="generation")


class ForecastSQL(Base, CreatedMixin):
    """Class representing the forecasts table.

    Each forecast row refers to a sequence of predicted solar generation values
    over a set of target times for one site.

    *Approximate size: *
    One forecast per site every 5 minutes = ~1,125,000 rows per day
    """

    __tablename__ = "forecasts"

    forecast_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    site_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("sites.site_uuid"),
        nullable=False,
        comment="The site for which the forecast sequence was generated",
    )

    # The timestamp at which we are making the forecast. This is often referred as "now" in the
    # modelling code.
    # Note that this could be very different from the `created_utc` time, for instance if we
    # run the model for a given "now" timestamp in the past.
    timestamp_utc = sa.Column(
        sa.DateTime,
        nullable=False,
        comment="The creation time of the forecast sequence",
    )

    forecast_version = sa.Column(
        sa.String(32),
        nullable=False,
        comment="The semantic version of the model used to generate the forecast",
    )

    # one (forecasts) to many (forecast_values)
    forecast_values: List["ForecastValueSQL"] = relationship("ForecastValueSQL")
    site = relationship("SiteSQL", back_populates="forecasts")

    __table_args__ = (
        # With this index, we are assuming that it doesn't make sense to do a query solely on
        # `timestamp_utc`: we always also filter by site_uuid.
        sa.Index("ix_forecasts_site_uuid_timestamp_utc", "site_uuid", "timestamp_utc"),
    )


class ForecastValueSQL(Base, CreatedMixin):
    """Class representing the forecast_values table.

    Each forecast_value row is a prediction for the power output
    of a site over a target datetime interval. Many predictions
    are made for each site at each target interval.

    *Approximate size: *
    One forecast value every 5 minutes per site per forecast.
    Each forecast's prediction sequence covers 24 hours of target
    intervals = ~324,000,000 rows per day
    """

    __tablename__ = "forecast_values"

    forecast_value_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    start_utc = sa.Column(
        sa.DateTime,
        nullable=False,
        index=True,
        comment="The start of the time interval over which this predicted power value applies",
    )
    end_utc = sa.Column(
        sa.DateTime,
        nullable=False,
        comment="The end of the time interval over which this predicted power value applies",
    )
    forecast_power_kw = sa.Column(
        sa.Float,
        nullable=False,
        comment="The predicted power generation of this site for the given time interval",
    )

    # This is the different between `start_utc` and the `forecast`'s `timestamp_utc`, in minutes.
    # It's useful to have it in its own column to efficiently query forecasts for a given horizon.
    # TODO Set to nullable=False
    horizon_minutes = sa.Column(
        sa.Integer,
        nullable=True,
        comment="The time difference between the creation time of the forecast value "
        "and the start of the time interval it applies for",
    )

    forecast_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("forecasts.forecast_uuid"),
        nullable=False,
        comment="The forecast sequence this forcast value belongs to",
    )

    forecast: ForecastSQL = relationship("ForecastSQL", back_populates="forecast_values")

    __table_args__ = (
        # Here we assume that we always filter on `horizon_minutes` *for given forecasts*.
        sa.Index(
            "ix_forecast_values_forecast_uuid_horizon_minutes", "forecast_uuid", "horizon_minutes"
        ),
    )


class StatusSQL(Base, CreatedMixin):
    """Class representing the status table.

    Each status row defines a message reporting on the status of the
    services within the nowcasting domain

    *Approximate size: *
    ~1 row per day
    """

    __tablename__ = "status"

    status_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    status = sa.Column(sa.String(255))
    message = sa.Column(sa.String(255))


class InverterSQL(Base, CreatedMixin):
    """Class representing the inverters table.

    Each InverterSQL row represents an inverter tied to a SiteSQL row.

    *Approximate size: *
    4 clients * ~1000 sites each * ~1 inverter each = ~4000 rows
    """

    __tablename__ = "inverters"

    inverter_uuid = sa.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    site_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("sites.site_uuid"),
        nullable=False,
        index=True,
        comment="The UUID for the site that has this inverter",
    )

    site: SiteSQL = relationship("SiteSQL", back_populates="inverters")


class APIRequestSQL(Base, CreatedMixin):
    """Information about what API route was called."""

    __tablename__ = "api_request"

    uuid = sa.Column(UUID, primary_key=True, server_default=sa.func.gen_random_uuid())
    url = sa.Column(sa.String)

    user_uuid = sa.Column(UUID, sa.ForeignKey("users.user_uuid"), index=True)
    user = relationship("UserSQL", back_populates="api_request")
