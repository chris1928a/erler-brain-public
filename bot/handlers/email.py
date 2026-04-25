"""Email handler — search, read, draft."""
import logging
from services.gmail import search_emails, read_email, draft_and_send
from services.gemini import call_gemini_direct

logger = logging.getLogger("handler.email")


async def handle_email(args: str, user_id: str) -> str:
    """Handle email commands."""
    args = args.strip()

    if args.startswith("read "):
        msg_id = args[5:].strip()
        email = await read_email(msg_id)
        return f"📧 *{email['subject']}*\nVon: {email['from']}\nDatum: {email['date']}\n\n{email['body'][:2000]}"

    elif args.startswith("draft "):
        # Parse: draft [to] [subject] | [body]
        parts = args[6:].split("|", 1)
        if len(parts) < 2:
            return "Usage: /email draft [to] [subject] | [body]"
        header = parts[0].strip().split(" ", 1)
        to = header[0]
        subject = header[1] if len(header) > 1 else "Kein Betreff"
        body = parts[1].strip()
        return await draft_and_send(to, subject, body)

    else:
        # Search
        query = args if args else "is:unread"
        emails = await search_emails(query, max_results=10)
        if not emails:
            return "📭 Keine Emails gefunden."

        lines = [f"📧 *{len(emails)} Emails* ({query}):\n"]
        for e in emails:
            lines.append(f"• `{e['id'][:8]}` *{e['subject'][:50]}*\n  Von: {e['from'][:40]} | {e['date'][:16]}")
        lines.append(f"\n💡 /email read [ID] zum Lesen")
        return "\n".join(lines)
