from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:item_id>/", views.index, name="index"),
    path("<str:sort_by>/", views.index, name="index"),
    # ex: /mainDash/detail/
    path("detail/analysis/", views.detail, name="detail"),
    # ex: /mainDash/5/industries/
    path("<int:item_id>/industries/", views.industries, name="industries"),
    # ex: /mainDash/5/edit/
    path("<int:item_id>/edit/", views.edit, name="edit"),
    path('upload-csv/suppliers/', views.upload_supplier_csv, name='upload_csv_suppliers'),
    path('upload-csv/bom/', views.upload_bom_csv, name='upload_bom_suppliers')
]

urlpatterns += staticfiles_urlpatterns()