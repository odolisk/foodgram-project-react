from rest_framework import status
from rest_framework.response import Response

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404


class CreateDeleteObjMixin:

    def create_obj(self, request, create_data):
        data = {
            'user': request.user.id,
            create_data['field_name']: create_data['id']
        }
        context = {
            'request': request,
            'exist_err_msg': create_data['err_msg']
        }
        serializer = create_data['serializer'](data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_obj(self, request, delete_data):
        subj = get_object_or_404(
            delete_data['subj_model'], id=delete_data['id'])
        obj_model = delete_data['obj_model']
        del_error_msg = delete_data['err_msg']
        del_success_msg = delete_data['success_msg']
        try:
            kwargs = {
                'user': request.user,
                delete_data['field_name']: subj}
            obj_model.objects.get(**kwargs).delete()
        except ObjectDoesNotExist:
            data = {'errors': del_error_msg}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        del_data = {'info': del_success_msg}
        return Response(data=del_data, status=status.HTTP_204_NO_CONTENT)
