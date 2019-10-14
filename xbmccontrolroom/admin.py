from django.contrib import admin
from django import forms
from datetime import timedelta, datetime
from .models import *
from accountbook.admin import *
from django.db.models import Q

admin.site.register(XbmcMediaHost)
admin.site.register(AddonFile)
admin.site.register(StoryNotepad)
@admin.register(StoryBoard)
class StoryBoardModelAdmin(HSHAdmin):

    class StoryBoardModelForm(forms.ModelForm):
        thumbnail_image = forms.ModelChoiceField(required=False, queryset=MediaFile.objects.filter(thumbnail__gt=0), widget=AdminMediaFileWidget())
        class Meta:
            model = StoryBoard
            exclude = []
    form = StoryBoardModelForm
    list_display = ['name', 'tag_list', 'view_file']
    list_filter = [TagMediaFileInputFilter]
    readonly_fields = ['content', 'md5']
    def view_file(self, obj):
        url = '/xbmccontrol/sbview?id=' + str(obj.idx)
        return format_html('<a href="{0}" title="{1}" target="_blank">보기</a>'.format(url, obj.name))
    view_file.short_description = '보기'
    def thumbnail_image(self, obj):
        return obj.thumbnail_image()

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())
    tag_list.short_description = '태그'


@admin.register(MediaFile)
class MediaFileModelAdmin(HSHAdmin):
    "미디어 파일"
    class PathMediaFileFilter(ComboFilter):
        title = '경로'
        parameter_name = 'path_mediafile_filter'
        template = 'admin/mediafile_path_combo_filter.html'

        def lookups(self, request, model_admin):
            pathes = MediaFile.objects.values('path').distinct()
            items = []
            if self.value() is None:
                selected_path_count = len(MediaFile.MEDIAS_PATH) + 1
                selected_path_depth = 0
            else:
                selected_path_count = len(self.value()) + 1
                selected_path_depth = self.value().replace(MediaFile.MEDIAS_PATH, '').count(os.sep)
                if selected_path_depth > 0:
                    items.append((os.path.dirname(self.value()), os.path.dirname((self.value().replace(MediaFile.MEDIAS_PATH, '')))))
            tested = []
            for path in pathes:
                target_path = path['path'] if path['path'].find(os.sep, selected_path_count) == -1 else path['path'][0:path['path'].find(os.sep, selected_path_count)]
                if target_path in tested:
                    continue
                tested.append(target_path)
                if self.value() is None or self.value() in target_path:
                    repr_path = target_path.replace(MediaFile.MEDIAS_PATH, '')
                    if repr_path.count(os.sep) == selected_path_depth + 1:
                        items.append((target_path, repr_path))
            return items
        def queryset(self, request, queryset):
            return queryset.filter(path=self.value()) if self.value() else queryset

    list_display = ['name', 'size_count', 'thumbnail', 'view_file', 'tag_list']
    list_filter = [PathMediaFileFilter, 'thumbnail', TagMediaFileInputFilter]
    class MediaFileModelForm(forms.ModelForm):
        class Meta:
            model = MediaFile
            exclude = ['size']
    form = MediaFileModelForm
    readonly_fields = ['name', 'path', 'thumbnail_image', 'md5', 'size_count']
    def size_count(self, obj):
        filesize = self.get_filesize(obj.size)
        return self.formed_html_numeric(filesize[0], filesize[1], lambda x: "{0:.2f}{1}".format(x, filesize[2]))

    def view_file(self, obj):
        return HSHAdmin.formed_media_file(obj)
    view_file.short_description = '보기'
    def thumbnail_image(self, obj):
        return obj.thumbnail_image()

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())
    tag_list.short_description = '태그'

    


@admin.register(OnAir)
class OnAirModelAdmin(admin.ModelAdmin):
    """XBMC 호스트 활성 상태 관리"""
    def get_queryset(self, request):
        now = datetime.now()
        before_now = now + timedelta(hours=-1)
        #1시간 내에 Ping 호출된 호스트만 활성으로 간주
        queryset = super().get_queryset(request).filter(updDate__range=(before_now, now))
        return queryset