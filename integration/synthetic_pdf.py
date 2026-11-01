"""Original Indie synthetic PDF renderer: self-contained Python stdlib only.

Generates ONLY the three fixed invented text records from indie_core.DOCS
as legible one-page text PDFs. No PyMuPDF or runtime PDF dependencies,
real-world issuer data, file uploads, or model inference.

This is a purposely small ISO 32000-style PDF writer for fixed ASCII
samples, NOT a general-purpose PDF processor or raster OCR engine.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import indie_core

PDF_TITLES={
 "invoice.txt":"TRUE LANDED / SYNTHETIC COMMERCIAL INVOICE",
 "packing.txt":"TRUE LANDED / SYNTHETIC PACKING LIST",
 "product-sheet.txt":"TRUE LANDED / SYNTHETIC PRODUCT SHEET",
}
PDF_NAMES={
 "invoice.txt":"invoice.pdf",
 "packing.txt":"packing.pdf",
 "product-sheet.txt":"product-sheet.pdf",
}
PROTOCOL_VERSION="df012-indie-private-original-pdf/1"


def _escape_ascii(value:str)->bytes:
    # Literal parentheses and backslashes in PDF string objects.
    if any(ord(c)<32 or ord(c)>126 for c in value):
        raise ValueError("NON_ASCII_SAMPLE_REFUSED")
    return value.replace("\\","\\\\").replace("(","\\(").replace(")","\\)").encode("ascii")


def make_pdf(filename:str)->bytes:
    if filename not in indie_core.DOCS:
        raise ValueError("NOT_FIXED_ORIGINAL_SYNTHETIC_DOC")
    lines=indie_core.DOCS[filename].splitlines()
    assert 3<len(lines)<14
    stream=[b"q",b"0.07 0.17 0.23 rg",b"35 740 542 35 re f",
            b"Q",b"BT",b"/F1 16 Tf",b"1 1 1 rg",b"44 751 Td",
            b"("+_escape_ascii(PDF_TITLES[filename])+b") Tj",b"ET",
            b"BT",b"/F1 12 Tf",b"0.12 0.20 0.27 rg",
            b"48 683 Td",b"23 TL"]
    for n,line in enumerate(lines):
        if n:
            stream.append(b"T*")
        stream.append(b"("+_escape_ascii(line)+b") Tj")
    stream.extend([b"ET",b"BT",b"/F1 9 Tf",b"0.35 0.41 0.47 rg",
                   b"48 65 Td",
                   b"(FICTIONAL SAMPLE - NOT A VALID TRADE DOCUMENT) Tj",
                   b"ET"])
    body=b"\n".join(stream)+b"\n"
    objs=[
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Length "+str(len(body)).encode()+b" >>\nstream\n"+body+b"endstream",
    ]
    output=bytearray(b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n")
    offsets=[0]
    for number,obj in enumerate(objs,1):
        offsets.append(len(output))
        output.extend(str(number).encode()+b" 0 obj\n"+obj+b"\nendobj\n")
    start=len(output)
    output.extend(b"xref\n0 "+str(len(objs)+1).encode()+b"\n")
    output.extend(b"0000000000 65535 f \n")
    for pos in offsets[1:]:
        output.extend(f"{pos:010d} 00000 n \n".encode())
    output.extend(
        b"trailer\n<< /Root 1 0 R /Size "+str(len(objs)+1).encode()+
        b" >>\nstartxref\n"+str(start).encode()+
        b"\n%%EOF\n")
    return bytes(output)


def all_pdfs()->dict[str,bytes]:
    return {PDF_NAMES[name]:make_pdf(name) for name in indie_core.DOCS}


def source_manifest()->dict:
    docs=all_pdfs()
    return {
       "revision":PROTOCOL_VERSION,
       "case_id":"TL-INDIE-ALPHA",
       "generator":"NEW_STDLIB_FIXED_SYNTHETIC_ASCII_RENDERER",
       "pdfs":{name:{"sha256":sha256(raw).hexdigest(),
                      "bytes":len(raw),"pages":1,
                      "input_doc":next(k for k,v in PDF_NAMES.items() if v==name)}
                for name,raw in docs.items()},
       "source_text_anchor_sha256":indie_core.evaluate()["source_anchor_sha256"],
       "all_documents_fictional":True,
       "issuer_authenticity":"NONE",
    }


def write_private(output:Path)->dict:
    # Can be called only for explicitly private local testing.
    if output.name!=".synthetic-pdf-preview":
        raise ValueError("DESTINATION_MUST_BE_PRIVATE_PREVIEW")
    output.mkdir(parents=True,exist_ok=True)
    for name,raw in all_pdfs().items():
        dest=output/name
        if dest.exists() and dest.read_bytes()!=raw:
            raise ValueError("UNEXPECTED_EXISTING_SOURCE_PDF")
        dest.write_bytes(raw)
    return source_manifest()


if __name__=="__main__":
    import json
    print(json.dumps(write_private(Path(__file__).resolve().parent/".synthetic-pdf-preview"),
                     indent=2,sort_keys=True))
