from django.shortcuts import render
import os
import shutil
import tempfile
import zipfile
import base64
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from weasyprint import HTML
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from html2image import Html2Image

# Get Chrome flags from environment or use defaults
CHROME_FLAGS = os.getenv('CHROME_FLAGS', '--no-sandbox --headless --disable-gpu --disable-dev-shm-usage')

# Set Chrome options
os.environ['CHROMIUM_FLAGS'] = CHROME_FLAGS

# Set Chrome path
os.environ['CHROME_BIN'] = '/usr/bin/chromium-browser'  # or '/usr/bin/chromium-browser' depending on your system

@method_decorator(csrf_exempt, name="dispatch")
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

                        pdf = HTML(filename=html_path, encoding="utf-8").write_pdf()
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
                        pdf = HTML(filename=file_path, encoding="utf-8").write_pdf()

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
                    pdf = HTML(filename=index_path, encoding="utf-8").write_pdf()
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


@api_view(["POST"])
def convert_svg_to_png(request):
    try:
        # Check if we received SVG content directly
        if "svg_content" in request.data:
            svg_data = request.data["svg_content"]
        # Check if a file was uploaded
        elif "file" in request.FILES:
            svg_file = request.FILES["file"]
            svg_data = svg_file.read().decode("utf-8")
        else:
            return Response(
                {"error": "No SVG content or file provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temporary directory for html2image to work correctly
            os.chdir(temp_dir)
            svg_path = os.path.join(temp_dir, "input.svg")
            png_path = "output.png"

            with open(svg_path, "w", encoding="utf-8") as f:
                f.write(svg_data)

            # Initialize html2image with custom settings
            hti = Html2Image()

            # Convert SVG to PNG
            hti.screenshot(other_file=str(svg_path), save_as=str(png_path))

            # Read the PNG and convert to base64
            with open("/app/" + png_path, "rb") as f:
                png_data = f.read()
                base64_png = base64.b64encode(png_data).decode("utf-8")

            # Remove the temporary directory
            shutil.rmtree(temp_dir)
            os.remove("/app/" + png_path)

            # Create response with PNG
            response = HttpResponse(base64.b64decode(base64_png), content_type="image/png")
            response["Content-Disposition"] = f'attachment; filename="converted.png"'
            return response

    except Exception as e:
        # Remove the temporary directory
        shutil.rmtree(temp_dir)
        return Response(
            {"error": f"Failed to convert SVG to PNG: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
