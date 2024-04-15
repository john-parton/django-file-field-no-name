The purpose of this application is to test surprising behavior which was found when
doing a performance audit of a Django application.

## Conditions for behavior

You must have an ImageField with the `width_field` or `height_field` arguments set.

## Description of current behavior

When a model is saved, the image file is written out using the Storage API, and then
in order for the width and height fields to be updated, the file is read back out
and then the width and height are extracted from the image.

In the case the storage is local, the performance impact is probably negligible, 
unless the application is seriously IO constrainted, however if the storage is
remote, the performance impact is significant, and there can be other impacts on
operations.

For instance, if using S3 as backing, more GET operations are performed than
strictly necessary. This could be a few dollars a day of operational costs if your
scale is small, but can be significant if egress charges are high.

As another example, CloudFlare Images rate limits requests. This effectively cuts
the rate limit in half because every save operations requires an additional GET.

## Proposed behavior

The proposed behavior is to simple read the image file which is resident in memory
without reading it back out from the storage backend.

## Possible breaking issues

The vast majority of storage backends and use cases likely guarantee that if you
write a file into storage, and then retrieve it, you will get the same file back.

However, for some image-specific services, they will compress or crush larger images.

For users who specifically have this use case, they may end up with the `width_field`
and `height_field` not representing the actual size of the image in the store, but
rather the size of the image at time of upload.

## Explanation of current behavior

It looks like when a model's save() method is called, the field's pre_save() method
is called which results in the descriptor for the field having its __get__ method
called and then immediately having its __set__ method called with a similar value.

The effect is to coerce the value of the field to `ImageFieldFile` which is a subclass
of `ImageFile`. The `ImageFieldFile` instance is assigned a property of `file` which
is the wrapped original value.

The image field then saves and persists the data using the storage API, and then the
wrapped file isn't referred to later to get the width and height. When the width and
height are requested, the file is read back out of storage.

## Proposed fix

No specific fix at this time.

## Mitigating breaking issues

Considering how unusual this use case is, it may be sufficient to document the change
in behavior and provide a code snippet to wire up a signal handler to do the
additional read for those users who have the unusual storage backends and actually
care about the width/height being what is on disk. This would also allow users to
customize the behavior. For instance, maybe if the image is under a certain resolution,
the storage provider guarantees they don't mangle the image. A user could enshrine
that logic in the signal handler, so they could still get the performance uplift where
appropriate.

## Running tests

- Clone this repo
- pip install -r requirements.txt
- ./manage.py test

## How these test are authored

The assumption is that the correct behavior is to not perform the additional read
or IO. The included model is backed by a subclass of the local storage backend
that raises an exception if trying to open a file.


