from django.conf import settings
from django.views import generic, View
from django.http import HttpResponse, JsonResponse

from oauth2_provider.views.generic import ProtectedResourceView

from xbmccontrolroom.models import MediaFile

from .models import PaymentMethod, Deal, HouseholdAccountBook, Package, Event, Asset, Product

from PIL import Image, ExifTags

import os, shutil
import logging
logger = logging.getLogger(__name__)

class ThumbnailValidationScanView(View):
    http_method_names = ['get']
    template_name = "thumbnailvalidationscan.html"

    images_ext = [".BMP", ".JPG", ".GIF", ".ICO", ".PCX", ".TGA", ".PNG", ".MNG"]

    def get(self, request, *args, **kwargs):
        """return Thumbnail Validation on HouseholdAccountBook."""

        ret = {"code" : -1, "desc" : ""}

        ex_count = 0

        #미디어 파일에 대한 썸네일 처리

        #썸네일 폴더 확인 및 생성
        mediafile_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'images', 'mediafile')
        if os.path.exists(mediafile_path) is False:
            os.mkdir(mediafile_path)
        mediafile_thumbnail_path = os.path.join(mediafile_path, 'thumbnail')
        if os.path.exists(mediafile_thumbnail_path) is False:
            os.mkdir(mediafile_thumbnail_path)


        mediafiles = MediaFile.objects.filter(name__isnull=False)
        thumbnail_size = (128, 128)
        size = (720, 720)
        exiftarget = None
        for orientation in ExifTags.TAGS:
            if ExifTags.TAGS[orientation] == 'Orientation':
                exiftarget = orientation
                break
        for mediafile in mediafiles:
            try:
                fname, ext = os.path.splitext(mediafile.name)

                if ext.upper() not in self.images_ext:
                    continue

                thumbnail_path = os.path.join(mediafile_thumbnail_path, str(mediafile.idx) + ext)
                if os.path.exists(thumbnail_path) is False:
                    im = Image.open(mediafile.fullpath())
                    if im._getexif() is not None:
                        exif = dict(im._getexif().items())
                        rotation = exif.get(exiftarget, 1)
                        if rotation == 3:
                            im = im.rotate(180, expand=True)
                        elif rotation == 6:
                            im = im.rotate(270, expand=True)
                        elif rotation == 8:
                            im = im.rotate(90, expand=True)
                    if im.size > thumbnail_size:
                        im.thumbnail(thumbnail_size)
                    im.save(thumbnail_path)
                    im.close()

                image_path = os.path.join(mediafile_path, str(mediafile.idx) + ext)
                if os.path.exists(image_path) is False:
                    im = Image.open(mediafile.fullpath())
                    if im._getexif() is not None:
                        exif = dict(im._getexif().items())
                        rotation = exif.get(exiftarget, 1)
                        if rotation == 3:
                            im = im.rotate(180, expand=True)
                        elif rotation == 6:
                            im = im.rotate(270, expand=True)
                        elif rotation == 8:
                            im = im.rotate(90, expand=True)
                    if im.size > size:
                        im.thumbnail(size)
                    im.save(image_path,optimize=True)
                    im.close()

                
            except Exception as e:
                logger.error('mediafile thumbnail proc error {0}, {1}'.format(mediafile, str(e)))
                ex_count = ex_count + 1

        #지불 방법에 대한 썸네일 처리
        paymentmethods = PaymentMethod.objects.all()
        size = (64, 64)
        for paymentmethod in paymentmethods:
            try:
                if paymentmethod.thumbnail_image is not None and os.path.exists(paymentmethod.thumbnail_image.path) is True:
                    im = Image.open(paymentmethod.thumbnail_image.path)
                    width, height = im.size
                    if im.size > size:
                        im.thumbnail(size)
                        im.save(paymentmethod.thumbnail_image.path)
                    im.close()
            except Exception as e:
                logger.error('paymentmethod thumbnail proc error {}, {}'.format(paymentmethod, e))
                ex_count = ex_count + 1

        #자산에 대한 썸네일 처리
        assets = Asset.objects.all()
        size = (64, 64)
        for asset in assets:
            try:
                if asset.thumbnail_image is not None and  os.path.exists(asset.thumbnail_image.path) is True:
                    im = Image.open(asset.thumbnail_image.path)
                    width, height = im.size
                    if im.size > size:
                        im.thumbnail(size)
                        im.save(asset.thumbnail_image.path)
                    im.close()
            except Exception as e:
                logger.error('asset thumbnail proc error {}, {}'.format(asset, e))
                ex_count = ex_count + 1

        #제품에 대한 썸네일 처리
        products = Product.objects.all()
        size = (64, 64)
        for product in products:
            try:
                if product.thumbnail_image is not None and os.path.exists(product.thumbnail_image.path) is True:
                    im = Image.open(product.thumbnail_image.path)
                    width, height = im.size
                    if im.size > size:
                        im.thumbnail(size)
                        im.save(product.thumbnail_image.path)
                    im.close()
            except Exception as e:
                logger.error('product thumbnail proc error {}, {}'.format(product, e))
                ex_count = ex_count + 1

        ret["code"] = 1 if ex_count == 0 else -1
        ret["desc"] = '갱신이 완료되었습니다.' if ex_count == 0 else "{}건의 오류가 있었습니다.".format(ex_count)
        return JsonResponse(ret)

class HouseholdAccountBookListView(generic.ListView):
    context_object_name = 'accountbook_list'
    template_name = 'accountbook/booklist.html'
    def get_queryset(self):
        """return HouseholdAccountBooks."""
        return HouseholdAccountBook.objects.all()

class HouseholdAccountBookView(generic.ListView):
    context_object_name = 'deal_list'
    template_name = 'accountbook/book.html'
    def get_queryset(self):
        """return Deals on HouseholdAccountBook."""
        #pk = self.args[0]
        print(self.args)
        #return Deal.objects.filter(accountbook_id == pk).order_by('-idx')[:100]
        return ""

class DealView(generic.DetailView):
    model = Deal
    template_name = 'accountbook/deal.html'

class PackageListView(generic.ListView):
    context_object_name = 'package_list'
    template_name = 'accountbook/packagelist.html'
    def get_queryset(self):
        #dealid = self.args[0]
        #return Package.objects.filter(deal_id == dealid)
        return ""
    #def get_context_data(self, **kwargs):
    #    context = super(PackageListView, self).get_context_data(**kwargs)
    #    context['dealid'] = self.args[0]
    #    return context

class PackageView(generic.DetailView):
    model = Package
    template_name = 'accountbook/package.html'

class ApiEndpoint(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        return HttpResponse('Hello, OAuth2!')
        