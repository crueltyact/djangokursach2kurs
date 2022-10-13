from django.urls import path

from excel_to_doc_parser.views import index, download, login_view, logout_view, themes, documents, info

urlpatterns = [
    path('', index, name="index"),
    path('download/', download, name='download'),
    path('login/', login_view, name="login"),
    path('logout/', logout_view, name="logout"),
    path('documents/', documents, name="documents"),
    path('themes/', themes, name="themes"),
    path('about/', info, name="about"),
]

