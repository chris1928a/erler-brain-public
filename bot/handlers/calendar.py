"""Calendar handler."""
from services.gcal import get_events


async def handle_calendar(args: str, user_id: str) -> str:
    day = "tomorrow" if "morgen" in args.lower() or "tomorrow" in args.lower() else "today"
    events = await get_events(day)
    if not events:
        return f"📅 Keine Termine {'morgen' if day == 'tomorrow' else 'heute'}."

    label = "Morgen" if day == "tomorrow" else "Heute"
    lines = [f"📅 *{label}: {len(events)} Termine*\n"]
    for e in events:
        start = e["start"]
        if "T" in start:
            time_str = start.split("T")[1][:5]
        else:
            time_str = "Ganztägig"
        loc = f" 📍 {e['location']}" if e.get("location") else ""
        att = f" 👥 {e['attendees']}" if e.get("attendees") else ""
        lines.append(f"• *{time_str}* — {e['title']}{loc}{att}")
    return "\n".join(lines)
