from rest_framework import status
from rest_framework.parsers import (
    FormParser,
    MultiPartParser,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from app.serializers import ImportSerializer
from app.services.courses import CourseService
from app.services.students import StudentService
from app.utils import check_excel_format_in_request_data


class UploadCourseExcelView(APIView):
    serializer_class = ImportSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        check_excel_format_in_request_data(request)
        school = self.request.user.user_school.all().first()
        try:
            total_courses = CourseService.create_course_and_course_schedule_from_excel_by_school(
                request.data['file'], school)
            return Response({'message': f'Total cursuri create: {total_courses}'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UploadStudentsExcelView(APIView):
    serializer_class = ImportSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        check_excel_format_in_request_data(request)
        school = self.request.user.user_school.all().first()
        try:
            StudentService.create_student_from_excel_and_assign_it_to_school_course(
                request.data['file'],
                school,
            )
            return Response({'message': 'Data imported successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
