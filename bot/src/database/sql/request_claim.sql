update request
set claimant_id = $3
where request_id = $2 and server_id = $1 and claimant_id is null and not filled
returning *;
