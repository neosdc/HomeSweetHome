import os
import mimetypes
from functools import reduce
from datetime import timedelta, datetime
from django import forms
from django.contrib import admin
from django.db import models
from django.db.models import Avg, Sum, F, Q
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.widgets import *
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from rangefilter.filter import DateRangeFilter
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import *

import logging
from django.forms.models import BaseInlineFormSet

logger = logging.getLogger(__name__)

admin.site.site_header = "Home Sweet Home"
admin.site.site_title = "HSH Portal Admin"
admin.site.index_title = "Welcome to Home Sweet Home Admin"

class InputFilter(admin.SimpleListFilter):
    template = 'admin/input_filter.html'
    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return ((),)
    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice

class ComboFilter(admin.SimpleListFilter):
    template = 'admin/combo_filter.html'
    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice

class TagMediaFileInputFilter(InputFilter):
    parameter_name = 'tag_input_filter'
    title = 'Tag'
    def queryset(self, request, queryset):
        term = self.value()
        if term is None:
            return
        tag = Q()
        for bit in term.split():
            tag &= (
                Q(tags__name__in=[bit])
            )
        return queryset.filter(tag)

class AdminImageWidget(AdminFileWidget):
    """이미지 파일 업로드 컨트롤"""
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        if str(value) and value is not None:
            url = os.path.join('/', str(value))
            output.append('<div><a href="{0}" target="_blank" class="gallery_source"><img src="{0}" alt="{1}" style="max-height: 300px; max-width: 300px;"/></a></div>'
                          .format(url, value))
        output.append(super().render(name, value, attrs))
        return mark_safe(u''.join(output))

