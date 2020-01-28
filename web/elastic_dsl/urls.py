from rest_framework.routers import SimpleRouter
from . import views

app_name = 'elastic_dsl' 

router = SimpleRouter()
router.register(
    prefix=r'',
    base_name='elastic_dsl',
    viewset=views.ArticleViewSet
)
urlpatterns = router.urls