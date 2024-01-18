from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from os.path import splitext


# 桌位表
class Table(models.Model):
    table_number = models.PositiveIntegerField(verbose_name='桌号', unique=True)

    def __str__(self):
        return str(self.table_number)


# 菜品分类表
class DishCategory(models.Model):
    category = models.CharField(max_length=200, verbose_name='菜品类别', unique=True)

    def __str__(self):
        return self.category


# 菜品单位表
class DishUnit(models.Model):
    unit = models.CharField(max_length=200, verbose_name='菜品单位', unique=True)

    def __str__(self):
        return self.unit


# 菜品图片表
class DishImage(models.Model):
    file = models.ImageField(upload_to='images/', verbose_name='菜品图片', unique=True)
    name = models.CharField(max_length=200, verbose_name='菜品图片名称', blank=True)

    def __str__(self):
        return self.name


# 菜品表
class Dish(models.Model):
    category = models.ForeignKey(DishCategory, on_delete=models.CASCADE, verbose_name='菜品所属分类')
    specification = models.CharField(max_length=200, verbose_name='菜品规格', blank=True)
    file = models.ForeignKey(DishImage, on_delete=models.CASCADE, verbose_name='菜品图片')
    name = models.CharField(max_length=200, verbose_name='菜品名称', unique=True)
    unit = models.ForeignKey(DishUnit, on_delete=models.CASCADE, verbose_name='菜品单位')
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='菜品单价')
    is_on_sale = models.BooleanField(default=True, verbose_name='是否在售')

    def __str__(self):
        return self.name


# 订单表
class Order(models.Model):
    transaction_time = models.DateTimeField(auto_now_add=True, verbose_name='交易时间')
    table = models.ForeignKey(Table, on_delete=models.CASCADE, verbose_name='桌号')
    number_of_people = models.PositiveIntegerField(verbose_name='用餐人数')
    total_amount = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='交易金额', blank=True, null=True)
    transaction_status = models.CharField(max_length=200, verbose_name='交易状态', default='未结账')

    # 添加一个条件来检查total_amount是否已经改变，如果没有改变，就不需要再次保存
    def save(self, *args, **kwargs):
        old_total_amount = self.total_amount
        super().save(*args, **kwargs)
        if old_total_amount != self.total_amount:
            super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


# 菜品详情表
class DishDetail(models.Model):
    order_time = models.DateTimeField(auto_now_add=True, verbose_name='下单时间')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, verbose_name='菜品id',
                             limit_choices_to={'is_on_sale': True})
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='订单id')
    quantity = models.PositiveIntegerField(verbose_name='菜品下单数量')
    total_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='总价', blank=True, null=True)

    def __str__(self):
        return f'{self.dish.name} - {self.order.id}'


# 员工表
class Employee(models.Model):
    GENDER_CHOICES = (
        ('男', '男'),
        ('女', '女'),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    employee_number = models.CharField(max_length=200, verbose_name='工号', unique=True)
    name = models.CharField(max_length=200, verbose_name='姓名')
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, verbose_name='性别')
    position = models.CharField(max_length=200, verbose_name='职位')
    is_resigned = models.BooleanField(default=False, verbose_name='是否离职')

    def __str__(self):
        return self.name


# 在保存DishImage之前，将DishImage的name赋值为图片的名称
@receiver(pre_save, sender=DishImage)
def save_image_name(sender, instance, **kwargs):
    if not instance.name:
        print(instance.file.name)
        instance.name = splitext(instance.file.name)[0]


# 在保存DishDetail之前，计算total_price
@receiver(pre_save, sender=DishDetail)
def calculate_total_price(sender, instance, **kwargs):
    instance.total_price = instance.dish.price * instance.quantity


# 在保存DishDetail之后，更新相关的Order的total_amount
@receiver(post_save, sender=DishDetail)
def update_order_total_amount(sender, instance, **kwargs):
    order = instance.order
    order.total_amount = sum(detail.total_price for detail in order.dishdetail_set.all())
    order.save()
