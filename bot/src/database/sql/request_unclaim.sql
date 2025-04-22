update request
set claimant_id = null
where request_id = $2 and server_id = $1 and claimant_id = $3 and not filled
returning *;
