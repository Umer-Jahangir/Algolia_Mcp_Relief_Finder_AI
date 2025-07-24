from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.mcp_service import generateResult
import asyncio

class AIChatView(APIView):
    def post(self, request):
        message = request.data.get("message", "")
        if not message:
            return Response({"error": "No message provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            answer = asyncio.run(generateResult(message))
            return Response({"response": answer})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
