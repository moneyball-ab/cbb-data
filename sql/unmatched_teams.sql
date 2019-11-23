SELECT
    cfb_teams.team_id,
    cfb_teams.matcher,
    cbb_teams.team_abb

FROM
(
    SELECT
        *
    
    FROM
        cbb_teams

) cbb_teams
LEFT JOIN
(
    SELECT
        *,
        lower(replace(team, ' ', '-')) matcher
    
    FROM
        cfb_teams

) cfb_teams ON cfb_teams.matcher = cbb_teams.team_abb

WHERE 1=1
    AND cbb_teams.team_abb is not null