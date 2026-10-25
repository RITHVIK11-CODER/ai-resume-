import pymupdf


def extract_resume_text(file_bytes: bytes) -> str:
    """Extract selectable text from a PDF stored in memory."""
    try:
        with pymupdf.open(stream=file_bytes, filetype="pdf") as document:
            if document.is_encrypted or document.needs_pass:
                raise ValueError("Password-protected PDFs are not supported.")

            text = "\n".join(page.get_text() for page in document)

        if not text.strip():
            raise ValueError(
                "No readable text found. The PDF may be scanned or image-based."
            )

        return text[:100_000]

    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("Could not read this PDF. Please try another file.") from exc
