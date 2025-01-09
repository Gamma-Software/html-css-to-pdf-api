from weasyprint import HTML
import os
import tempfile
import zipfile
import sys


def convert_zip_to_pdf(zip_filepath):
    try:
        # Check if file exists
        if not os.path.exists(zip_filepath):
            print("Error: File does not exist")
            return False

        # Check file extension
        if not zip_filepath.endswith(".zip"):
            print("Error: Invalid file format. Please provide a ZIP file.")
            return False

        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the zip file
            zip_path = os.path.join(temp_dir, "upload.zip")
            with open(zip_filepath, "rb") as src, open(zip_path, "wb") as dst:
                dst.write(src.read())

            # Verify zip file is valid
            try:
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    # Extract the contents
                    extract_path = os.path.join(temp_dir, "extracted")
                    os.makedirs(extract_path, exist_ok=True)
                    zip_ref.extractall(extract_path)
            except zipfile.BadZipFile:
                print("Error: Invalid ZIP file. The file may be corrupted.")
                return False

            # Look for HTML files
            html_files = [f for f in os.listdir(extract_path) if f.endswith(".html")]
            if not html_files:
                print("Error: No HTML files found in the ZIP file.")
                return False

            # Use index.html if present, otherwise use the first HTML file
            if "index.html" in html_files:
                html_file = "index.html"
            else:
                html_file = html_files[0]

            index_path = os.path.join(extract_path, html_file)

            try:
                # Convert to PDF
                print(f"Converting {html_file} to PDF...")
                pdf = HTML(filename=index_path).write_pdf()
            except Exception as e:
                print(f"Error: PDF conversion failed: {str(e)}")
                return False

            # Save PDF file
            output_filename = os.path.splitext(html_file)[0] + ".pdf"
            with open(output_filename, "wb") as f:
                f.write(pdf)
            print(f"Successfully created {output_filename}")
            return True

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test.py <zip_file>")
        sys.exit(1)

    success = convert_zip_to_pdf(sys.argv[1])
    sys.exit(0 if success else 1)
