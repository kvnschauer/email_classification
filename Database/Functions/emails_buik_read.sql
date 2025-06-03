CREATE OR REPLACE FUNCTION emails_bulk_read(
    idSearchAfter INTEGER DEFAULT NULL
)
RETURNS TABLE (
    id INTEGER,
    email_id TEXT,
    is_spam BOOLEAN,
    sender_address TEXT,
    sender_name TEXT,
    subject TEXT,
    create_datetime_utc TIMESTAMP,
    source TEXT,
    size_bytes int4
)
LANGUAGE SQL
AS $$
    SELECT
        id,
        email_id,
        is_spam,
        sender_address,
        sender_name,
        subject,
        create_datetime_utc,
        source AS source,
        size_bytes
    FROM emails e
    WHERE idSearchAfter IS NULL OR e.id > idSearchAfter
    ORDER BY e.id
    LIMIT 100;
$$;