"""DynamoDB session memory — unlimited history, searchable."""
import os
import time
import logging
import json
import boto3

logger = logging.getLogger("session")

TABLE_NAME = os.environ.get("SESSION_TABLE", "erler-brain-sessions")
HISTORY_TABLE = os.environ.get("HISTORY_TABLE", "erler-brain-history")

dynamodb = boto3.resource("dynamodb", region_name="eu-central-1")
table = dynamodb.Table(TABLE_NAME)
history_table = None

# Try to use history table, create if needed
try:
    history_table = dynamodb.Table(HISTORY_TABLE)
    history_table.load()
    logger.info("History table '%s' connected", HISTORY_TABLE)
except Exception:
    # Table doesn't exist yet — we'll create it on first use
    logger.info("History table not found, will create on first use")
    history_table = None


def _ensure_history_table():
    """Create the history table if it doesn't exist."""
    global history_table
    if history_table is not None:
        return history_table

    try:
        client = boto3.client("dynamodb", region_name="eu-central-1")
        client.create_table(
            TableName=HISTORY_TABLE,
            KeySchema=[
                {"AttributeName": "user_id", "KeyType": "HASH"},
                {"AttributeName": "ts", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "ts", "AttributeType": "N"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        # Wait for table to be active
        waiter = client.get_waiter("table_exists")
        waiter.wait(TableName=HISTORY_TABLE, WaiterConfig={"Delay": 2, "MaxAttempts": 30})
        history_table = dynamodb.Table(HISTORY_TABLE)
        logger.info("Created history table '%s'", HISTORY_TABLE)
        return history_table
    except Exception as e:
        logger.warning("Failed to create history table: %s", e)
        return None


async def load_session(user_id: str) -> dict:
    """Load session from DynamoDB."""
    try:
        resp = table.get_item(Key={"user_id": user_id})
        if "Item" in resp:
            return resp["Item"]
    except Exception as e:
        logger.warning("Session load failed: %s", e)
    return {"user_id": user_id, "messages": [], "context": {}}


async def save_session(user_id: str, session: dict):
    """Save session to DynamoDB (no TTL — persistent forever)."""
    try:
        session["user_id"] = user_id
        table.put_item(Item=session)
    except Exception as e:
        logger.warning("Session save failed: %s", e)


def add_message(session: dict, role: str, text: str):
    """Add message to session history and archive to permanent history."""
    if "messages" not in session:
        session["messages"] = []

    ts = int(time.time())
    msg_entry = {
        "role": role,
        "text": text[:2000],
        "ts": ts,
    }

    # Add to session (keep last 50 for quick access)
    session["messages"].append(msg_entry)
    session["messages"] = session["messages"][-50:]

    # Archive to permanent history table (unlimited, forever)
    try:
        ht = _ensure_history_table()
        if ht:
            ht.put_item(Item={
                "user_id": session.get("user_id", "unknown"),
                "ts": ts,
                "role": role,
                "text": text[:4000],  # Store more in archive
            })
    except Exception as e:
        logger.warning("History archive failed: %s", e)


def format_history(session: dict) -> str:
    """Format session messages for prompt context (last 20)."""
    msgs = session.get("messages", [])
    if not msgs:
        return ""
    lines = []
    for m in msgs[-20:]:
        role = "Du" if m["role"] == "user" else "Bot"
        lines.append(f"{role}: {m['text']}")
    return "\n".join(lines)


async def search_history(user_id: str, keyword: str = None, days: int = 30, limit: int = 50) -> list:
    """Search permanent conversation history.

    Args:
        user_id: User ID to search for
        keyword: Optional keyword to filter by
        days: How many days back to search (default 30)
        limit: Max results to return

    Returns:
        List of matching messages
    """
    try:
        ht = _ensure_history_table()
        if not ht:
            return []

        from boto3.dynamodb.conditions import Key
        cutoff = int(time.time()) - (days * 86400)

        resp = ht.query(
            KeyConditionExpression=Key("user_id").eq(user_id) & Key("ts").gte(cutoff),
            ScanIndexForward=False,  # Newest first
            Limit=200,
        )

        results = resp.get("Items", [])

        # Filter by keyword if provided
        if keyword:
            keyword_lower = keyword.lower()
            results = [m for m in results if keyword_lower in m.get("text", "").lower()]

        return results[:limit]

    except Exception as e:
        logger.warning("History search failed: %s", e)
        return []
