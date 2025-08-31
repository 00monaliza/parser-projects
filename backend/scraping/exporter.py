import io
import pandas as pd

def export_to_xlsx_bytes(items):
    df = pd.DataFrame(items)
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    return buf
