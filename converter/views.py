from django.shortcuts import render
import os
import shutil
import tempfile
import zipfile
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from weasyprint import HTML


class ConvertToPDFView(APIView):
    def post(self, request):
        try:
            # Check if we received HTML content directly
            if "html_content" in request.data:
                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        html_path = os.path.join(temp_dir, "content.html")
                        with open(html_path, "w", encoding="utf-8") as f:
                            f.write(request.data["html_content"])

                        pdf = HTML(filename=html_path).write_pdf()
                        response = HttpResponse(pdf, content_type="application/pdf")
                        response["Content-Disposition"] = (
                            'attachment; filename="converted.pdf"'
                        )
                        return response
                except Exception as e:
                    return Response(
                        {"error": f"PDF conversion failed: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            # Check if a file was uploaded
            if "file" not in request.FILES:
                return Response(
                    {
                        "error": "No file or HTML content provided. Please upload a ZIP/HTML file or provide HTML content."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            uploaded_file = request.FILES["file"]
            file_name = uploaded_file.name

            # Handle HTML file directly
            if file_name.endswith(".html"):
                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Save the HTML file
                        file_path = os.path.join(temp_dir, file_name)
                        with open(file_path, "wb") as f:
                            for chunk in uploaded_file.chunks():
                                f.write(chunk)

                        # Convert to PDF
                        pdf = HTML(filename=file_path).write_pdf()

                        # Create response
                        response = HttpResponse(pdf, content_type="application/pdf")
                        pdf_filename = os.path.splitext(file_name)[0] + ".pdf"
                        response["Content-Disposition"] = (
                            f'attachment; filename="{pdf_filename}"'
                        )
                        return response
                except Exception as e:
                    return Response(
                        {"error": f"PDF conversion failed: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            # Handle ZIP file
            if not file_name.endswith(".zip"):
                return Response(
                    {"error": "Invalid file format. Please upload a ZIP or HTML file."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create a temporary directory for ZIP handling
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract the zip file
                zip_path = os.path.join(temp_dir, "upload.zip")
                with open(zip_path, "wb") as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)

                # Verify zip file is valid
                try:
                    with zipfile.ZipFile(zip_path, "r") as zip_ref:
                        # Extract the contents
                        extract_path = os.path.join(temp_dir, "extracted")
                        os.makedirs(extract_path, exist_ok=True)
                        zip_ref.extractall(extract_path)
                except zipfile.BadZipFile:
                    return Response(
                        {"error": "Invalid ZIP file. The file may be corrupted."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Look for HTML files
                html_files = [
                    f for f in os.listdir(extract_path) if f.endswith(".html")
                ]
                if not html_files:
                    return Response(
                        {
                            "error": "No HTML files found in the ZIP file. Found instead: "
                            + str(os.listdir(extract_path))
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Use index.html if present, otherwise use the first HTML file
                if "index.html" in html_files:
                    html_file = "index.html"
                else:
                    html_file = html_files[0]

                index_path = os.path.join(extract_path, html_file)

                try:
                    # Convert to PDF
                    pdf = HTML(filename=index_path).write_pdf()
                except Exception as e:
                    return Response(
                        {"error": f"PDF conversion failed: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                # Create response with PDF
                response = HttpResponse(pdf, content_type="application/pdf")
                filename = os.path.splitext(html_file)[0] + ".pdf"
                response["Content-Disposition"] = f'attachment; filename="{filename}"'
                return response

        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
