from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .utils import run_prediction
from .loader import stage1_model, stage2_model, stage3_model


class PredictStage1View(APIView):
    def post(self, request):
        try:
            result = run_prediction(stage1_model)
            return Response(result, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)


class PredictStage2View(APIView):
    def post(self, request):
        try:
            result = run_prediction(stage2_model)
            return Response(result, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)


class PredictStage3View(APIView):
    def post(self, request):
        try:
            result = run_prediction(stage3_model)
            return Response(result, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)