class HSHAdmin(ImportExportModelAdmin):
    """모델에 위젯 적용한 베이스 클래스"""
    formfield_overrides = {
        models.ImageField: {'widget': AdminImageWidget},
    }

    TIMEDIFF_SECONDS_RECENT = 10

    @staticmethod
    def formed_html_numeric(obj, size=None, formed=None):
        """형식 적용된 숫자 출력 HTML Tag"""

        obj = formed(obj) if formed else format(obj if obj is not None else 0, ',')

        if size:
            return format_html(
                '<div style="width:100%;height:100%;text-align:right;"><font size="{1}">{0}</font></div>',
                obj, size
            )
        else:
            return format_html(
                '<div style="width:100%;height:100%;text-align:right;">{0}</div>',
                obj
            )

    @staticmethod
    def get_filesize(size):
        power = 2**10
        n = 0
        Dic_powerN = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
        while size > power:
            size /= power
            n += 1
        return (size, n+1, Dic_powerN[n]+'B')

    @staticmethod
    def get_interval_timediff_seconds(obj, child=False):
        """일시와 현재로 부터 차이"""
        formed_string = ""
        if obj > 31536000:
            formed_string = "{}년".format(int(obj // 31536000))
            if obj % 31536000 > 2592000 and child is False:
                formed_string += HSHAdmin.get_interval_timediff_seconds(obj % 31536000, True)
        elif obj > 2592000:
            formed_string = "{}개월".format(int(obj // 2592000))
            if obj % 2592000 > 86400 and child is False:
                formed_string += HSHAdmin.get_interval_timediff_seconds(obj % 2592000, True)
        elif obj > 86400:
            formed_string = "{}일".format(int(obj // 86400))
            if obj % 86400 > 3600 and child is False:
                formed_string += HSHAdmin.get_interval_timediff_seconds(obj % 86400, True)
        elif obj > 3600:
            formed_string = "{}시간".format(int(obj // 3600))
            if obj % 3600 > 60 and child is False:
                formed_string += HSHAdmin.get_interval_timediff_seconds(obj % 3600, True)
        elif obj > 60:
            formed_string = "{}분".format(int(obj // 60))
            if obj % 60 > 0 and child is False:
                formed_string += HSHAdmin.get_interval_timediff_seconds(obj % 60, True)
        else:
            formed_string = "{}초".format(int(obj))
        return formed_string

    @staticmethod
    def formed_html_datetime(obj):
        """형식 적용된 일시 출력 HTML Tag"""
        formed_string = ""
        total_seconds = (datetime.now() - obj).total_seconds()
        if total_seconds < -HSHAdmin.TIMEDIFF_SECONDS_RECENT:
            formed_string = "후"
        elif total_seconds > HSHAdmin.TIMEDIFF_SECONDS_RECENT:
            formed_string = "전"
        else:
            formed_string = "현재"

        return format_html(
            '{}<br />({})',
            obj.strftime("%y/%m/%d %H:%M:%S"),
            HSHAdmin.get_interval_timediff_seconds(total_seconds),
            formed_string
        )

    file_formats = [".AVI", ".MPG", ".WMV", ".ASF", ".FLV", ".MKV", ".MKA", ".MP4", ".RM", ".OGM", ".3GP", ".BMP", ".JPG", ".GIF", ".ICO", ".PCX", ".TGA", ".PNG", ".MNG"]
    @staticmethod
    def formed_html_file(obj):
        """형식 적용된 파일 출력 HTML Tag"""
        if obj is not None and str(obj):
            fname, ext = os.path.splitext(obj.name)
            filetypeicon = 'File'
            if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), settings.FILETYPE_ICON_URL, ext.replace('.', '').lower() + ".png")):
                filetypeicon = '<img src="{}" style="max-height: 32px; max-width: 32px;"></img>'.format(os.path.join('/', settings.FILETYPE_ICON_URL, ext.replace('.', '').lower() + ".png"))

            if ext.upper() in HSHAdmin.file_formats:
                return mark_safe('<div style="width:100%;height:100%;text-align:center;"><a href="{0}" target="_blank" class="gallery_source">{1}</a></div>'.format(os.path.join('/', str(obj)), filetypeicon))

            return mark_safe('<div style="width:100%;height:100%;text-align:center;"><a href="{0}" target="_blank">{1}</a></div>'.format(os.path.join('/', str(obj)), filetypeicon))
        return ''

    @staticmethod
    def formed_media_file(obj):
        mimetype = mimetypes.guess_type(obj.name)
        if mimetype is None or mimetype[0] is None:
            return ''

        if 'video' in mimetype[0]:
            url = '/xbmccontrol/api/mediastream?idx=' + str(obj.idx)
            return format_html('<a href="{0}" class="gallery_source" title="{1}" type="{2}">보기</a><button class="clipboard_copy">복사</button>'.format(url, obj.name, mimetype[0]))
        else:
            url = '/xbmccontrol/api/mediadownload?idx=' + str(obj.idx)
            return format_html('<a href="{0}" class="gallery_source" title="{1}" type="{2}">{3}</a><button class="clipboard_copy">복사</button>'.format(url, obj.name, mimetype[0], obj.thumbnail_image()))

    def thumbnail_image_tag(self, obj):
        if obj.thumbnail_image and hasattr(obj.thumbnail_image, 'url'):
            return format_html('<img src="{}" title="{}" />'.format(os.path.join('/', obj.thumbnail_image.url), str(obj)))
        return obj.name
    thumbnail_image_tag.short_description = '썸네일'


@admin.register(Product)
class ProductMethodModelAdmin(HSHAdmin):
    list_display = ('name', 'category', 'thumbnail_image_tag', 'type_flag')
    list_filter = ['type_flag', 'category']

    def apply_status_lack(self, modeladmin, request, queryset):
        for product in queryset:
            product.type_flag = (product.type_flag + 1) % 3
            product.save()
    apply_status_lack.short_description = '상태 변경'
    actions = [apply_status_lack, ]


@admin.register(PaymentMethod)
class PaymentMethodModelAdmin(HSHAdmin):
    list_display = ('name', 'thumbnail_image_tag', 'type_flag')


class WealthInlineFormSet(BaseInlineFormSet):
    def save_new_objects(self, commit=True):
        saved_instances = super(WealthInlineFormSet, self).save_new_objects(commit)
        if commit:            
            for obj in saved_instances:
                if isinstance(obj, Wealth):
                    obj.calcChangeNew()
        return saved_instances
    def save_existing_objects(self, commit=True):
        self.changed_objects = []
        self.deleted_objects = []
        if not self.initial_forms:
            return []
        saved_instances = []
        forms_to_delete = self.deleted_forms
        for form in self.initial_forms:
            obj = form.instance
            if obj.pk is None:
                continue
            if form in forms_to_delete:
                self.deleted_objects.append(obj)
                self.delete_existing(obj, commit=commit)
                if isinstance(obj, Wealth):
                    obj.calcChangeDelete()
            elif form.has_changed():
                if isinstance(obj, Wealth):
                    orig = Wealth.objects.filter(idx=obj.pk).first()
                    obj.calcChangeUpdate(orig)                    
                self.changed_objects.append((obj, form.changed_data))
                saved_instances.append(self.save_existing(form, obj, commit=commit))                
                if not commit:
                    self.saved_forms.append(form)
        return saved_instances


@admin.register(Deal)
class DealModelAdmin(HSHAdmin):
    """거래 관리"""
    class DealModelForm(forms.ModelForm):
        accountbook = forms.ModelChoiceField(required=True, queryset=HouseholdAccountBook.objects.all(), widget=forms.RadioSelect(), empty_label=None)
        type_flag = forms.ChoiceField(choices=Deal.TYPEFLAG_CHOICES, widget=forms.RadioSelect(attrs={'class':'radio_1', 'name': 'name2'}))
        event = forms.ModelChoiceField(required=False, queryset=Event.objects.filter(ongoing__gt=0))

        class Meta:
            model = Deal
            exclude = []

    form = DealModelForm

    class IsOngoinEventFilter(admin.SimpleListFilter):
        title = '이벤트'
        parameter_name = 'is_ongoing_Event'
        def lookups(self, request, model_admin):
            return Event.objects.filter(ongoing__gt=0).values_list('idx', 'name')
        def queryset(self, request, queryset):
            return queryset.filter(event=self.value()) if self.value() else queryset

    class PaymentMethodComboFilter(ComboFilter):
        title = '지불방법'
        parameter_name = 'deal_paymentmethod_filter'

        def lookups(self, request, model_admin):
            methods = PaymentMethod.objects.filter(type_flag=PaymentMethod.INUSE)
            ret = [(str(method.idx), method.name) for method in methods]
            ret.insert(0, (str(0), "All"))
            return ret
        def queryset(self, request, queryset):
            return queryset.filter(paymentmethod=self.value()) if self.value() is not None and self.value() != "0" else queryset

    class DealChangeList(ChangeList):
        def get_results(self, request):
            super().get_results(request)
            results = list(self.result_list)
            self.total_expense_amount = "{:,}".format(reduce(lambda x, y: x + y, map(lambda x: x.amount, filter(lambda x: x.type_flag == 0, results)), 0))
            self.total_income_amount = "{:,}".format(reduce(lambda x, y: x + y, map(lambda x: x.amount, filter(lambda x: x.type_flag == 1, results)), 0))

    def get_changelist(self, request, **kwargs):
        return DealModelAdmin.DealChangeList


    class DealResource(resources.ModelResource):
        class Meta:
            model = Deal
            exclude = ('receipt', 'attached_file')

    list_per_page = 20
    list_display = ['title', 'accountbook', 'type_flag', 'paymentmethod_formed', 'amount_formed', 'regdate_formed',
                    'receipt_tag', 'attached_file_link', 'package_count', 'wealth_count']
    list_filter = [('regDate', DateRangeFilter), 'accountbook__name',
                   'type_flag', PaymentMethodComboFilter, IsOngoinEventFilter]
    ordering = ['-regDate']
    search_fields = ['title', 'amount']
    resource_class = DealResource
    change_list_template = 'admin/accountbook/deal/change_list.html'

    class PackageInline(admin.TabularInline):
        model = Package
        extra = 0
        min_num = 0

    class WealthInline(admin.TabularInline):
        model = Wealth
        extra = 0
        min_num = 0
        formset = WealthInlineFormSet

    inlines = [PackageInline, WealthInline]

    def receipt_tag(self, obj):
        return HSHAdmin.formed_html_file(obj.receipt)
    receipt_tag.short_description = "영수증"
    def attached_file_link(self, obj):
        return HSHAdmin.formed_html_file(obj.attached_file)
    attached_file_link.short_description = "첨부"
    def package_count(self, obj):
        return HSHAdmin.formed_html_numeric(Package.objects.filter(deal=obj).count())
    package_count.short_description = "상품"
    def wealth_count(self, obj):
        return HSHAdmin.formed_html_numeric(Wealth.objects.filter(deal=obj).count())
    wealth_count.short_description = "관련 자산"
    def amount_formed(self, obj):
        return HSHAdmin.formed_html_numeric(obj.amount)
    amount_formed.short_description = "잔액"
    def regdate_formed(self, obj):
        return HSHAdmin.formed_html_datetime(obj.regDate)
    regdate_formed.short_description = "거래일시"
    def paymentmethod_formed(self, obj):
        return self.thumbnail_image_tag(obj.paymentmethod)
    paymentmethod_formed.short_description = "지불 방법"

    def changelist_view(self, request, extra_context=None):
        if 'regDate__gte' not in request.GET:
            if 'is_ongoing_Event' not in request.GET:
                request_params = request.GET.copy()
                request_params['regDate__gte'] = (datetime.now() + timedelta(days=-7)).date().__str__()
                request_params['regDate__lte'] = datetime.now().date().__str__()
                request.GET = request_params
                request.META['QUERY_STRING'] = request.GET.urlencode()
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Asset)
class AssetModelAdmin(HSHAdmin):
    """자산 관리"""
    list_display = ('name', 'abbreviation', 'thumbnail_image_tag', 'type_flag', 'balance_formed', 'cost_formed')
    search_fields = ('name', 'abbreviation')


    def balance_formed(self, obj):
        return HSHAdmin.formed_html_numeric(obj.balance)
    balance_formed.short_description = "잔고"
    def cost_formed(self, obj):
        return HSHAdmin.formed_html_numeric(obj.cost)
    cost_formed.short_description = "단가"
    

class AdminMediaFileWidget(forms.Select):
    """미디어 파일 컨트롤"""
    def __init__(self):
        super().__init__()

    def render(self, name, value, attrs=None, renderer=None):
        output = []        
        if str(value) and value is not None:
            mediaFile = MediaFile.objects.filter(idx=value).first()
            if mediaFile is not None:
                output.append(HSHAdmin.formed_media_file(mediaFile))
                output.append('<br />')
        output.append(super().render(name, value, attrs))
        return mark_safe(u''.join(output))
    

@admin.register(Event)
class EventModelAdmin(HSHAdmin):

    class EventModelForm(forms.ModelForm):
        thumbnail_image = forms.ModelChoiceField(required=False, queryset=MediaFile.objects.filter(thumbnail__gt=0), widget=AdminMediaFileWidget())
        medias = forms.ModelChoiceField(required=False, queryset=MediaFile.objects.filter(thumbnail__gt=0), widget=AdminMediaFileWidget())
        class Meta:
            model = Event
            exclude = []

    def thumbnail_image_tag(self, obj):
        if obj.thumbnail_image and hasattr(obj.thumbnail_image, 'name'):
            return obj.thumbnail_image.thumbnail_image()            
        return ''

    def medias_path(self, obj):
        if obj.medias and hasattr(obj.medias, 'path'):
            return obj.medias.path
    medias_path.short_description = '미디어 경로'
    form = EventModelForm
    list_display = ['name', 'ongoing', 'thumbnail_image_tag', 'medias_path', 'deals_link']
    ordering = ['-ongoing']
    search_fields = ['name']

    def deals_link(self, event):
        url = reverse("admin:accountbook_deal_changelist")
        link = '<a href="{}?is_ongoing_Event={}">{}</a>'.format(url, str(event.idx), str(Deal.objects.filter(event=event.idx).count()) + '건 보기')
        return mark_safe(link)
    deals_link.short_description = '거래 목록'

@admin.register(Wealth)
class WealthModelAdmin(HSHAdmin):
    """자산 관리"""
    class WealthModelForm(forms.ModelForm):
        class Meta:
            model = Wealth
            exclude = ['deal']
    form = WealthModelForm

    list_display = ('asset', 'amount_formed', 'price_formed', 'deal')

    def amount_formed(self, obj):
        return HSHAdmin.formed_html_numeric(obj.amount)
    amount_formed.short_description = "수량"
    def price_formed(self, obj):
        return HSHAdmin.formed_html_numeric(obj.price)
    price_formed.short_description = "금액"

    class EarningsOrSpendingFilter(admin.SimpleListFilter):
        title = '획득, 소비'
        parameter_name = 'earning_spending'
        def lookups(self, request, model_admin):
            return [('1', '획득'), ('2', '소비')]
        def queryset(self, request, queryset):
            return queryset if self.value() is None else queryset.filter(Q(amount__gt=0) if self.value() == '1' else Q(amount__lt=0))

    list_filter = ['asset__name', EarningsOrSpendingFilter]

admin.site.register(HouseholdAccountBook)
admin.site.register(ProductRelation)
admin.site.register(Person)

@admin.register(Package)
class PackageModelAdmin(HSHAdmin):
    """구매 제품 관리"""

    list_display = ('product', 'price_formed', 'quantity_formed', 'price_avg', 'deal')
    def price_avg(self, obj):
        return HSHAdmin.formed_html_numeric(obj.price / (obj.quantity if obj.quantity != 0 else 1))
    price_avg.short_description = "단가"
    def price_formed(self, obj):
        return HSHAdmin.formed_html_numeric(obj.price)
    price_formed.short_description = "금액"
    def quantity_formed(self, obj):
        return HSHAdmin.formed_html_numeric(obj.quantity)
    quantity_formed.short_description = "수량"
