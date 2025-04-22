select * from request
where server_id = $1 and requestor_id = $2 and not filled;
