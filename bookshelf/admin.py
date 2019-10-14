from django.contrib import admin
from django import forms
from datetime import timedelta, datetime
from .models import *
from accountbook.admin import *

@admin.register(Book)
class BookModelAdmin(HSHAdmin):
    "전자책"
    class PathBookFilter(ComboFilter):
        title = '경로'
        parameter_name = 'path_book_filter'
        template = 'admin/book_path_combo_filter.html'

        def lookups(self, request, model_admin):
            pathes = Book.objects.values('path').distinct()
            items = []
            if self.value() is None:
                selected_path_count = len(Book.BOOKS_PATH) + 1
                selected_path_depth = 0
            else:
                selected_path_count = len(self.value()) + 1
                selected_path_depth = self.value().replace(Book.BOOKS_PATH, '').count(os.sep)
                if selected_path_depth > 0:
                    items.append((os.path.dirname(self.value()), os.path.dirname((self.value().replace(Book.BOOKS_PATH, '')))))
            tested = []
            for path in pathes:
                target_path = path['path'] if path['path'].find(os.sep, selected_path_count) == -1 else path['path'][0:path['path'].find(os.sep, selected_path_count)]
                if target_path in tested:
                    continue
                tested.append(target_path)
                if self.value() is None or self.value() in target_path:
                    repr_path = target_path.replace(Book.BOOKS_PATH, '')
                    if repr_path.count(os.sep) == selected_path_depth + 1 or (selected_path_depth == 0 and repr_path.count(os.sep) == 0):
                        items.append((target_path, repr_path))
            return items
        def queryset(self, request, queryset):
            return queryset.filter(path=self.value()) if self.value() else queryset

    list_display = ['name', 'size_count', 'view_file', 'tag_list']
    list_filter = [PathBookFilter, TagMediaFileInputFilter]
    class BookModelForm(forms.ModelForm):
        class Meta:
            model = Book
            exclude = ['size']
    form = BookModelForm
    readonly_fields = ['name', 'path', 'md5', 'size_count']
    def size_count(self, obj):
        filesize = self.get_filesize(obj.size)
        return self.formed_html_numeric(filesize[0], filesize[1], lambda x: "{0:.2f}{1}".format(x, filesize[2]))
    def view_file(self, obj):
        mimetype = mimetypes.guess_type(obj.name)
        if mimetype is None or mimetype[0] is None:
            return ''
        url = '/bookshelf/api/download?idx=' + str(obj.idx)
        return format_html('<a href="{0}" title="{1}" type="{2}">다운로드</a>'.format(url, obj.name, mimetype[0]))
    view_file.short_description = '보기'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')
    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())
    tag_list.short_description = '태그'
