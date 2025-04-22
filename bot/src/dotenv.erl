-module(dotenv).
-compile([no_auto_import, nowarn_unused_vars]).

-export([config_with/1, config/0]).

-spec config_with(binary()) -> nil.
config_with(File) ->
    _assert_subject = gleam@erlang@file:read(File),
    {ok, Env_file} = case _assert_subject of
        {ok, _} -> _assert_subject;
        _assert_fail ->
            erlang:error(#{gleam_error => let_assert,
                        message => <<"Assertion pattern match failed"/utf8>>,
                        value => _assert_fail,
                        module => <<"dotenv"/utf8>>,
                        function => <<"config_with"/utf8>>,
                        line => 37})
    end,
    _pipe = gleam@string:split(Env_file, <<"\n"/utf8>>),
    _pipe@1 = gleam@list:filter(_pipe, fun(Line) -> Line /= <<""/utf8>> end),
    gleam@list:each(
        _pipe@1,
        fun(Line@1) -> case gleam@string:split(Line@1, <<"="/utf8>>) of
                [Key, Value] ->
                    Key@1 = gleam@string:trim(Key),
                    Value@1 = gleam@string:trim(Value),
                    gleam_erlang_ffi:set_env(Key@1, Value@1);

                _ ->
                    gleam@io:println(<<"Invalid line in .env file:"/utf8>>),
                    gleam@io:println(Line@1)
            end end
    ).

-spec config() -> nil.
config() ->
    config_with(<<".env"/utf8>>).
