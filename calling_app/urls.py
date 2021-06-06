from django.urls import path
from .views import Register, Login, DbContacts, MarkSpam, SearchPhone, SearchName


urlpatterns = [
    path('register/', Register.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('dbcontacts/', DbContacts.as_view(), name='dbcontacts'),
    path('mark_spam/', MarkSpam.as_view(), name='mark_spam'),
    path('search_phone/', SearchPhone.as_view(), name='search_phone'),
    path('search_name/', SearchName.as_view(), name='search_name'),

]
