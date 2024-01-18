# serializers.py
from rest_framework import serializers
from .models import Table, DishCategory, DishUnit, DishImage, Dish, Order, DishDetail, Employee


# 桌位表序列化
class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'


# 菜品分类表序列化
class DishCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DishCategory
        fields = '__all__'


# 菜品单位表序列化
class DishUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = DishUnit
        fields = '__all__'


# 菜品图片表序列化
class DishImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DishImage
        fields = '__all__'


# 菜品表序列化
class DishSerializer(serializers.ModelSerializer):
    dish_unit = serializers.SerializerMethodField()  # 菜品单位
    dish_category = serializers.SerializerMethodField()  # 菜品规格
    dish_url = serializers.SerializerMethodField()  # 菜品图片url

    class Meta:
        model = Dish
        fields = '__all__'

    def get_dish_unit(self, obj):
        return obj.unit.unit

    def get_dish_category(self, obj):
        return obj.category.category

    # obj.file.file.url只会返回相对URL。为了获取完整的URL，需要使用request.build_absolute_uri()方法
    def get_dish_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file.file, 'url'):
            return request.build_absolute_uri(obj.file.file.url)
        return None


# 订单表序列化
class OrderSerializer(serializers.ModelSerializer):
    transaction_time = serializers.SerializerMethodField()
    dish_details = serializers.SerializerMethodField()  # 新增字段

    class Meta:
        model = Order
        fields = '__all__'

    def get_transaction_time(self, obj):
        return obj.transaction_time.strftime("%Y-%m-%d %H:%M:%S")

    def get_dish_details(self, obj):
        dish_details = DishDetail.objects.filter(order=obj)
        return DishDetailSerializer(dish_details, many=True).data


# 菜品详情表序列化
class DishDetailSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()  # 菜品名称
    unit = serializers.SerializerMethodField()  # 菜品单位
    specification = serializers.SerializerMethodField()  # 菜品规格

    class Meta:
        model = DishDetail
        fields = '__all__'

    def get_name(self, obj):
        return obj.dish.name

    def get_unit(self, obj):
        return obj.dish.unit.unit

    def get_specification(self, obj):
        return obj.dish.specification


# 员工表序列化
class EmployeeSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = '__all__'

    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")
