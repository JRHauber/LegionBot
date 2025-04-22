select * from request
where server_id = $1 and claimant_id = $2 and not filled;
