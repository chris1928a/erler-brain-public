"""Drive search handler."""
from services.gdrive import search_drive


async def handle_drive(query: str, user_id: str) -> str:
    if not query:
        return "Usage: /drive [Suchbegriff]"
    files = await search_drive(query)
    if not files:
        return "📂 Keine Dateien gefunden."
    lines = [f"📁 *{len(files)} Ergebnisse für '{query}':*\n"]
    for f in files:
        lines.append(f"• [{f['name']}]({f['link']}) ({f['type']}, {f['modified']})")
    return "\n".join(lines)
