#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author:  HUHU
# @File:    init_data.py
# @Time:    2024/01/18
"""
生成数据库基础数据
"""
# init_data.py
import os
import random
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')  # 替换为你的settings.py所在的模块
django.setup()

from restaurant_app.models import Table, DishCategory, DishUnit, DishImage, Dish, Order, DishDetail, \
    Employee  # 替换为你的模型所在的模块


def create_data():
    for i in range(1, 11):
        Table.objects.get_or_create(table_number=i)
    print("Table data created.")

    for i in range(1, 5):
        DishCategory.objects.get_or_create(category=f'类别{i}')
    print("DishCategory data created.")

    DishUnit.objects.get_or_create(unit='份')
    print("DishUnit data created.")

    for filename in os.listdir('../media/images'):  # 注意这里的路径已经修改
        if filename.endswith('.jpg'):
            DishImage.objects.get_or_create(file=f'images/{filename}', name=filename[:-4])
    print("DishImage data created.")

    for dish_image in DishImage.objects.all():
        if not Dish.objects.filter(name=dish_image.name).exists():
            Dish.objects.get_or_create(category=DishCategory.objects.order_by('?').first(), specification=f'精品',
                                       file=dish_image, name=dish_image.name,
                                       unit=DishUnit.objects.order_by('?').first(),
                                       price=random.randint(10, 200), is_on_sale=True)
    print("Dish data created.")

    for i in range(random.randint(20, 101)):
        order = Order.objects.create(table=Table.objects.order_by('?').first(), number_of_people=random.randint(1, 10),
                                     total_amount=random.randint(10, 2000), transaction_status='未结账')
        for j in range(random.randint(1, 31)):
            dish = Dish.objects.order_by('?').first()
            if dish is not None:  # 检查是否有Dish对象
                quantity = random.randint(1, 2)
                DishDetail.objects.create(dish=dish, order=order, quantity=quantity, total_price=dish.price * quantity)
    print("Order and DishDetail data created.")

    for i in range(80):
        if not Employee.objects.filter(employee_number=f'{i}').exists():
            Employee.objects.get_or_create(employee_number=f'{i}', name=f'员工{i}', gender=random.choice(['男', '女']),
                                           position='服务员')
    print("Employee data created.")


if __name__ == '__main__':
    create_data()
