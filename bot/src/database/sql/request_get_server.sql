select * from request
where server_id = $1 and not filled;
