insert into request
(server_id, requestor_id, resource_message, filled)
values ($1, $2, $3, false)
returning request_id;
