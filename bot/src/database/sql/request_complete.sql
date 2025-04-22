update request
set filled = true
where request_id = $2 and server_id = $1 and claimant_id = $3 and not filled
returning *;
