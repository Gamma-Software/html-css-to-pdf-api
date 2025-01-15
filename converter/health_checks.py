from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable
from weasyprint import HTML
import tempfile
import os

class PDFConversionHealthCheck(BaseHealthCheckBackend):
    critical_service = True

    def check_status(self):
        try:
            # Create a simple HTML file for testing
            test_html = "<html><body><h1>Test</h1></body></html>"

            with tempfile.TemporaryDirectory() as temp_dir:
                test_file = os.path.join(temp_dir, "test.html")
                with open(test_file, "w") as f:
                    f.write(test_html)

                # Try to convert to PDF
                HTML(filename=test_file).write_pdf()

        except Exception as e:
            self.add_error(
                ServiceUnavailable("PDF conversion service is not working: %s" % str(e))
            )

    def identifier(self):
        return self.__class__.__name__