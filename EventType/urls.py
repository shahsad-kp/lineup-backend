from rest_framework.routers import DefaultRouter

from EventType.apis import EventTypeModelViewSet

router = DefaultRouter()
router.register('event-type', EventTypeModelViewSet, basename='accounts')
urlpatterns = router.urls