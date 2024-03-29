# Importing necessary modules and classes
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TableViewSet, DishCategoryViewSet, DishUnitViewSet, DishImageViewSet, DishViewSet, OrderViewSet, \
    DishDetailViewSet, EmployeeViewSet

# Creating a DefaultRouter to handle the viewset's URL routing
router = DefaultRouter()
router.register(r'table', TableViewSet)
router.register(r'dish-category', DishCategoryViewSet)
router.register(r'dish-unit', DishUnitViewSet)
router.register(r'dish-image', DishImageViewSet)
router.register(r'dish', DishViewSet)
router.register(r'order', OrderViewSet)
router.register(r'dish-detail', DishDetailViewSet)
router.register(r'employees', EmployeeViewSet)

# Defining the URL patterns for the app
urlpatterns = [
    # Including the URLs generated by the router
    path('', include(router.urls)),
]
