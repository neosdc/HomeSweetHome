from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from xbmccontrolroom.models import MediaFile

class HouseholdAccountBook(models.Model):
    """장부"""
    idx = models.AutoField(primary_key=True, verbose_name='식별자')
    name = models.CharField(max_length=50, verbose_name='장부 이름')

    def __str__(self):
        return self.name


class PaymentMethod(models.Model):
    """지불 수단"""

    INUSE = 1
    NOTWORKING = 0
    TYPEFLAG_CHOICES = (
        (INUSE, '사용중'),
        (NOTWORKING, '사용불가')
    )
    idx = models.AutoField(primary_key=True, verbose_name='식별자')
    name = models.CharField(max_length=50, verbose_name='지불 수단 명칭')
    thumbnail_image = models.ImageField(upload_to=settings.PAYMENTMETHOD_THUMBNAIL_URL, blank=True, verbose_name='이미지')
    type_flag = models.IntegerField(default=INUSE, choices=TYPEFLAG_CHOICES, verbose_name='사용 여부', help_text='1 사용, 0 미사용')

    def __str__(self):
        return self.name

class Person(models.Model):
    """구성원"""
    class Meta:
        verbose_name_plural = 'People'
    idx = models.AutoField(primary_key=True, verbose_name='식별자')
    name = models.CharField(max_length=20, verbose_name='이름')

    def __str__(self):
        return self.name

class Event(models.Model):
    """이벤트"""
    CLOSED = 0
    OPEN = 1
    ONGOING_CHOICES = (
        (CLOSED, '종료'),
        (OPEN, '진행')
    )
    class Meta:
        verbose_name_plural = 'Events'

    idx = models.AutoField(primary_key=True, verbose_name='식별자')
    name = models.CharField(max_length=50, verbose_name='이름')
    thumbnail_image = models.ForeignKey(MediaFile, on_delete=models.SET_NULL, related_name='%(class)s_relation_thumbnail', blank=True, null=True, verbose_name='썸네일')
    medias = models.ForeignKey(MediaFile, on_delete=models.SET_NULL, related_name='%(class)s_relation_medias', blank=True, null=True, verbose_name='관련 미디어 파일')
    ongoing = models.IntegerField(default=0, choices=ONGOING_CHOICES, verbose_name='진행 여부')

    def __str__(self):
        return self.name

class Deal(models.Model):
    """거래"""

    INCOME = 1
    EXPENSE = 0
    TYPEFLAG_CHOICES = (
        (INCOME, '수입'),
        (EXPENSE, '지출')
    )

    idx = models.AutoField(primary_key=True, verbose_name='식별자')
    accountbook = models.ForeignKey(HouseholdAccountBook, on_delete=models.CASCADE, verbose_name='기입 장부')
    title = models.CharField(max_length=100, verbose_name='내용')
    type_flag = models.IntegerField(default=EXPENSE, choices=TYPEFLAG_CHOICES, verbose_name='지출 구분')
    paymentmethod = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, default=1, verbose_name='결제 수단')
    amount = models.IntegerField(default=0, verbose_name='금액')
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='구성원')
    longitude = models.DecimalField(max_digits=20, decimal_places=17, blank=True, null=True, validators=[
        MaxValueValidator(180),
        MinValueValidator(-180)
        ], verbose_name='경도')
    latitude = models.DecimalField(max_digits=20, decimal_places=18, blank=True, null=True, validators=[
        MaxValueValidator(90),
        MinValueValidator(-90)
        ], verbose_name='위도')
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='주소')
    receipt = models.ImageField(upload_to=settings.DEAL_RECEIPT_URL, blank=True, max_length=1000, verbose_name='첨부 파일', help_text='영수증')
    attached_file = models.FileField(upload_to=settings.DEAL_ATTACHED_URL, blank=True, max_length=1000, verbose_name='첨부 파일', help_text='내역서, 설명서 등')
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='관련 이벤트')
    memo = models.CharField(max_length=255, blank=True, null=True, verbose_name='메모')
    regDate = models.DateTimeField(verbose_name='등록 일시')

    def __str__(self):
        return "({3})[{0}]({1:,}){2}".format([item[1] for item in self.TYPEFLAG_CHOICES if item[0] == self.type_flag][0], self.amount, self.title, self.regDate.strftime("%y/%m/%d %H:%M"))

class Product(models.Model):
    """제품"""
    idx = models.AutoField(primary_key=True, verbose_name='식별자')
    name = models.CharField(max_length=100, verbose_name='품명')
    category = models.CharField(max_length=50, verbose_name='분류')
    maker = models.CharField(max_length=50, verbose_name='제조사')
    thumbnail_image = models.ImageField(upload_to=settings.PRODUCT_THUMBNAIL_URL, blank=True, verbose_name='이미지')

    NORMAL = 0
    LACK = 1
    CART = 2
    TYPEFLAG_CHOICES = (
        (NORMAL, '정상'),
        (LACK, '부족'),
        (CART, '카트'),
    )
    type_flag = models.IntegerField(default=NORMAL, choices=TYPEFLAG_CHOICES, verbose_name='상태', help_text='0 정상, 1 부족, 2 카트')

    def __str__(self):
        return self.name

