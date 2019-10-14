import json
import hashlib
import os
from datetime import timezone, timedelta, datetime
import mimetypes
import logging
import zipfile
from base64 import b64encode
import requests

from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.utils.timezone import now
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from oauth2_provider.models import Application
from oauth2_provider.views.generic import ProtectedResourceView

from ranged_fileresponse import RangedFileResponse
from .models import *

from common import utility

logger = logging.getLogger(__name__)

class ApiEndpoint_ScanMediaFiles(View):

    def validMediaFile(self, filename, dirname):
        mediaFile = MediaFile.objects.filter(name=filename, path=dirname[len(MediaFile.MEDIAS_PATH) + 1:]).first()
        if mediaFile is None:
            mediaFile = MediaFile()
        else:
            if datetime.fromtimestamp(os.path.getmtime(os.path.join(dirname, filename))) <= mediaFile.updDate:
                logger.info('skip file {}'.format(os.path.join(dirname, filename)))
                mediaFile.size = os.path.getsize(os.path.join(dirname, filename))
                mediaFile.save()
                return False

        logger.info('proc file {}'.format(os.path.join(dirname, filename)))
        mediaFile.name = filename
        mediaFile.path = dirname[len(MediaFile.MEDIAS_PATH) + 1:]
        mediaFile.md5 = utility.getFileMd5(os.path.join(dirname, filename))
        mediaFile.size = os.path.getsize(os.path.join(dirname, filename))
        mediaFile.updDate = now()
        mediaFile.save()
        return True

    def get(self, request, *args, **kwargs):
        targetpath = os.path.join(MediaFile.MEDIAS_PATH, request.GET.get('path'))
        recursive = request.GET.get('recursive')

        logger.info("target path is '{}'".format(targetpath))
        ret = {"code" : -1, "desc" : "", "skip" : 0, "proc" : 0, "total" : 0}

        try:
            if recursive == "true":
                MediaFile.objects.filter(path__startswith=request.GET.get('path')).update(size=0)

                for dirname, dirnames, filenames in os.walk(targetpath):
                    for filename in filenames:
                        ret["total"] = ret["total"] + 1
                        result = self.validMediaFile(filename, dirname)
                        if result:
                            ret["proc"] = ret["proc"] + 1
                        else:
                            ret["skip"] = ret["skip"] + 1
                MediaFile.objects.filter(size=0).delete()
            else:
                MediaFile.objects.filter(path=targetpath).update(size=0)

                for item in os.listdir(targetpath):
                    if os.path.isfile(os.path.join(targetpath, item)):
                        ret["total"] = ret["total"] + 1
                        result = self.validMediaFile(item, targetpath)
                        if result:
                            ret["proc"] = ret["proc"] + 1
                        else:
                            ret["skip"] = ret["skip"] + 1
                MediaFile.objects.filter(size=0).delete()
            ret["code"] = 1
        except Exception as e:
            logger.error("{}".format(e))
        return JsonResponse(ret)


class ApiEndpoint_HostWelcome(View):
    def get(self, request, *args, **kwargs):

        ret = {"code" : -1, "desc" : "", "idx" : 0}

        xbmc_media_host = XbmcMediaHost.objects.filter(name=request.GET.get('name')).first()

        if xbmc_media_host is None:
            xbmc_media_host = XbmcMediaHost()

        xbmc_media_host.macaddress = request.GET.get('mac')
        xbmc_media_host.name = request.GET.get('name')
        xbmc_media_host.ipaddress = request.GET.get('ip')
        xbmc_media_host.osinfo = request.GET.get('os')
        xbmc_media_host.appinfo = request.GET.get('app')
        xbmc_media_host.deviceinfo = request.GET.get('dv')
        xbmc_media_host.save()

        ret["code"] = 1
        ret["idx"] = xbmc_media_host.idx

        return JsonResponse(ret)

class ApiEndpoint_HostPing(View):
    def get(self, request, *args, **kwargs):

        ret = {"code" : -1, "desc" : ""}

        xbmc_media_host = XbmcMediaHost.objects.filter(idx=request.GET.get('idx')).first()

        if xbmc_media_host is None:
            ret["desc"] = 'You are Not My Host.'
            return JsonResponse(ret)

        on_air = OnAir.objects.filter(xbmcmediahost=xbmc_media_host).first()

        if on_air is None:
            on_air = OnAir(xbmcmediahost=xbmc_media_host)

        ret["action"] = on_air.action
        ret["action_param"] = on_air.action_param
        on_air.action = ""
        on_air.action_param = ""
        on_air.updDate = now()
        on_air.save()

        ret["code"] = 1
        ret["desc"] = 'Pong!'

        return JsonResponse(ret)

class ApiEndpoint_SyncMediaBunchList(View):
    def get(self, request, *args, **kwargs):

        idx = int(request.GET.get('idx'))
        if idx < 0:
            media = MediaFile.objects.filter(idx=-idx).first()
            if media is None:
                ret = {}
                ret["code"] = -1
                ret["desc"] = 'Invalid idx!'
                return JsonResponse(ret)

            mediabunch = MediaFile.objects.filter(path=media.path)
        else:
            mediabunch = MediaFile.objects.filter(idx=idx)
        ret = {}
        ret["code"] = 1
        ret["medias"] = []
        for media in mediabunch:
            ret["medias"].append({"name":media.name, "path":media.path, "md5":media.md5, "idx":media.idx, "size":media.size})
        return JsonResponse(ret)

