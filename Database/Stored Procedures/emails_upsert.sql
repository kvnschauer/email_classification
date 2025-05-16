CREATE OR REPLACE PROCEDURE email_upsert(
    emailId VARCHAR(150),
    isSpam BOOLEAN,
    senderAddress VARCHAR(150),
    senderName VARCHAR(150),
    subject_ VARCHAR(250),
    source_ VARCHAR(20),
    sizeBytes int4
    OUT upsert_email_id INTEGER
)
AS $$
BEGIN
	IF EXISTS (SELECT 1 FROM emails e WHERE emailId = e.email_id) THEN
		UPDATE emails
		SET
	        is_spam = isSpam,
	        sender_address = senderAddress,
	        sender_name = senderName,
	        subject = subject_,
			update_datetime_utc = (NOW() AT TIME ZONE 'UTC'),
			source = source_
			size_bytes = sizeBytes
		WHERE email_id = emailId
		RETURNING id INTO upsert_email_id;
	ELSE
	    INSERT INTO emails
	    (
	        email_id,
	        is_spam,
	        sender_address,
	        sender_name,
	        subject,
			create_datetime_utc,
			source,
			size_bytes
	    )
	    VALUES
	    (
	        emailId,
	        isSpam,
	        senderAddress,
	        senderName,
	        subject_,
			NOW() AT TIME ZONE 'UTC',
			source_,
			sizeBytes
	    )
    	RETURNING id INTO upsert_email_id;
	END IF;
END;
$$ LANGUAGE plpgsql;