class ProductRelation(models.Model):
    """관련 제품"""
    CONSUMABLE = 0
    COMPONENT = 1
    RELATION_CHOICES = (
        (CONSUMABLE, '소모품'),
        (COMPONENT, '구성품')
    )
    class Meta:
        unique_together = (('master', 'slave'),)
    master = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='%(class)s_relation_master', verbose_name='상위')
    slave = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='%(class)s_relation_slave', verbose_name='하위')
    relation = models.IntegerField(default=CONSUMABLE, choices=RELATION_CHOICES, verbose_name='유형')

class Package(models.Model):
    """상품"""
    idx = models.AutoField(primary_key=True, verbose_name='식별자')
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, verbose_name='거래')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='제품')
    quantity = models.PositiveIntegerField(default=1, verbose_name='수량')
    price = models.PositiveIntegerField(default=1, verbose_name='금액')

    def __str__(self):
        return "{0}:{1}({2:,})".format(self.product.name, self.quantity, self.price)

class Asset(models.Model):
    """자산"""
    CASHABLE = 0
    SPOTGOODS = 1
    BOND = 2
    SECURITIES = 3
    FOREIGNEXCHANGE = 4
    TYPEFLAG_CHOICES = (
        (CASHABLE, '현금성'),
        (SPOTGOODS, '현물'),
        (BOND, '채권'),
        (SECURITIES, '유가증권'),
        (FOREIGNEXCHANGE, '외환')
    )
    idx = models.AutoField(primary_key=True, verbose_name='식별자')
    name = models.CharField(max_length=100, verbose_name='자산 명칭')
    abbreviation = models.CharField(max_length=10, verbose_name='자산 약칭')
    type_flag = models.IntegerField(default=CASHABLE, choices=TYPEFLAG_CHOICES, verbose_name='유형 구분')
    thumbnail_image = models.ImageField(upload_to=settings.ASSET_THUMBNAIL_URL, blank=True, verbose_name='이미지')
    balance = models.IntegerField(default=0, verbose_name='잔고')
    cost = models.DecimalField(max_digits=20, decimal_places=10, default=0, verbose_name='획득비용')
    def __str__(self):
        return "({1}){0}".format(self.name, self.abbreviation)

    def calcBalanceAndCost(self, amount, price):
        if amount > 0:
            self.cost = (self.balance * self.cost + price) / (self.balance + amount)
        elif amount < 0:
            if self.balance * self.cost - price == 0 or self.balance + amount == 0:
                self.cost = 0
            else:
                self.cost = (self.balance * self.cost - price) / (self.balance + amount)
        
        self.calcBalance(amount)

    def calcBalance(self, amount):
        self.balance = self.balance + amount
        if self.balance == 0:
            self.cost = 0

class Wealth(models.Model):
    """재산"""
    class Meta:
        verbose_name_plural = 'Wealth'
    idx = models.AutoField(primary_key=True, verbose_name='식별자')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='%(class)s_relation_asset', verbose_name='자산')
    amount = models.IntegerField(default=0, verbose_name='수량')
    price = models.DecimalField(max_digits=20, decimal_places=4, default=0, verbose_name='금액')
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, blank=True, null=True, verbose_name='관련 거래')
    
    def __str__(self):
        return "({0}){1:,}".format(self.asset.abbreviation, self.amount)

    def calcChangeNew(self):
        self.asset = Asset.objects.filter(idx=self.asset.idx).first()
        if self.amount < 0:
            self.price = abs(self.amount) * self.asset.cost
            self.save()
            self.asset.calcBalance(self.amount)
        elif self.amount > 0:
            self.asset.calcBalanceAndCost(self.amount, self.price)
        self.asset.save()
    def calcChangeDelete(self):
        self.asset = Asset.objects.filter(idx=self.asset.idx).first()
        self.asset.calcBalanceAndCost(self.amount * -1, self.price)
        self.asset.save()
    def calcChangeUpdate(self, orig):
        assetorig = Asset.objects.filter(idx=orig.asset.idx).first()
        assetorig.calcBalanceAndCost(-orig.amount, orig.price)
        assetorig.save()
        if self.asset.idx != orig.asset.idx:
            self.asset = Asset.objects.filter(idx=self.asset.idx).first()
        if self.amount < 0:
            self.price = abs(self.amount) * self.asset.cost
            self.save()
        elif self.amount > 0:
            self.asset.calcBalanceAndCost(self.amount, self.price)
        self.asset.save()
