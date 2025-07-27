#!/bin/python

import os
import shutil

import requests
from django.core.management.base import BaseCommand

from payshare.purchases.models import UserProfile


class Command(BaseCommand):
    help = "Download all User avatar images to disk for a local backup"

    def handle(self, *args, **options):
        output_dir = os.path.abspath("avatars")
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        values = UserProfile.objects.values("user__id", "avatar_image_url")
        for obj in values:
            ext = ".png"
            try:
                ext = os.path.splitext(obj["avatar_image_url"])[1]
            except (AttributeError, IndexError):
                pass
            user_id = obj["user__id"]
            filepath = os.path.join(
                output_dir,
                "{0}{1}".format(user_id, ext),
            )

            try:
                avatar_image_url = obj["avatar_image_url"]
                self.stdout.write(
                    self.style.NOTICE(
                        "Starting to download: " + avatar_image_url
                    )
                )

                response = requests.get(avatar_image_url, stream=True)
                if response.status_code != 200:
                    raise ValueError("Response: " + response.status_code)
                with open(filepath, "wb") as f:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, f)
                    self.stdout.write(
                        self.style.SUCCESS("Finished download to " + filepath)
                    )
            except Exception as err:
                self.stdout.write(
                    self.style.ERROR("Failed to download " + filepath)
                )
                self.stdout.write(self.style.ERROR(str(err)))

        self.stdout.write(
            self.style.SUCCESS("Done")
        )


