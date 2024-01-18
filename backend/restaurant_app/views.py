# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_list_or_404
from django.db.models import Sum, F
from datetime import datetime, timedelta
from collections import defaultdict

from .models import Table, DishCategory, DishUnit, DishImage, Dish, Order, DishDetail, Employee
from .serializers import TableSerializer, DishCategorySerializer, DishUnitSerializer, DishImageSerializer, \
    DishSerializer, OrderSerializer, DishDetailSerializer, EmployeeSerializer


def get_time_range(period):
    """
    根据给定的时间段（'day'，'week'或'month'）返回一个时间范围。
    """
    now = datetime.now()
    if period == 'day':
        start_time = now - timedelta(days=1)
    elif period == 'week':
        start_time = now - timedelta(weeks=1)
    elif period == 'month':
        start_time = now - timedelta(days=30)
    else:
        raise ValueError('无效的时间段。')
    return start_time, now


def get_total_amount_statistics(queryset):
    """
    根据给定的订单查询集，返回一个字典，其中包含各个订单总价区间的数量。
    """
    ranges = [(0, 200), (200, 400), (400, 600), (600, 800), (800, 1000), (1000, 1200), (1200, 1400), (1400, 1600),
              (1600, 1800), (1800, 2000), (2000, float('inf'))]
    statistics = {f'{start}-{end if end != float("inf") else "inf"}': 0 for start, end in ranges}
    for order in queryset:
        for start, end in ranges:
            if start <= order.total_amount < end:
                statistics[f'{start}-{end if end != float("inf") else "inf"}'] += 1
                break
    return statistics


# 桌位表视图
class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all().order_by('table_number')
    serializer_class = TableSerializer
    pagination_class = None  # 不分页
    # permission_classes = [IsAuthenticated]


# 菜品分类表视图
class DishCategoryViewSet(viewsets.ModelViewSet):
    queryset = DishCategory.objects.all().order_by('id')
    serializer_class = DishCategorySerializer
    pagination_class = None  # 不分页

    # permission_classes = [IsAuthenticated]

    # 按菜品分类销量排行榜：这个接口返回一个按菜品分类销量排行榜，支持按当周，当月二种形式返回每天各菜品分类的销量总数的统计数据。
    # 可以通过发送一个GET请求到/dish-category/sales-rank来使用这个接口。在请求的查询参数中，你可以提供一个名为period的参数，
    # 其值可以是’week’或’month’。
    #
    # 示例：GET /dish-category/sales-rank/?period=month
    @action(detail=False, methods=['get'], url_path='sales-rank')
    def sales_rank(self, request, *args, **kwargs):
        period = request.query_params.get('period', 'week')  # 默认为'week'
        if period not in ['week', 'month']:
            return Response({'msg': '无效的时间段。'}, status=400)

        start_date, end_date = get_time_range(period)
        queryset = DishDetail.objects.filter(order_time__range=(start_date, end_date)) \
            .extra({"date": "date(order_time)"}) \
            .values('date', 'dish__category__category') \
            .annotate(total_sales=Sum('quantity')) \
            .order_by('date', '-total_sales')

        # 对查询结果进行后处理，生成所需的数据结构
        result_dict = defaultdict(list)
        for item in queryset:
            result_dict[item['dish__category__category']].append({
                'date': item['date'],
                'total_sales': item['total_sales']
            })

        result = []
        for category, data in result_dict.items():
            result.append({
                'category': category,
                'data': data
            })

        return Response(result)


# 菜品单位表视图
class DishUnitViewSet(viewsets.ModelViewSet):
    queryset = DishUnit.objects.all().order_by('id')
    serializer_class = DishUnitSerializer
    pagination_class = None  # 不分页
    # permission_classes = [IsAuthenticated]


class DishImageViewSet(viewsets.ModelViewSet):
    queryset = DishImage.objects.all().order_by('-id')
    serializer_class = DishImageSerializer
    # permission_classes = [IsAuthenticated]


