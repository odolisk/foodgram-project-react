from rest_framework.pagination import PageNumberPagination


class StandartPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'limit'