class ApiEndpoint_SyncMediaDownload(View):
    def get(self, request, *args, **kwargs):
        mediafile = MediaFile.objects.filter(idx=request.GET.get('idx')).first()
        file_path = os.path.join(MediaFile.MEDIAS_PATH, mediafile.path, mediafile.name)
        with open(file_path, 'rb') as f:
            response = HttpResponse(f, content_type='application/force-download')
            response['Content-Length'] = len(response.content)
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response

class ApiEndpoint_MediaStream(View):
    def get(self, request, *args, **kwargs):
        mediafile = MediaFile.objects.filter(idx=request.GET.get('idx')).first()
        filename = os.path.join(MediaFile.MEDIAS_PATH, mediafile.path, mediafile.name)
        response = RangedFileResponse(request, open(filename, 'rb'), content_type=mimetypes.guess_type(mediafile.name)[0])
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        return response

class ApiEndpoint_HostByeBye(View):
    def get(self, request, *args, **kwargs):
        ret = {"code" : -1, "desc" : ""}
        xbmc_media_host = XbmcMediaHost.objects.filter(idx=request.GET.get('idx')).first()
        if xbmc_media_host is None:
            ret["desc"] = 'I don\'t know who you are.'
            return JsonResponse(ret)
        on_air = OnAir.objects.filter(xbmcmediahost=xbmc_media_host).first()
        if on_air is not None:
            on_air.delete()
        xbmc_media_host.delete()
        ret["code"] = 1
        ret["desc"] = 'See you again.'
        return JsonResponse(ret)

class ApiEndpoint_AddonVersion(View):
    def get(self, request, *args, **kwargs):
        ret = {"code" : -1, "desc" : ""}
        addon = AddonFile.objects.first()
        if addon is None or os.path.exists(os.path.join(settings.BASE_DIR, addon.addonfile.path)) is not True:
            return JsonResponse(ret)
        ret["code"] = 1
        ret["version"] = addon.version
        return JsonResponse(ret)

class ApiEndpoint_AddonDownload(View):
    def get(self, request, *args, **kwargs):
        addon = AddonFile.objects.first()
        if addon is None or os.path.exists(os.path.join(settings.BASE_DIR, addon.addonfile.path)) is not True:
            ret = {"code" : -1, "desc" : "Addon Not Found"}
            return JsonResponse(ret)
        with open(addon.addonfile.path, 'rb') as f:
            response = HttpResponse(f, content_type='application/force-download')
            response['Content-Length'] = len(response.content)
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(addon.addonfile.path)
            return response


class StoryBoardEditorView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'storyboard.html')

class StoryBoardAccessView(View):
    def get(self, request, *args, **kwargs):
        #logger.info('storyboard access has been called')
        application = Application.objects.filter(name="storyboard").first()

        headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'Authorization' : 'Basic {}'.format(b64encode("{}:{}".format(application.client_id, application.client_secret).encode("ascii")).decode("ascii"))
        }
        data = {'grant_type': 'authorization_code', 'code': request.GET['code']}
        response = requests.post("{0}://{1}/o/token/".format(request.scheme, request.get_host()), data=data, headers=headers)
        return redirect('/xbmccontrol/sbeditor?code={}'.format(response.json()['access_token']))


class StoryNotepadSaveView(ProtectedResourceView):
    def post(self, request, *args, **kwargs):
        user = User.objects.filter(username=request.resource_owner).first()
        notememo = StoryNotepad()
        notememo.author = user
        notememo.content = request.body.decode('utf-8')
        notememo.updDate = now()
        notememo.save()
        return HttpResponse('note has been stored!')

class StoryNotepadLoadView(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        user = User.objects.filter(username=request.resource_owner).first()
        notememo = StoryNotepad.objects.filter(author=user).first()
        return JsonResponse(json.loads(notememo.content), safe=False)

class StoryBoardSaveView(ProtectedResourceView):
    def post(self, request, *args, **kwargs):
        
        story = StoryBoard.objects.filter(name=request.POST['title']).first()
        if story is None:
            story = StoryBoard()

        strMd5 = utility.getBinaryMd5(story.serv_file)
        if strMd5 != story.md5:
            story.serv_file = request.FILES['payload'].read()
            story.md5 = strMd5
            story.name = request.POST['title']
            story.content = request.POST['content']
            story.updDate = now()
            story.save()

        return HttpResponse('story has been stored!')

class StoryBoardLoadView(ProtectedResourceView):
    def post(self, request, *args, **kwargs):

        story = StoryBoard.objects.filter(name=request.POST['title']).first()

        ret = {"code" : -1, "desc" : "찾을 수 없는 제목."}
        if story is not None:
            ret["code"] = 1
            ret["content"] = story.content
            ret["desc"] = story.name

        return JsonResponse(ret)

class StoryBoardView(View):
    def get(self, request, *args, **kwargs):
        storypath = os.path.join(StoryBoard.STORY_PATH, request.GET['id'])
        logger.info(os.path.join(storypath, 'index.html'))
        if os.path.exists(os.path.join(storypath, 'index.html')) is not True:
            story = StoryBoard.objects.filter(idx=request.GET['id']).first()
            if story is None:
                return HttpResponse('story view is not ready!')
            if os.path.exists(storypath) is not True:
                os.makedirs(storypath)

            with open(os.path.join(storypath, 'story.zip'), 'wb+') as storyzipped:
                storyzipped.write(story.serv_file)

            story_zip = zipfile.ZipFile(os.path.join(storypath, 'story.zip'))
            story_zip.extractall(storypath)
            story_zip.close()
            os.remove(os.path.join(storypath, 'story.zip'))

        return redirect('/xbmccontrol/story/{}/index.html'.format(request.GET['id']))
