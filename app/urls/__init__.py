from .auth import urlpatterns as urlpatterns_auth
from .automated_messages import urlpatterns as urlpatterns_automated_messages
from .calendar import urlpatterns as urlpatterns_calendar
from .courses import urlpatterns as urlpatterns_courses
from .excel import urlpatterns as urlpatterns_excel
from .school import urlpatterns as urlpatterns_school
from .sessions import urlpatterns as urlpatterns_sessions
from .students import urlpatterns as urlpatterns_students
from .trainers import urlpatterns as urlpatterns_trainers


urlpatterns = []
urlpatterns += urlpatterns_auth
urlpatterns += urlpatterns_automated_messages
urlpatterns += urlpatterns_calendar
urlpatterns += urlpatterns_courses
urlpatterns += urlpatterns_excel
urlpatterns += urlpatterns_school
urlpatterns += urlpatterns_sessions
urlpatterns += urlpatterns_students
urlpatterns += urlpatterns_trainers

