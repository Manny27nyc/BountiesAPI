import requests
from math import pow
from decimal import Decimal
from django.core.management.base import BaseCommand
from std_bounties.models import Activity, Community, Bounty, Event, Comment, Fulfillment, FulfillerApplication
import logging
import sys

logger = logging.getLogger('django')


class Command(BaseCommand):
    help = 'Populate the activities table with comments'

    def handle(self, *args, **options):
        try:
            all_comments = Comment.objects.all()
            for comment in all_comments:
                try:
                    bounty = Bounty.objects.get(comments__in=[comment])
                    Activity.objects.create(
                        event_type='Comment',
                        bounty_id=bounty.id,
                        comment_id=comment.id,
                        date=comment.created,
                        user_id=comment.user_id,
                        community_id=comment.community_id)
                except Bounty.DoesNotExist:
                    pass

                try:
                    fulfillment = Fulfillment.objects.get(comments__in=[comment])
                    Activity.objects.create(
                        event_type='Comment',
                        fulfillment_id=fulfillment.id,
                        comment_id=comment.id,
                        date=comment.created,
                        user_id=comment.user_id,
                        community_id=comment.community_id)
                except Fulfillment.DoesNotExist:
                    pass
        except Exception as e:
            # goes to rollbar
            logger.exception(e)
            sys.exit(1)