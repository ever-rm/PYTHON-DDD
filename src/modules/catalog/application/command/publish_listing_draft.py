from dataclasses import dataclass

from modules.catalog.application import catalog_module
from modules.catalog.domain.entities import Listing
from modules.catalog.domain.repositories import ListingRepository
from modules.catalog.domain.rules import OnlyListingOwnerCanPublishListing
from modules.catalog.domain.value_objects import ListingId, SellerId
from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command
from seedwork.domain.mixins import check_rule


@dataclass
class PublishListingDraftCommand(Command):
    """A command for publishing a draft of a listing"""

    listing_id: ListingId  # a listing to be published
    seller_id: SellerId  # a seller, who is publishing a listing


@catalog_module.command_handler
def publish_listing_draft(
    command: PublishListingDraftCommand,
    listing_repository: ListingRepository,
):
    listing: Listing = listing_repository.get_by_id(command.listing_id)

    check_rule(
        OnlyListingOwnerCanPublishListing(
            listing_seller_id=listing.seller_id, current_seller_id=command.seller_id
        )
    )

    events = listing.publish()

    listing_repository.persist_all()

    return CommandResult.success(entity_id=listing.id, events=events)
