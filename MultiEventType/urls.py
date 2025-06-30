from rest_framework.routers import DefaultRouter

from MultiEventType.apis import MultiEventTypeViewSet

router = DefaultRouter()
router.register('multi-event-types', MultiEventTypeViewSet, basename='accounts')
urlpatterns = router.urls