# 菜品表视图
class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all().order_by('-id')
    serializer_class = DishSerializer

    # permission_classes = [IsAuthenticated]

    # 菜品销量排行榜：这个接口返回一个菜品销量排行榜，支持按当日，当周，当月三个维度展示每个菜品销量总数的统计数据。
    # 可以通过发送一个GET请求到/dish/sales-rank来使用这个接口。在请求的查询参数中，可以提供一个名为period的参数，
    # 其值可以是’day’，‘week’或’month’。
    #
    # 示例：GET /dish/sales-rank/?period=day
    @action(detail=False, methods=['get'], url_path='sales-rank')
    def sales_rank(self, request, *args, **kwargs):
        period = request.query_params.get('period', 'day')  # 默认为'day'
        if period not in ['day', 'week', 'month']:
            return Response({'msg': '无效的时间段。'}, status=400)
        queryset = DishDetail.objects.filter(order_time__range=get_time_range(period)) \
            .values('dish__name').annotate(name=F('dish__name'), total_sales=Sum('quantity')) \
            .values('name', 'total_sales').order_by('-total_sales')
        return Response(queryset)


# 订单表视图
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-transaction_time')
    serializer_class = OrderSerializer

    # permission_classes = [IsAuthenticated]

    # 可以根据时间段，以及桌号对订单进行过滤
    # 例如：/order?start_time=2023-12-01T00:00:00Z&end_time=2023-12-31T23:59:59Z&table_number=1
    def get_queryset(self):
        queryset = super().get_queryset()
        start_time = self.request.query_params.get('start_time', None)
        end_time = self.request.query_params.get('end_time', None)
        table_number = self.request.query_params.get('table_number', None)

        if start_time is not None and end_time is not None:
            queryset = queryset.filter(transaction_time__range=[start_time, end_time])

        if table_number is not None:
            queryset = queryset.filter(table__table_number=table_number)

        return queryset.order_by('-transaction_time')

    # 订单销售总价区间统计：这个接口返回一个订单销售总价区间统计，支持按当日，当周，当月三个维度，按总价0-200，200-400，400-600，
    # 600-800，800-1000，1000-1200，1200-1400，1400-1600，1600-1800，1800-2000，2000及以上展示订单总价所在区间数量数据
    # 进行展示统计数据。可以通过发送一个GET请求到/orders/total-amount-statistics来使用这个接口。
    # 在请求的查询参数中，可以提供一个名为period的参数，其值可以是’day’，‘week’或’month’。
    #
    # 示例：GET /order/total-amount-statistics/?period=week
    @action(detail=False, methods=['get'], url_path='total-amount-statistics')
    def total_amount_statistics(self, request, *args, **kwargs):
        period = request.query_params.get('period', 'day')  # 默认为'day'
        if period not in ['day', 'week', 'month']:
            return Response({'msg': '无效的时间段。'}, status=400)
        queryset = Order.objects.filter(transaction_time__range=get_time_range(period))
        statistics = get_total_amount_statistics(queryset)

        # 对statistics进行处理，生成所需的数据结构
        result = []
        for ranges, stat in statistics.items():
            result.append({
                'ranges': ranges,
                'statistics': stat
            })

        return Response(result)

    # 重写retrieve方法。在返回响应之前，检查Order对象是否有相关的DishDetail对象，如果有，就更新total_amount
    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     if instance.dishdetail_set.exists():
    #         instance.total_amount = sum(detail.total_price for detail in instance.dishdetail_set.all())
    #         instance.save()
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)


# 菜品详情表视图
class DishDetailViewSet(viewsets.ModelViewSet):
    queryset = DishDetail.objects.all().order_by('id')
    serializer_class = DishDetailSerializer
    # permission_classes = [IsAuthenticated]


# 员工表视图
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('-created_at')
    serializer_class = EmployeeSerializer

    # permission_classes = [IsAuthenticated]

    # 通过发送一个POST请求到/employees/delete-multiple/来使用
    # 在请求的body中提供一个名为ids的数组，其中包含想要删除的所有员工的id
    @action(detail=False, methods=['post'], url_path='delete-multiple')
    def delete_multiple(self, request, *args, **kwargs):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'msg': '没有提供要删除的员工ID。'}, status=400)
        employees = get_list_or_404(Employee, id__in=ids)
        for employee in employees:
            employee.delete()
        return Response({'status': 'success'})
