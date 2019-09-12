import os

from payshare.purchases.models import UserProfile

for profile in UserProfile.objects.filter(
    avatar_image_url__icontains="/media/filer_public/"
):
    basename = os.path.basename(profile.avatar_image_url)
    newbasename = basename + "__180x180_q85_crop_subsampling-2_upscale.png"
    new_url = (
        profile.avatar_image_url
        .replace("/filer_public/", "/filer_public_thumbnails/filer_public/")
        .replace(basename, newbasename)
    )
    profile.avatar_image_url = new_url
    profile.save()
