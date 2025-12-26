import traceback

try:
    import send_wave1_emails

    print("IMPORT_OK")
    print("EMAILS_TO_SEND" in dir(send_wave1_emails))
    # print first email subjects to verify
    if "EMAILS_TO_SEND" in dir(send_wave1_emails):
        for e in send_wave1_emails.EMAILS_TO_SEND:
            print("SUBJ:", e.get("subject")[:60])
except Exception:
    traceback.print_exc()
