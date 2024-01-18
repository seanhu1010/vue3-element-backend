# 1.依赖
python 3.11

```shell
pip install -r requirements.txt
```

# 2.运行项目
将backend文件夹标记为**Sources Root**

创建数据库和用户
```shell
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

在`media/images`文件夹下放入一些菜品的图片，格式限定为jpg，文件名为菜品名，如`糖醋里脊.jpg`

为餐厅app添加一些数据
```shell
cd restaurant_app
python init_data.py
```

运行
```shell
cd ..
python manage.py runserver 0.0.0.0:8000
```

接口列表

| 接口名           | url                                                                                      | 说明                               |
|---------------|------------------------------------------------------------------------------------------|----------------------------------|
| user          | http://localhost:8000/api/user/                                                          |                                  |
| table         | http://localhost:8000/api/table/                                                         |                                  |
| dish-category | http://localhost:8000/api/dish-category/                                                 |                                  |
| dish-unit     | http://localhost:8000/api/dish-unit/                                                     |                                  |
| dish-image    | http://localhost:8000/api/dish-image/                                                    |                                  |
| dish          | http://localhost:8000/api/dish/                                                          |                                  |
| order         | http://localhost:8000/api/order/                                                         |                                  |
| 订单过滤          | http://localhost:8000/api/order?start_time=2024-01-01&end_time=2024-12-31&table_number=1 | 时间段和桌号可以分开或一起传                   |
| dish-detail   | http://localhost:8000/api/dish-detail/                                                   |                                  |
| employees     | http://localhost:8000/api/employees/                                                     |                                  |
| 批量删除employees | http://localhost:8000/api/employees/delete-multiple/                                     | post,传入ids=[id,id,...]           |
| 菜品分类销售趋势      | http://localhost:8000/api/dish-category/sales-rank/?period=month                         | period可选['week', 'month']        |
| 菜品销量排行榜       | http://localhost:8000/api/dish/sales-rank/?period=day                                    | period可选['day', 'week', 'month'] |
| 订单销售总价区间统计    | http://localhost:8000/api/order/total-amount-statistics/?period=week                     | period可选['day', 'week', 'month'] |